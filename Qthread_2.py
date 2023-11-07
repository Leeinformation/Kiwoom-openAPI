from PyQt5.QtCore import *
from kiwoom import Kiwoom
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from datetime import datetime, timedelta

class Thread2(QThread) :
    def __init__(self, parent) :
        super().__init__(parent)
        self.parent = parent
        
        self.k = Kiwoom()
        
        self.Find_down_Screen = "1200"
        self.code_in_all = None
        
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)
        
        self.detail_account_info_event_loop = QEventLoop()
        
        self.C_K_F_class()
        
        column_head = ["종목코드", "종목명", "위험도"]
        colCount = len(column_head)
        rowCount = len(self.k.acc_portfolio)
        
        self.parent.Danger_wd.setColumnCount(colCount)
        self.parent.Danger_wd.setRowCount(rowCount)
        self.parent.Danger_wd.setHorizontalHeaderLabels(column_head)
        idx2 = 0
        
        for i in self.k.acc_portfolio.keys() :
            self.parent.Danger_wd.setItem(idx2, 0, QTableWidgetItem(str(i)))
            self.parent.Danger_wd.setItem(idx2, 1, QTableWidgetItem(self.k.acc_portfolio[i]["종목명"]))
            self.parent.Danger_wd.setItem(idx2, 2, QTableWidgetItem(self.k.acc_portfolio[i]["위험도"]))
            idx2 += 1
        
    def C_K_F_class(self) :
        code_list = []
        
        for code in self.k.acc_portfolio.keys() :
            code_list.append(code)
            
        print(f"계좌 종목 개수 {len(code_list)}")
        
        for idx, code in enumerate(code_list) :
            QTest.qWait(3000)
            
            self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", self.Find_down_Screen)
            
            self.code_in_all = code
            print(f"{idx+1} / {len(code_list)} : 종목 검사 중 코드이름 : {self.code_in_all}")
            
            date_today = datetime.today().strftime("%Y%m%d")
            date_prev = datetime.today() - timedelta(10)
            date_prev = date_prev.strftime("%Y%m%d")
            
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시작일자", date_prev)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종료일자", date_today)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기관추정단가구분", "1")
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "외인추정단가구분", "1")
            
            self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "종목별기관매매추이요청", "opt10045", "0", self.Find_down_Screen)
            self.detail_account_info_event_loop.exec()
            
    def institutional_trading_batch(self, a, c) :
        a = a[0:4]
        c = c[0:4]
        print(a)
        
        if all(x < 0 for x in a) and all(x < 0 for x in c) :
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "손절"})
        elif all(x < 0 for x in a[:3]) and all(x < 0 for x in c[:3]) :
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "주의"})
        elif all(x < 0 for x in a[:2]) and all(x < 0 for x in c[:2]) :
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "관심"})
        else :
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "낮음"})
            
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext) :
        if sRQName == "종목별기관매매추이요청" :
            cnt2 = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            
            self.calcul2_data = []
            self.calcul2_data2 = []
            self.calcul2_data3 = []
            self.calcul2_data4 = []
            
            for i in range(cnt2) :
                institutional_trading = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "기관일별순매매수량"))
                institutional_trading_avg = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "기관추정평균가"))
                forgin_trading = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "외인일별순매매수량"))
                forgin_trading_avg = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "외인추정평균가"))
                per = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "등락율"))
                close = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "종가"))
                
                self.calcul2_data.append(int(institutional_trading.strip()))
                self.calcul2_data2.append(abs(int(close.strip())))
                self.calcul2_data2.append(abs(int(institutional_trading_avg.strip())))
                self.calcul2_data2.append(abs(int(forgin_trading_avg.strip())))
                self.calcul2_data3.append(int(forgin_trading.strip()))
                self.calcul2_data4.append(float(per.strip()))
                
            self.institutional_trading_batch(self.calcul2_data, self.calcul2_data3)
            self.detail_account_info_event_loop.exit()