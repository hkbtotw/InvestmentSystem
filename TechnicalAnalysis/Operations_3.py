import pandas as pd
from pandas_datareader import data
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import pytz
import time

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from pyvirtualdisplay import Display

import re
import os


fundList=['TMBCOF','ONE-UGG-RA','K-USA-A(A)','KFGBRAND-A','WE-CHIG', 'WE-CYBER']
BenchmarkList=['CSI300','SP500','USDIndex']
BenchmarkScrapeList=['MSCIW']
BenchmarkScrapedCode=['msci-world']
BenchmarkCode=['000300.SS','^GSPC','DX-Y.NYB']
BenchmarkDict=dict(zip(BenchmarkList,BenchmarkCode))
BenchmarkScrapedDict=dict(zip(BenchmarkList,BenchmarkScrapedCode))

catDict={ 'Fund':fundList,
          'Benchmark':BenchmarkList
        }

colDict_1={'Date':1,
        'Price':2,
        'Update':3,
        'UpdateTime':4
        }


class Scraping_Price(object):
    def __init__(self):
        self.url_fund='https://www.finnomena.com/fund/'
        self.url_vn30='https://th.investing.com/indices/vn-30'
        self.url_msciw='https://th.investing.com/indices/msci-world'
        
    def ScrapingOperation(self):
        #display=Display(visible=0, size=(1024,768))
        #display.start()

        option=webdriver.ChromeOptions()
        option.add_argument("--incognito")
        driver = webdriver.Chrome(chrome_options=option)
        #driver=webdriver.Chrome('/usr/local/bin/chromedriver',options=option)
        driver.implicitly_wait(30)

        priceList=[]
        updateList=[]
        for n in fundList:
            driver.get(self.url_fund+n)
            elements= driver.find_elements_by_xpath('.//div[@class = "fund-nav-percent"]') 
            print(' elements : ',list(elements))
            result=elements[0].text.split("\n")
            print(' ==> ', result)
            print(result[0], ' :: ',result[1])
            priceList.append(result[0])
            updateList.append(result[1])
            time.sleep(2)
        
        driver.quit()
        driver = webdriver.Chrome(chrome_options=option)
        #driver=webdriver.Chrome('/usr/local/bin/chromedriver',options=option)
        driver.implicitly_wait(30)

        df=pd.DataFrame(list(zip(fundList, priceList, updateList)), columns=['Name','Price','Update'])
        dfOut=df.set_index(['Name'])

        driver.get(self.url_vn30)
        elements= driver.find_elements_by_xpath('.//span[@id = "chart-info-last"]')    
        print(' elements : ',list(elements))
        print(' vn30-price :',elements[0].text)    
        vn30Price=elements[0].text.replace(",","")
        elements= driver.find_elements_by_xpath('.//span[@class = "bold pid-41064-time"]')        
        print(' vn30-date  :',elements[0].text)    
        vn30Updatedate=elements[0].text
        vn30Df=pd.DataFrame(columns=['Name','Price','Update'])
        vn30Df=vn30Df.append({'Name':'VN30','Price':float(vn30Price), 'Update':vn30Updatedate}, ignore_index=True)
        vn30Df=vn30Df.set_index(['Name'])
        time.sleep(2)

        driver.get(self.url_msciw)
        try:
            elements= driver.find_elements_by_xpath('.//span[@id = "chart-info-last"]')   
            print(' elements : ',list(elements))     
            print(' msciw-price :',elements[0].text)    
            msciwPrice=elements[0].text.replace(",","")
        except:
            msciwPrice=""
        try:
            elements= driver.find_elements_by_xpath('.//span[@class = "bold pid-41064-time"]')        
            print(' msciw-date :',elements[0].text)    
            msciwUpdatedate=elements[0].text
        except:
            msciwUpdatedate=""
        msciwDf=pd.DataFrame(columns=['Name','Price','Update'])
        msciwDf=msciwDf.append({'Name':'VN30','Price':float(msciwPrice), 'Update':msciwUpdatedate}, ignore_index=True)
        msciwDf=msciwDf.set_index(['Name'])

        driver.quit()
        #display.stop()
        del driver, df
        return  dfOut, vn30Df, msciwDf


