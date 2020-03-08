import urllib.request
import bs4 as bs

class Data:
    def __init__(self,DOI,Title,Abstract,Tags,Authors):
        self.Cite=""
        self.Title=""
        self.Abstract=""
        self.Tags=list()
        self.Authors=list()


def medarch(searchterm):
    Results=list()
    url="https://www.medrxiv.org/search/"+searchterm+"%20numresults%3A30%20sort%3Arelevance-rank"
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')
    UL= soup.find('ul', attrs={'class':"highwire-search-results-list"})#list of results
    links=list()
    for LI in UL.findChildren('li'):
        links.append(LI.div.div.span.a['href'])
    for end in links:
        URL='https://www.medrxiv.org'+end
        SOURCE = urllib.request.urlopen(URL).read()
        SOUP = bs.BeautifulSoup(SOURCE,'lxml')
        data= SOUP.find('div', attrs={'class':"inside"})
        datacite=data.find('div',attrs={'class':"panel-pane pane-highwire-article-citation"}).div.div.find('div',attrs={'class':"highwire-cite highwire-cite-highwire-article highwire-citation-medrxiv-article-top clearfix has-author-tooltip"})
        title= datacite.h1.text
        al=datacite.find('div',attrs={'class':'highwire-cite-authors'}).span
        Authors=[]
        for a in al.children:
            if(a==', '):
                continue
            else:
                Authors.append(a.text)
        doi=datacite.select_one('div[class=highwire-cite-metadata] > span').text[21:-1]
        abstract= data.find('h2').findParent().text[8:]
        citeTemp=[]
        total=len(Authors)
        if(total>=6):
            citeTemp.append(Authors[0]+", et al.")
        elif(total==5):
            citeTemp.append(Authors[0]+", "+Authors[1]+", "+Authors[2]+", "+Authors[3]+", and "+Authors[4]+". (")
        elif(total==4):
            citeTemp.append(Authors[0]+", "+Authors[1]+", "+Authors[2]+", and "+Authors[3]+". (")
        elif(total==3):
            citeTemp.append(Authors[0]+", "+Authors[1]+", and "+Authors[2]+". (")
        elif(total==2):
            citeTemp.append(Authors[0]+" and "+Authors[1]+". (")
        elif(total==1):
            citeTemp.append(Authors[0]+". (")
        citeTemp.append(SOUP.find('div',attrs={'class':'pane-1'}).text[13:-4])
        citeTemp.append(title+". ")
        citeTemp.append(URL)
        D=Data("","","",[],[])
        D.Cite="".join(citeTemp)
        D.Title=title
        D.Abstract=abstract
        D.Authors=Authors
        Results.append(D)
    return Results
