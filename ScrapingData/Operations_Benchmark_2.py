import pandas as pd
from pandas_datareader import data
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
from selenium import webdriver
import pytz
import time

## Import line below for Linux
#from pyvirtualdisplay import Display


BenchmarkScrapedList=['RealYield']

catDict={ 'benchmarker':BenchmarkScrapedList,
                       
                     }
colDict_benchmark={'Date':1,
        'Price':2,
        'Update':3,
        'UpdateTime':4
}


class Scraping_Price_Benchmark(object):
    def __init__(self):
        self.url='https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=realyield'
        
        
    def ScrapingOperation(self):
        #display=Display(visible=0, size=(1024,768))
        #display.start()
        
        option=webdriver.ChromeOptions()
        option.add_argument("--incognito")
        option.add_argument("--no-sandbox")
        
        for m in range(0,10):
            print(' Driver attempt : ',m)
            try:
                driver=webdriver.Chrome(chrome_options=option)
                #driver=webdriver.Chrome('/usr/local/bin/chromedriver',options=option)
                driver.implicitly_wait(30)
                print(' Driver successfully acquired ')
                break
            except:
                print(' Repeat acquiring driver ')
                time.sleep(10)
        
        eleLists=[]
        for n in BenchmarkScrapedList:
            for m in range(0,10):
                print(' attempt : ',m,' -- from ',n)
                try:
                    try:
                        driver.set_page_load_timeout(20)
                        driver.get(self.url)
                    except TimeoutException as te:
                        print(' Loading timed out, Kill driver ')
                        print(te)
                        driver.close()
                    elements= driver.find_elements_by_xpath('.//td[@class = "text_view_data"]') 
                    for title in elements:
                        output=title.text
                        eleLists.append(title.text)
                        #print(output, ' == ',type(output))
        
                    eleList=eleLists[-6:]
                    #display(eleList)
                    time.sleep(2)
                    break
                except:
                    print(n,' :: Error scraping ')
                    time.sleep(10)
    
        flowDf=pd.DataFrame(columns =['Date','10yr']) 
        flowDf=flowDf.append({'Date':eleList[0],'10yr':eleList[3]},ignore_index=True)
    
                        
        #driver.quit()
        #display.stop()
        del driver, eleList
        return flowDf

