import urllib.request
import bs4 as bs

class Data:
    def __init__(self,DOI,Title,Abstract,Tags,Authors):
        self.Cite=""
        self.Title=""
        self.Abstract=""
        self.Tags=list()
        self.Authors=list()


def PubMed(searchterm):
    Results=list()
    url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="+searchterm+"&retmax=30"
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')
    #print(soup)
    ids=[]
    for ID in soup.find_all('id'):
        ids.append(ID.string)
        Results.append(Data('','','',[],[]))

    articles=",".join(ids)
    source=urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="+articles+"&retmode=xml&rettype=abstract").read()
    soup = bs.BeautifulSoup(source,'lxml') 
    #print(soup)
    for div in soup.find_all("affiliationinfo"):#cleans out non-useful data
        div.decompose()
    i=0
    for Article in soup.findAll('pubmedarticle'):
        Journal=Article.findNext('journal')
        Results[i].Title=Article.findNext('articletitle').text
        try:
            Results[i].Abstract= Article.find('abstract').text
        except:
            Results[i].Abstract="Abstract not found"
        Al=Article.findNext('authorlist')
        total=0
        for child in Al.findChildren('author'):
            if(child.lastname):
                Results[i].Authors.append(child.lastname.text)
            else:
                Results[i].Authors.append(child.collectivename.text)
            total=total+1
        #citation starts here
            citeTemp=[]
        if(total>=6):
            citeTemp.append(Results[i].Authors[0]+", et al.")
        elif(total==5):
            citeTemp.append(Results[i].Authors[0]+", "+Results[i].Authors[1]+", "+Results[i].Authors[2]+", "+Results[i].Authors[3]+", and "+Results[i].Authors[4]+". (")
        elif(total==4):
            citeTemp.append(Results[i].Authors[0]+", "+Results[i].Authors[1]+", "+Results[i].Authors[2]+", and "+Results[i].Authors[3]+". (")
        elif(total==3):
            citeTemp.append(Results[i].Authors[0]+", "+Results[i].Authors[1]+", and "+Results[i].Authors[2]+". (")
        elif(total==2):
            citeTemp.append(Results[i].Authors[0]+" and "+Results[i].Authors[1]+". (")
        elif(total==1):
            citeTemp.append(Results[i].Authors[0]+". (")

        Pub=Article.findNext('articledate')
        #print(Article)
        if(Journal.journalissue.volume):
            try:
                citeTemp.append(Journal.journalissue.pubdate.year.text+"). "+Results[i].Title+". "+Journal.title.text+" "+Journal.journalissue.volume.text+", ")
            except:
                
                citeTemp.append(Journal.journalissue.pubdate.medlinedate.text+"). "+Results[i].Title+". "+Journal.title.text+", ")
        else:
            citeTemp.append(Journal.journalissue.pubdate.year.text+"). "+Results[i].Title+". "+Journal.title.text+", ")
        temp=Article.articleidlist.find('articleid', idtype='doi')
        if(temp):
            citeTemp.append(temp.text)
        else:
            citeTemp.append("https://www.ncbi.nlm.nih.gov/pubmed/"+Article.articleidlist.find('articleid', idtype='pubmed').text)
        Results[i].Cite="".join(citeTemp)
        #citation ends here
        i=i+1
    return Results
