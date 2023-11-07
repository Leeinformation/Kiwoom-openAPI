from PyQt5.QtCore import *
from kiwoom import Kiwoom
from PyQt5.QtWidgets import *

class Thread1(QThread) :
    def __init__(self, parent) :
        super().__init__(parent)
        self.parent = parent
        
        self.k = Kiwoom()
        
        self.Acc_Screen = "1000"
        
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)
        self.detail_account_info_event_loop = QEventLoop()
        self.getItemList()
        self.detail_account_mystock()

    def getItemList(self) :
        marketList = ["0", "10"]
        
        for market in marketList :
            codeList = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(";")[:-1]
            
            for code in codeList :
                name = self.k.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)
                self.k.All_Stock_Code.update({code : {"종목명" : name}})
                
    def detail_account_mystock(self, sPrevNext=0) :
        print("계좌평가잔고내역 조회")
        account = self.parent.accComboBox.currentText()
        self.account_num = account
        print("선택 계좌는 %s" % self.account_num)

        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "")
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.Acc_Screen)

        self.detail_account_info_event_loop.exec_()
        
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "계좌평가잔고내역요청":

            column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
            colCount = len(column_head)
            rowCount = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.parent.stocklistTableWidget_2.setColumnCount(colCount)
            self.parent.stocklistTableWidget_2.setRowCount(rowCount)
            self.parent.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head) 
            
            print("계좌에 들어있는 종목 수 %s" % rowCount)

            totalBuyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)"))
            
            self.parent.label_l6.setText(str(totalBuyingPrice))
            self.parent.label_l7.setText(str(currentTotalPrice))
            self.parent.label_l8.setText(str(balanceAsset))
            self.parent.label_l9.setText(str(totalEstimateProfit))
            self.parent.label_l10.setText(str(total_profit_loss_rate))
            
            for index in range(rowCount) :
                itemCode = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목번호").strip(" ").strip("A")
                itemName = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목명")
                amount = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "보유수량"))
                buyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입가"))
                currentPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "현재가"))
                estimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "평가손익"))
                profitRate = float(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "수익률(%)"))
                total_chegual_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입금액")
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매매가능수량")
                possible_quantity = int(possible_quantity.strip())
                
                if itemCode in self.k.acc_portfolio :
                    pass
                else :
                    self.k.acc_portfolio.update({itemCode : {}})
                    
                self.k.acc_portfolio[itemCode].update({"종목명": itemName.strip()})
                self.k.acc_portfolio[itemCode].update({"보유수량": amount})
                self.k.acc_portfolio[itemCode].update({"매입가": buyingPrice})
                self.k.acc_portfolio[itemCode].update({"수익률(%)": profitRate})
                self.k.acc_portfolio[itemCode].update({"현재가": currentPrice})
                self.k.acc_portfolio[itemCode].update({"매입금액": total_chegual_price})
                self.k.acc_portfolio[itemCode].update({"매매가능수량": possible_quantity})

                self.parent.stocklistTableWidget_2.setItem(index, 0, QTableWidgetItem(str(itemCode)))
                self.parent.stocklistTableWidget_2.setItem(index, 1, QTableWidgetItem(str(itemName)))
                self.parent.stocklistTableWidget_2.setItem(index, 2, QTableWidgetItem(str(amount)))
                self.parent.stocklistTableWidget_2.setItem(index, 3, QTableWidgetItem(str(buyingPrice)))
                self.parent.stocklistTableWidget_2.setItem(index, 4, QTableWidgetItem(str(currentPrice)))
                self.parent.stocklistTableWidget_2.setItem(index, 5, QTableWidgetItem(str(estimateProfit)))
                self.parent.stocklistTableWidget_2.setItem(index, 6, QTableWidgetItem(str(profitRate)))

            if sPrevNext == "2":
                self.detail_acount_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()