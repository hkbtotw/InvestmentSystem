### Scrape VIX data , see what is VIX in ref:
### https://www.finnomena.com/mr-messenger/vix/
### Dont forget , VIX is for US market, you look relatively with its mean value.

from Operations_4 import *
import numpy as np
from datetime import datetime, timedelta

#Declare class
scrapingPrice=Scraping_Price()
readSheet=ReadSheet()

# Declare function
sheetMList=readSheet.Authorization_BenchmarkScraped()

todayStr, nowDate, nowTime=readSheet.GetDateTime()
#print(' df : ',dfIn)
#print(' catDict : ',catDict)

dfIn=scrapingPrice.ScrapingOperation()

print(dfIn)

for  n in sheetMList:
    print(' n :',n, ' title : ',n.title)
    dummyStr=str(dfIn.loc[n.title,['Price']])
    out=dummyStr.split("\n")
    dummyStr=out[0].replace("Price","")
    updatedPrice=float(dummyStr.replace(",",""))
    
    #updatedPrice=dfIn['Price'].values[0]
    #updatedDate=dfIn['Update'].values[0]   
    
    print(updatedPrice, ' :: ',type(updatedPrice))   
    updatedDate=todayStr
    print(updatedDate, ' :: ',type(updatedDate))
    readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, n ,nowDate, updatedPrice, updatedDate)
    print(' Complete ')

del dfIn, sheetMList