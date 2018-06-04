#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

from pymystem3 import Mystem
import wikipedia
import Stemmer
from math import log
from bs4 import BeautifulSoup
import requests
import networkx as nx

wikipedia.set_lang('ru')

# Получение ссылок на статью Википедии по её названию
def get_backlinks(title):
	url='https://ru.wikipedia.org/w/api.php?action=query&format=xml&list=backlinks&bltitle='+title+'&bllimit=1000'
	x=requests.get(url)
	soup=BeautifulSoup(x.text,'lxml')
	blinks=[]
	bl=soup.find('bl')
	blinks.append(bl.get('title'))
	while True:
		bl=bl.findNext('bl')
		if bl==None:
			break
		if bl.get('ns')=='0':
			blinks.append(bl.get('title'))
	return blinks  
# Составление взвешенного неориентированного графа по фразам
def graf(phrases):
	L=len(phrases)
	W=1474081 
	k_blinks=[]
	blinks=[]
	for i in range(L):
		blinks.append(get_backlinks(phrases[i]))
		k_blinks.append(len(blinks[i]))
	ind=[]
	G=nx.Graph()
	i=0;j=0; 
	while i<L-1:
		j=i+1;
		while j<L:
			if k_blinks[i]<k_blinks[j]:
				Imax=k_blinks[j]
				Imin=k_blinks[i]
			else:
				Imax=k_blinks[i]
				Imin=k_blinks[j]
			per=0
			for k in range(k_blinks[i]):
				for l in range(k_blinks[j]):
					if blinks[i][k]==blinks[j][l]:
						per+=1
			if per!=0:
				G.add_edge(phrases[i],phrases[j],weight=(log(Imax)-log(per))/(log(W)-log(Imin)))
			else:
				ind.append(i)
			j+=1
		i+=1
	print('sem:')
	print(phrases)
	rank_v=nx.pagerank(G)
	print(rank_v)
	return(rank_v) 
  
# Получить текст из коллекции
def get_text(name_txt='collect2.txt',name_teg='text'):
	res=[]
	reading=False
	f=open(name_txt)
	for line in f:
		if line=='</'+name_teg+'>\n':
			reading=False
		elif reading:
				res.append(line)
		elif line=='<'+name_teg+'>\n':
				reading=True
	f.close()
	return res # Получить текст из коллекции

def get_pos(a):
	if a.find(',')!=-1:
		if a.find(',')<a.find('='):
			return a[0:a.find(',')]			
		else:
			return a[0:a.find('=')]			
	else:
		return a[0:a.find('=')]
    
#Получить файл, содержащий список частеречевых последовательностей по релевантным фразам
def get_patterns():
	with open('expert_phrases.txt') as f:
		t=f.read()
	my=Mystem()
	analyz=my.analyze(t)
	fras=[]
	word=[]
	k=0
	l=0
	for i in range(0,len(analyz),2):
		if analyz[i].get('analysis',1) == 1:
			if analyz[i+1].get('text').find('\n')!=-1:
				fras.append(' '.join(word[k-l:k]))
				l=0
			continue
		if analyz[i].get('analysis')!=[]:  
			a=analyz[i].get('analysis')[0].get('gr')
			if a.find(',')!=-1:
				if a.find(',')<a.find('='):
					word.append(a[0:a.find(',')])
					k+=1
					l+=1
				else:
					word.append(a[0:a.find('=')])
					k+=1
					l+=1
			else:
				word.append(a[0:a.find('=')])
				k+=1
				l+=1
		if analyz[i+1].get('text').find('\n')!=-1:
			fras.append(' '.join(word[k-l:k]))
			l=0
	f=open('phrases_morphologe.txt','w')
	for i in range(len(fras)):
		f.write(fras[i]+'\n')
	f.close()
	print('phrases_morphologe.txt are written')
	fras.sort()
	k=1
	paterns=[]
	kol=[]
	for i in range(len(fras)-1):
		if fras[i]==fras[i+1]:
			k+=1
		else:
			paterns.append(fras[i])
			kol.append(k)
			k=1
	
	i=0
	while i<len(paterns):
		if kol[i]==1:
			paterns.pop(i)
			kol.pop(i)
		else:
			i+=1
	return paterns,kol 
  
