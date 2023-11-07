import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

from kiwoom import Kiwoom
from Qthread_1 import Thread1

form_class = uic.loadUiType("pytrader.ui")[0]

class Login_Machnine(QMainWindow, QWidget, form_class) :
    def __init__(self, *args, **kwargs) :
        print("Login Machine 실행")
        super(Login_Machnine, self).__init__(*args, **kwargs)
        form_class.__init__(self)
        self.setUI()
        
        self.label_l1.setText(str("총매입금액"))
        self.label_l2.setText(str("총평가금액"))
        self.label_l3.setText(str("추정예탁자산"))
        self.label_l4.setText(str("총평가손익금액"))
        self.label_l5.setText(str("총수익률(%)"))
        
        self.login_event_loop = QEventLoop()
        
        self.k = Kiwoom()
        self.set_signal_slot()
        self.signal_login_commConnect()
        
        self.call_account.clicked.connect(self.c_acc)
        
    def setUI(self) :
        self.setupUi(self)
        
    def set_signal_slot(self) :
        self.k.kiwoom.OnEventConnect.connect(self.login_slot)
        
    def signal_login_commConnect(self) :
        self.k.kiwoom.dynamicCall("CommConnect()")
        
        self.login_event_loop.exec_()
        
    def login_slot(self, errCode) :
        if errCode == 0 :
            print("로그인 성공")
            self.statusbar.showMessage("로그인 성공")
            self.get_account_info()
            
        elif errCode == -100 :
            print("사용자 정보교환 실패")
        elif errCode == -101 :
            print("서버접속 실패")
        elif errCode == -102 :
            print("버전처리 실패")
        self.login_event_loop.exit()
        
    def get_account_info(self) :
        account_list = self.k.kiwoom.dynamicCall("GetLoginInfo(String)", "ACCNO")
        for i in account_list.split(';') :
            self.accComboBox.addItem(i)
            
    def c_acc(self) :
        print("선택 계좌 정보 가져오기")
        h1 = Thread1(self)
        h1.start()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    CH = Login_Machnine()
    CH.show()
    app.exec_()