class ReadSheet(object):
    def __init__(self):
        self.secret_path_1=r'c:/users/70018928/Quantra_Learning/CheckInOutReminder-e2ff28c53e80.json'
        #self.secret_path_1=r'/home/pi/Project/Webscraping/CheckInOutReminder-e2ff28c53e80.json'
        self.secret_path_2=r'./CheckInOutReminder-e2ff28c53e80.json'
        self.scope= ['https://spreadsheets.google.com/feeds',
                              'https://www.googleapis.com/auth/drive']
    
    def Authorization_Fund(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=catDict['Fund']
        for n in cList:
            sheetHList.append(client.open("DataScraping_Fund_1").worksheet(n))
        return sheetHList

    def Authorization_Benchmark(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=catDict['Benchmark']
        for n in cList:
            #print(n.title)
            sheetHList.append(client.open("DataBenchmarking_Fund_1").worksheet(n))
        return sheetHList    

    def Authorization_Benchmark_Scaped(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=BenchmarkScrapeList
        for n in cList:
            #print(n.title)
            sheetHList.append(client.open("DataBenchmarking_Fund_2").worksheet(n))
        return sheetHList   

    
    def StrToDate(self,strIn):
        return datetime.strptime(strIn, '%Y-%m-%d')

    def Date2TString(self, dateIn):
        return dateIn.strftime("%Y-%m-%d")

    def GetDateTime(self):
        todayUTC=datetime.today()
        nowUTC=datetime.now()
        # dd/mm/YY H:M:S
        to_zone = pytz.timezone('Asia/Bangkok')

        today=todayUTC.astimezone(to_zone)
        now=nowUTC.astimezone(to_zone)

        todayStr=today.strftime("%Y-%m-%d")
        nowDate = now.strftime("%Y-%m-%d")
        nowTime = now.strftime("%H:%M:%S")

        #print(' today : ',todayStr)
        #print(nowDate, ' ==> ', nowTime)
        return todayStr, nowDate, nowTime

    def InsertNewValue_1(self,todayStr, nowDate, nowTime, sheet, dateIn, priceIn, updateIn):
        lenRecords=len(sheet.get_all_values())
        list_of_hashes=sheet.get_all_records()
        lenHash=len(list_of_hashes)
        print(" len : ",lenRecords)
        lastDate=sheet.cell(lenRecords,1).value
        print(' lastDate : ',lastDate)
        lenDate=len(list_of_hashes[lenHash-1]['Date'])
        if(dateIn == lastDate):
            todayRow=lenRecords
            row_index=todayRow
            col_index=colDict_1['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_1['Update']
            message=updateIn
            sheet.update_cell(row_index, col_index,message)   
            col_index=colDict_1['UpdateTime']
            message=nowTime
            sheet.update_cell(row_index, col_index,message)            
            print('Updated at ', nowTime)
        else:
            todayRow=lenRecords+1
            row_index=todayRow
            col_index=colDict_1['Date']
            message=todayStr
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_1['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_1['Update']
            message=updateIn
            sheet.update_cell(row_index, col_index,message) 
            col_index=colDict_1['UpdateTime']
            message=nowTime
            sheet.update_cell(row_index, col_index,message)               
            print('Updated on ', todayStr, ' :: ', nowTime)

    def GetPreviousValue(self, todayStr, nowDate, nowTime, sheet):
        lenRecords=len(sheet.get_all_values())
        list_of_hashes=sheet.get_all_records()
        lenHash=len(list_of_hashes)
        print(" len : ",lenRecords)
        lastDate=sheet.cell(lenRecords,1).value
        print(' lastDate : ',lastDate)
        #lenDate=len(list_of_hashes[lenHash-1]['Date'])
        #previousDate=sheet.cell(lenRecords-1,1).value
        minPrice=sheet.cell(lenRecords-1,4).value
        minDate=sheet.cell(lenRecords-1,5).value
        
        return lastDate, minDate, minPrice
    
    def LoadSheet(self,sheet):
        listSheet=sheet.get_all_values()
        listHash=sheet.get_all_records()
        dfSet=pd.DataFrame()
        lenList=len(listHash)
        colList=listSheet[0]
        dateList=[]
        priceList=[]
        updateList=[]
        updateTimeList=[]
        for n in range(0,lenList):
            dateList.append(self.StrToDate(listHash[n][colList[0]]))
            priceList.append(listHash[n][colList[1]])
            updateList.append(listHash[n][colList[2]])
            updateTimeList.append(listHash[n][colList[3]])
        
        dfSet=pd.concat([pd.DataFrame(dateList),pd.DataFrame(priceList),pd.DataFrame(updateList),pd.DataFrame(updateTimeList)],axis=1)
        dfSet.columns=['Date','Price','Update','UpdateTime']
        
        return dfSet