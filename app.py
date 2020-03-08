import os
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
#import sys
#sys.path.append('/home/ubuntu/Public')
import pubmedscraper_multithread
import BiorxivScraper
import MedrxivScraper
import threading
from multiprocessing import Pipe


f = open("Homo_sapiens.gene_info", "r")
rows=f.read().split("\n")
column=list()
print(rows.pop())
for row in rows:
    try:
        column.append(row.split("\t")[2])
        if not '-'==row.split("\t")[11]:
            column.append(row.split("\t")[11])
    except:
        pass
list_tags=column

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
#print(app.config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#from models import Result
###########class########
class Data:
    def __init__(self,DOI,Title,Abstract,Tags,Author):
        self.Cite=""
        self.Title=""
        self.Abstract=""
        self.Tags=list()
        self.Authors=list()
###########class########
###########test_data#########
results_fake=list()
results_fake.append(Data('','','',[],[]))
results_fake[0].Cite="this is a citation"
results_fake[0].Title="this is a title"
results_fake[0].Abstract="this is a abstract"
results_fake[0].Tags=['tag1','tag2','tag3','tag4']
results_fake[0].Authors=['Bob','Jill']

results_fake.append(Data('','','',[],[]))
results_fake[1].Cite="1this is a citation"
results_fake[1].Title="1this is a title"
results_fake[1].Abstract="1this is a abstract"
results_fake[1].Tags=['1tag1','1tag2','1tag3','1tag4']
results_fake[1].Authors=['1Bob','1Jill']
###########test_date#########

def bioarch_thread(child_conn,query):
    try:
        results1=BiorxivScraper.bioarch(str(query).replace(' ','+'))
        child_conn.send(results1)
    except:
        results1=None

def medarch_thread(child_conn,query):
    try:
        results2=MedrxivScraper.medarch(str(query).replace(' ','+'))
        child_conn.send(results2)
    except:
        results2=None

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = []
    results1 = []
    results2 = []
    if request.method == "POST":
        # get url that the user has entered
        try:
            query = request.form['url']
            query_tags = request.form['tag'].strip().split(',')
            if query_tags[0]=='':
                query_tags=['Pubmed','MedArchive','PubArchive']
            #print(url)
            #r = requests.get(str(url))
            #print(r.text[:100])
            try:
                print(str(query).replace(' ','+'))
                
                temp, temp2 = Pipe()
                parent_conn1=temp
                child_conn1=temp2

                temp, temp2 = Pipe()
                parent_conn2=temp
                child_conn2=temp2

                d1=threading.Thread(name='daemon', target=bioarch_thread, args=(child_conn1,query))
                d1.setDaemon(True)
                d1.start()
                
                d2=threading.Thread(name='daemon', target=medarch_thread, args=(child_conn2,query))
                d2.setDaemon(True)
                d2.start()
                try:
                    results=pubmedscraper_multithread.PubMed(str(query).replace(' ','+'))
                except:
                    print("pubmed crashed")
                try:
                    results1=parent_conn1.recv()
                    parent_conn1.close()
                    d1.join()
                except:
                   print("PubArchive crashed")
                try:
                    results2=parent_conn2.recv()
                    parent_conn2.close()
                    d2.join()
                except:
                    print("MedArchive crashed")

            except Exception as e:
                print("call failed"+str(e))
                results=None
            
            if results==None:
                results=results_fake

            ####finding tags###
            for result_i in range(len(results)):
                for tag in list_tags:
                    if tag in results[result_i].Abstract:
                        results[result_i].Tags.append(tag)
                results[result_i].Tags.append('PubMed')
            for result_i in range(len(results1)):
                for tag in list_tags:
                    if tag in results1[result_i].Abstract:
                        results1[result_i].Tags.append(tag)
                results1[result_i].Tags.append('BioArchive')
            for result_i in range(len(results2)):
                for tag in list_tags:
                    if tag in results2[result_i].Abstract:
                        results2[result_i].Tags.append(tag)
                results2[result_i].Tags.append('MedArchive')

##############################################################
###########are tags present############
            print('string of tags: '+str(query_tags))
            found=0
            for result_i in range(len(results)):
                for tag in query_tags:
                    if tag in results[result_i].Tags:
                        found=1
                if found==0:
                    results[result_i]=None
                found=0
            results=[i for i in results if i] #removes None

            found=0
            for result_i in range(len(results1)):
                for tag in query_tags:
                    if tag in results1[result_i].Tags:
                        found=1
                if found==0:
                    results1[result_i]=None
                found=0
            results1=[i for i in results1 if i] #removes None
            found=0

            for result_i in range(len(results2)):
                for tag in query_tags:
                    if tag in results2[result_i].Tags:
                        found=1
                if found==0:
                    results2[result_i]=None
                found=0
            results2=[i for i in results2 if i] #removes None

        except Exception as e:
            print(e)
            errors.append(
                "Unable to get URL. Please try again."
            )
    return render_template('index.html', errors=errors, results=results, results1=results1, results2=results2)


if __name__ == '__main__':
    app.run()
