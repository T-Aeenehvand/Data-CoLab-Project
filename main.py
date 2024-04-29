import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.request import urlopen
import re
import ssl
from PIL import Image
import nltk           
from nltk.corpus import stopwords                       
from nltk.tokenize import word_tokenize, sent_tokenize 
#import text_to_image as tti
#import texttoimage
import heapq
import string
import seaborn as sns


#Define some variables
freqTable = dict()
sentenceValue = dict()
rawsums = list()
rawheaders = list()
consum = list()
sumValues = 0
summary = '' 
title, author, pub_date , genre = 'N/A', 'N/A', 'N/A', 'N/A'
bigsize = 80
smallsize = 20

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS Data
    (id INTEGER PRIMARY KEY, title TEXT, author TEXT,
     pub_date INTEGER, genre TEXT , sums TEXT, condencedSum TEXT)''')


# Load the dataset
#url = input('Enter web url or enter: ')
#data = urlopen(url, context=ctx)
#fhandle = open('booksummaries.txt', encoding="utf-8")
fhandle = open('shorties.txt')
data = fhandle.read()
lines = data.splitlines()
#data.dropna(inplace=True)


#extracting summeries and storing headers too
for line in lines:
    header = re.findall('^[0-9].+}', line)
    
    try:
        first_part = [i for i in re.split('(\t)', header[0]) if i[0].isupper()]
        title = first_part[0]
        author = first_part[1]
    except:
        print("There is something wrong with the title.")
    
    try:
        second_part = re.findall('{(.+?)}', header[0])
        genre = [i for i in re.split(':', second_part[0]) if i[2].isupper()][-1].strip('" "')
    except:
        print("There is something wrong with the genre.")
        
    try:
        pub_date = [i for i in re.findall(r'\d{4}-\d{2}-\d{2}', header[0]) if i][0]
    except:
        print("There is something wrong with the date.")
    rawheaders.append(header)
    sumstory = re.split('^[0-9].+}', line)

    try:
        for story in sumstory: 
            #print(story)
            if story :
                #rawsums.append(story)                
                #Counting and documenting every word in the summaries
                stopWords = set(stopwords.words("english")) 
                #print(story)
                words = word_tokenize(story.translate(str.maketrans('', '', string.punctuation)))
                for word in words:               
                    word = word.lower()                 
                    if word in stopWords:                 
                        continue                  
                    if word in freqTable:                       
                        freqTable[word] += 1            
                    else:          
                        freqTable[word] = 1
                #print(freqTable)
                
                
                
                
                #Counting and documenting every sentence in the summaries
                sentences = sent_tokenize(story) 
                for sentence in sentences:
                    for word, freq in freqTable.items():              
                        if word in sentence.lower():                              
                            if sentence in sentenceValue:                                 
                                sentenceValue[sentence] += freq                       
                            else:                       
                                sentenceValue[sentence] = freq                    
                            
                for sentence in sentenceValue:              
                    sumValues += sentenceValue[sentence]
                #print(sentenceValue)
                
                #Condencing the summaries by calculating the average
                average = int(sumValues / len(sentenceValue)) 
                for sentence in sentences:            
                    if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):                
                        summary += " " + sentence
                #print(summary)
                consum.append(summary)
                cur.execute('INSERT OR IGNORE INTO Data (title, author, genre, pub_date, sums) VALUES ( ?, ?, ?, ?, ? )', ( title, author, genre, pub_date, story) )
                cur.execute('INSERT OR IGNORE INTO Data (condencedSum) VALUES ( ? )', ( summary, ) )
                
                
            else:
                continue 
            
    except:
        print("I could not get a glipms of data mining here")
conn.commit()




#Data Visualization
n = int(input("How many of the most popular characters do you want to see? "))
sorted_items = sorted(freqTable.items(), key=lambda x: x[1], reverse=True)[:n]
max_list = dict(sorted_items)
print(max_list)




#Building a Word Cloud
fhand = open('gword.js','w')
fhand.write("gword = [")
first = True
for key,value in max_list.items():
    if not first : fhand.write( ",\n")
    first = False
    fhand.write("{text: '"+key+"', size: "+str(value)+"}")
fhand.write( "\n];\n")
fhand.close()



#Plotting 
perc =  [float(i) for i in max_list.values()]
plt.title(" Most Common Words")
plt.xlabel("Words")
plt.ylabel("Quantity")
plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)
plt.xticks(rotation=90, ha='right')
#sns.barplot(x=list(max_list.keys()),y=perc)


sns.relplot(data= max_list.items(), kind="line",facet_kws=dict(sharex=False),)

sns.displot(data=max_list.items(), kde=True)




#Closing the Cur Connection
cur.close()





