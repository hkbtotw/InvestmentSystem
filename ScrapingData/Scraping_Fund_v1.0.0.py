from Operations_3 import *
import numpy as np
from datetime import datetime, timedelta

#Declare class
scrapingPrice=Scraping_Price()
readSheet=ReadSheet()

# Declare function
sheetFList=readSheet.Authorization_Fund()
sheetMList=readSheet.Authorization_Benchmark()
sheetSList=readSheet.Authorization_Benchmark_Scaped()

todayStr, nowDate, nowTime=readSheet.GetDateTime()
#print(' df : ',dfIn)
#print(' catDict : ',catDict)

dfIn, msciwDf=scrapingPrice.ScrapingOperation()

for n in sheetFList:
    #print(' n :',n, ' title : ',n.title)    
    updatedPrice=float(dfIn.loc[n.title,['Price']])
    dummyStr=str(dfIn.loc[n.title,['Update']])
    out=dummyStr.split("\n")
    dummyStr=out[0].replace("Update","")
    dummyStr=dummyStr.lstrip()    
    updatedDate=dummyStr
    readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, n ,nowDate, updatedPrice, updatedDate)
    print(' Complete ')


del sheetFList

### Record Benchmarking Data extracted from Yahoo Finance
today=datetime.now()
dm1 = today - timedelta(days=1)
dm3 = today - timedelta(days=3)
d=todayStr
dm3=dm3.strftime("%Y-%m-%d")

groupList=BenchmarkCode

print(groupList)
readFlag=False
def ReadData(groupList,d,dm3,readFlag):
    try:
        dfIn= data.DataReader(groupList,start=d,data_source='yahoo') #['Adj Close']
        readFlag=True
        print(' Today data logged ')
    except:
        dfIn= data.DataReader(groupList,start=dm3,data_source='yahoo') #['Adj Close']
        readFlag=False
        print(' today data not available ')
    return dfIn, readFlag

iteration=10
for i in range(1,iteration):
    print('attempt :',i)
    if(readFlag==False):
        dfIn, readFlag=ReadData(groupList,d,dm3,readFlag)
    else:
        break

dfPre=dfIn.tail(1).copy()

for  n in sheetMList:
    #print(' n :',n, ' title : ',n.title)
    updatedPrice=dfPre['Adj Close'][BenchmarkDict[n.title]].values[0]
    print(' Price : ',updatedPrice)
    if(np.isnan(updatedPrice)):
        print(' Not logged ')
    else:
        updatedDate=todayStr
        readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, n ,nowDate, updatedPrice, updatedDate)
        print(' Complete ')


del dfPre, dfIn, sheetMList

for  n in sheetSList:
    #print(' n :',n, ' title : ',n.title)
    updatedPrice=msciwDf['Price'].values[0]
    updatedDate=msciwDf['Update'].values[0]    

    if(np.isnan(updatedPrice)):
        print(' Not logged ')
    else:
        updatedDate=todayStr
        readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, n ,nowDate, updatedPrice, updatedDate)
        print(' Complete ')

del msciwDf, sheetSList