# Получить частеречевые шаблоны
def patterns_from_txt(name_txt='phrases_morphologe.txt'):
	ans=[]
	f=open(name_txt)
	for line in f:
		ans.append(line)
	f.close()
	ans.sort()
	k=1
	fras=[]
	kol=[]
	for i in range(len(ans)-1):
		if ans[i]==ans[i+1]:
			k+=1
		else:
			fras.append(ans[i])
			kol.append(k)
			k=1
	i=0
	while i<len(fras):
		if fras[i].find(' ')==-1:
			fras.pop(i)
			kol.pop(i)
		elif kol[i]==1: 
			fras.pop(i)
			kol.pop(i)
		else:
			i+=1
	return fras,kol 
  
#Получить список кандидатов в ключевые фразы
def get_candidats(text): 
	my=Mystem()
	analyz=my.analyze(text)
	word=[]
	t=[]
	lem=[]
	for i in range(0,len(analyz),2):	
		if analyz[i].get('analysis',1) == 1:
			if i==len(analyz)-1:
				break
			if analyz[i+1].get('analysis',1) == 1:
				continue
			if analyz[i+1].get('analysis')!=[]:
				word.append(get_pos(analyz[i+1].get('analysis')[0].get('gr')))
				t.append(analyz[i+1].get('text'))
				lem.append(analyz[i+1].get('analysis')[0].get('lex'))	
			continue	
		if analyz[i].get('analysis')!=[]:
			word.append(get_pos(analyz[i].get('analysis')[0].get('gr')))
			t.append(analyz[i].get('text'))
			lem.append(analyz[i].get('analysis')[0].get('lex'))
	z=[]
	fras,kol=patterns_from_txt()
	#fras,kol=get_patterns()  
	for i in range(len(fras)):
		p=fras[i].split(' ')
		p[len(p)-1]=p[len(p)-1][0:p[len(p)-1].find('\n')] ##
		z.append([])
		for j in range(len(word)-len(p))   :
			if word[j]==p[0]:
				fl=1
				for l in range(1,len(p)):
					if word[j+l]==p[l]:
						fl+=1
					else:
						break
				if fl==len(p):
					st=''
					for m in range(fl): 
						st+=t[j+m]+' ' # фразы в том виде в котором в тексте
						# st+=lem[j+m]+' ' #лемматизированные фразы
					z[i].append(st.rstrip())
	#получили z - список, состоящий из списков выделенных кандидатов по каждому паттерну
	return z  
  
# Получить название статьи Википедии по фразам кандидатам
def get_title(t):
	stemmer=Stemmer.Stemmer('russian')
	first_candidats=[]
	phrases=[]
	for frases in t:
		f=wikipedia.search(frases)
		if f==[]:
			break	
		word_frases=frases.split(' ')
		word_query=f[0].split(' ')
		k=0
		for word in word_frases:
			for w in word_query:
				if stemmer.stemWord(word).lower()==stemmer.stemWord(w.replace(',','')).lower():
					k+=1
		if k!=0:
			if k==len(word_frases) and (len(word_query)-len(word_frases)<2) or k==len(word_query) and (len(word_frases)-len(word_query)<2) :
				first_candidats.append(f[0])
				phrases.append(frases)
	return first_candidats,phrases 
  
# выделить только уникальные статьи
def get_unikl(phrases,aticls):
	f=aticls
	qt=0
	extract_phrases=[]
	i=0
	while True:
		p=[]
		qt=1
		p.append(phrases[i])
		j=i+1
		while j<len(f):
			if f[i]==f[j]:
				qt+=1
				p.append(phrases[j])
				f.pop(j)
				phrases.pop(j)
			else:
				j+=1
		extract_phrases.append([f[i],p,qt,len(f[i].split(' '))])
		if i==len(f)-1:
			break
		else:
			i+=1
	return(extract_phrases) 

def main():
	texts=get_text()
	f=[]
	phras=[]
	k=0
	ttx=texts[1]
	candidats=get_candidats(ttx)
	print(candidats)
	for i in range(len(candidats)):
		f1,phras1=get_title(candidats[i])
		k+=len(candidats[i])
		f+=f1
		phras+=phras1
	print(k)
	print('kolvo statey:',len(f))
	print(phras)
	print(f)
	extract_phrases=get_unikl(phras,f)
	phras=[];kol=[]
	for i in range(len(extract_phrases)):
		phras.append(extract_phrases[i][0])
		kol.append(extract_phrases[i][2])
	print(len(extract_phrases))
	print(extract_phrases)
	gr=graf(phras)
	print(gr)

if __name__=="__main__":
	main()