class ReadSheet_Benchmark(object):
    def __init__(self):
        self.secret_path_1=r'c:/users/70018928/Quantra_Learning/InvestmentSystem/TechnicalAnalysis/CheckInOutReminder-e2ff28c53e80.json'
        self.secret_path_2=r'./CheckInOutReminder-e2ff28c53e80.json'
        self.scope= ['https://spreadsheets.google.com/feeds',
                              'https://www.googleapis.com/auth/drive']

    def Authorization_Benchmark(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheetFList=[]
        cList=catDict['benchmarker']
        for n in cList:
            sheetFList.append(client.open("DataBenchmarking_Fund_2").worksheet(n))
        return sheetFList


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
    
    def InsertNewValue_1(self,todayStr, nowDate, nowTime, sheet, dateIn, priceIn, dateUpdate):
        lenRecords=len(sheet.get_all_values())
        list_of_hashes=sheet.get_all_records()
        lenHash=len(list_of_hashes)
        print(" len : ",lenRecords)
        lastDate=sheet.cell(lenRecords,1).value
        #print(' lastDate : ',lastDate, ' -- ',type(lastDate))
        #print(' dateIn : ',dateIn, ' -- ',type(dateIn))
        lenDate=len(list_of_hashes[lenHash-1]['Date'])
        if(dateIn == lastDate):
            todayRow=lenRecords
            row_index=todayRow
            col_index=colDict_benchmark['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_benchmark['Update']
            message=dateUpdate
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_benchmark['UpdateTime']
            message=nowTime
            sheet.update_cell(row_index, col_index,message)
            print('Updated at ', nowTime)
        else:
            todayRow=lenRecords+1
            row_index=todayRow
            col_index=colDict_benchmark['Date']
            message=todayStr
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_benchmark['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_benchmark['Update']
            message=dateUpdate
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict_benchmark['UpdateTime']
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
        lenDate=len(list_of_hashes[lenHash-1]['Date'])
        previousDate=sheet.cell(lenRecords-1,1).value
        previousPrice=sheet.cell(lenRecords-1,2).value
        
        return lastDate, previousDate, previousPrice



    def LoadSheet_0(self,sheet):
        listSheet = sheet.get_all_values()
        #print(' ==> ',type(listSheet)," :: ",listSheet)
        listHash=sheet.get_all_records()
        #print(' ==> ',type(listHash)," :: ",listHash)

        dfSet=pd.DataFrame()
        lenList=len(listHash)
        colList=listSheet[0]
        #print(colList)
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
        #print(dfSet.columns)
        dfSet.columns=colList

        return dfSet


    def LoadSheet(self,sheet):
        listSheet = sheet.get_all_values()
        #print(' ==> ',type(listSheet)," :: ",listSheet)
        listHash=sheet.get_all_records()
        #print(' ==> ',type(listHash)," :: ",listHash)

        dfSet=pd.DataFrame()
        lenList=len(listHash)
        colList=listSheet[0]
        #print(colList)
        dateList=[]
        priceList=[]
        updateList=[]
        for n in range(0,lenList):
            dateList.append(self.StrToDate(listHash[n][colList[0]]))
            priceList.append(listHash[n][colList[1]])
            updateList.append(listHash[n][colList[2]])
    
        dfSet=pd.concat([pd.DataFrame(dateList),pd.DataFrame(priceList),pd.DataFrame(updateList)],axis=1)
        dfSet.columns=colList

        return dfSet

    def LoadSheet_2(self,sheet):
        listSheet = sheet.get_all_values()
        #print(' ==> ',type(listSheet)," :: ",listSheet)
        listHash=sheet.get_all_records()
        #print(' ==> ',type(listHash)," :: ",listHash)

        dfSet=pd.DataFrame()
        lenList=len(listHash)
        colList=listSheet[0]
        #print(colList)
        dateList=[]
        priceList=[]
        updateList=[]
        volumeList=[]
        for n in range(0,lenList):
            dateList.append(self.StrToDate(listHash[n][colList[0]]))
            volumeList.append(listHash[n][colList[5]])
            priceList.append(listHash[n][colList[6]])
            updateList.append(listHash[n][colList[7]])
    
        dfSet=pd.concat([pd.DataFrame(dateList),pd.DataFrame(volumeList),pd.DataFrame(priceList),pd.DataFrame(updateList)],axis=1)
        dfSet.columns=['Date','Volume','Adj Close','UpdateTime']

        return dfSet


class LoadData(object):
    def __init__(self):
        self.QUANDL_API_KEY = 'abe1CkdZn-beCcde_GSt'
        self.start_date= '2015-01-01'
        self.filepath1=r'C:/Users/70018928/Quantra_Learning/data/'
        self.filepath2='data/'


    def LoadYahoo_Data(self,end, category):
        cList=catDict[category]
        dfList=[]
        for n in cList:
            dfList.append(data.get_data_yahoo(n, self.start_date, end))
        return dfList

    def LoadYahoo_Data_NoEnd(self,category):
        cList=catDict[category]
        dfList=[]
        for n in cList:
            dfList.append(data.get_data_yahoo(n, self.start_date))
        return dfList
    
    def WriteData(self,ticker,dfIn):
        try:
            fileout=self.filepath1+ticker+'.csv'
            dfIn.to_csv(fileout)
        except:
            fileout=self.filepath2+ticker+'.csv'
            dfIn.to_csv(fileout)

    def WriteInitialData(self,dfIn,category):
        cList=catDict[category]
        for n in range(0,len(dfIn)):
            filename=self.filepath1+cList[n]+'.csv'
            #print(cList[n])       
            dfIn[n].to_csv(filename)

    

            
         
        
    
    




