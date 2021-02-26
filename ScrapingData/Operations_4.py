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


BenchmarkList_1=['USDIndex'] # only used to be read in to make plot, not used for scraping
BenchmarkList_2=['MSCIW'] # # only used to be read in to make plot, not used for scraping
BenchmarkScrapedList=['VIX','MSCIUS','MSCICN','ARKW']
BenchmarkScrapedCode=['indices/volatility-s-p-500','indices/msci-us-net-usd','indices/msci-china-net-usd','etfs/ark-web-x-0-advanced-chart']

benchmarkScrapedDict=dict(zip(BenchmarkScrapedList,BenchmarkScrapedCode))


catDict={ 
        'BenchmarkScrapedList':BenchmarkScrapedList,
        'BenchmarkList_1':BenchmarkList_1,
        'BenchmarkList_2':BenchmarkList_2
        }

colDict_1={'Date':1,
        'Price':2,
        'Update':3,
        'UpdateTime':4
        }


class Scraping_Price(object):
    def __init__(self):
        self.url='https://th.investing.com/'
        
    def ScrapingOperation(self):
        # today date
        today = date.today()       
        d1 = today.strftime("%Y-%m-%d")

        #display=Display(visible=0, size=(1024,768))
        #display.start()

        option=webdriver.ChromeOptions()
        option.add_argument("--incognito")
        option.add_argument("--no-sandbox")
        #driver = webdriver.Chrome(chrome_options=option)
        #driver=webdriver.Chrome('/usr/local/bin/chromedriver',options=option)
        #driver.implicitly_wait(30)

        for m in range(0,10):
            print(' Driver attempt :',m)
            try:
                driver = webdriver.Chrome(chrome_options=option)
                #driver=webdriver.Chrome('/usr/local/bin/chromedriver',options=option)
                driver.implicitly_wait(30)
                print(' Driver successfully acqiored ')
                break
            except:
                print(' Repeat acquiring driver ')
                time.sleep(10)

        priceList=[]   
        updateList=[]     
        for n in BenchmarkScrapedList:
            for m in range(0,10):
                print(' attempt ', m,' -- from fund -> ',n)
                try:
                    try:
                        driver.set_page_load_timeout(20)
                        driver.get(self.url+benchmarkScrapedDict[n])   
                               
                    except TimeoutException as te:
                        print("Loading timed out. Killer driver")
                        print(te)
                        driver.close()

                    elements= driver.find_elements_by_xpath('.//span[@id = "last_last"]') 
            
                    print(n,' : ',elements[0].text)
                    priceList.append(elements[0].text)
                    updateList.append(d1)
                    time.sleep(2)
                    break
                except:
                    print(n,' :: ERROR Scraping')          
                    #priceList.append('0')  
                    #updateList.append(d1)
                    time.sleep(10)
        


        df=pd.DataFrame(list(zip(BenchmarkScrapedList, priceList, updateList)), columns=['Name','Price','Update'])
        dfOut=df.set_index(['Name'])


        driver.quit()
        #display.stop()
        del driver, df, priceList, updateList
        return  dfOut


class ReadSheet(object):
    def __init__(self):
        self.secret_path_1=r'c:/users/70018928/Quantra_Learning/InvestmentSystem/TechnicalAnalysis/CheckInOutReminder-e2ff28c53e80.json'
        #self.secret_path_1=r'/home/pi/Project/Webscraping/CheckInOutReminder-e2ff28c53e80.json'
        self.secret_path_2=r'./CheckInOutReminder-e2ff28c53e80.json'
        self.scope= ['https://spreadsheets.google.com/feeds',
                              'https://www.googleapis.com/auth/drive']

    def Authorization_BenchmarkScraped(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=catDict['BenchmarkScrapedList']
        for n in cList:
            #print(n.title)
            sheetHList.append(client.open("DataBenchmarking_Fund_2").worksheet(n))
        return sheetHList
    
    def Authorization_Benchmark(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=catDict['BenchmarkList_1']
        for n in cList:
            #print(n.title)
            sheetHList.append(client.open("DataBenchmarking_Fund_1").worksheet(n))
        return sheetHList
    
    def Authorization_Benchmark_2(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetHList=[]
        cList=catDict['BenchmarkList_2']
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