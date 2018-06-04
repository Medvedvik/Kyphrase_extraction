import urllib.request
from bs4 import BeautifulSoup, Comment
import re

fontanka='http://www.fontanka.ru'
lenta='https://lenta.ru'
#/rubrics/sport/2017/
regexp=r'^a'


def get_html(url):
	res=urllib.request.urlopen(url)
	return res.read()

def get_a(div):
	a=div.find('a')
	h=a.get('href')
	return h

def find_a(html,txt):
	n=0
	soup=BeautifulSoup(html,'lxml')
	div1=soup.find(class_='b-layout')
	div2=div1.find('div',class_='span4')
	if (div2==None):
		return n
	div3=div2.find('div',class_='item news b-tabloid__topic_news')
	if (div3==None):
		return n
	div4=div3.find('div',class_='titles')
	n=n+parse(get_html(lenta+get_a(div4)),txt,get_a(div4))
	while (True):
		
		div4=div4.findNext('div',class_='titles')
		if(div4==None):
			break
		else:
			#print(get_a(div4))
			n=n+parse(get_html(lenta+get_a(div4)),txt,get_a(div4))
	return n



def parse(html,txt,a):
	soup=BeautifulSoup(html,'lxml')
	div=soup.find('div',class_='span8')
	if (div==None):
		return 0
	if (div.find('h1',class_='b-topic__title')==None):
		return 0
	title=div.find('h1',class_='b-topic__title').next
	print(str(title))
	date=div.find('time',class_='g-date').next
	text=div.find('div',class_='b-text clearfix js-topic__text')
	comments = text.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]
	deltext=text.find('div')
	if (deltext!=None):
		[text.extract() for text in deltext]
	text2=text.find_all(text=True)
	txt.write('<title>\n')
	txt.write(str(title))
	txt.write('\n</title>')
	txt.write('\n<text>\n')
	for i in range(len(text2)):
		text2[i]=re.sub(r"[\n\u0142\u017c\xfa\u200b]","",text2[i])
		txt.write(str(text2[i]))
	txt.write('\n</text>')
	txt.write('\n<date>\n')
	txt.write(str(date))
	txt.write('\n</date>')
	txt.write('\n<url>\n')
	txt.write(lenta+a)
	txt.write('\n</url>\n')
	return 1
	
def main():
	n=200
	year=2017
	month=5
	day=12
	economics=open('economics.txt','w')
	while(n>0):
		if (month<10):
			if (day<10):
				n=n-find_a(get_html(lenta+'/rubrics/economics/'+str(year)+'/0'+str(month)+'/0'+str(day)+'/'),economics)
			else: 
				n=n-find_a(get_html(lenta+'/rubrics/economics/'+str(year)+'/0'+str(month)+'/'+str(day)+'/'),economics)
		else:
			if (day<10):
				n=n-find_a(get_html(lenta+'/rubrics/economics/'+str(year)+'/'+str(month)+'/0'+str(day)+'/'),economics)
			else: 
				n=n-find_a(get_html(lenta+'/rubrics/economics/'+str(year)+'/'+str(month)+'/'+str(day)+'/'),economics)
		if (day>1):
			day-=1
		else:
			if (month==3):
				month-=1 
				day=28
			else:
				if (month>1):
					month-=1
					day=30
				else:
					year-=1
					month=12
					day=31
	economics.close()
	

if __name__=='__main__':
	main()
