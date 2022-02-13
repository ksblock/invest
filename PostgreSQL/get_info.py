import sys
import time
import psycopg2
from decimal import Decimal
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

host = 'localhost'
dbname = 'stock'
user = 'postgres'
password = 'ks1101'
port = 5432

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host,user,dbname,password,port)

STANDARD_DATE = datetime.today().strftime("%Y%m%d")
TR_REQ_TIME_INTERVAL = 0.5

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._API_Setting()
        self._event_mapping()
        self.req_stock_code = ""
        self.isHappendError = False

    def _API_Setting(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _event_mapping(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._event_receive_tr_data)

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def comm_connect(self):
        print("connect?")
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):

            # 받은 데이터를 하나씩 읽는 함수에 전달
            # 여러 종류의 TR을 요청해도 모두 이 메서드 내에서 처리해야한다.
        if rqname == "opt10001_req":
            self._opt10001(rqname, trcode)


        try:
            self.tr_event_loop.exit()  # 사용되어 필요없는 이벤트 루프를 종료한다.
        except AttributeError:
            pass

    def get_kospi_list(self):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()

            cursor.execute("SELECT code FROM stock_code.kospi")
            kospi_list = cursor.fetchall()

        except Exception as e:
            print("error in get_info.py/get_kospi_list")
            print(e)
            print(type(e))

        cursor.close()
        conn.close()
        return kospi_list

    def get_kosdaq_list(self):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()

            cursor.execute("SELECT code FROM stock_code.kosdaq")
            kosdaq_list = cursor.fetchall()

        except Exception as e:
            print("error in get_info.py/get_kosdaq_list")
            print(e)
            print(type(e))

        cursor.close()
        conn.close()
        return kosdaq_list

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_get_data(self, code, field_name, real_type, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, QString, QString)", code, field_name, real_type, item_name)
        print(ret, item_name)
        return ret.strip()

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _opt10001(self, rqname, trcode):

        try:
            conn = psycopg2.connect(conn_string)
            print("연결성공")
            cursor = conn.cursor()

            #price = self._comm_get_data(trcode, rqname, 0, "현재가")
            market = self._comm_get_data(trcode, rqname, 0, "시가총액")
            sales = self._comm_get_data(trcode, rqname, 0, "매출액")
            profit = self._comm_get_data(trcode, rqname, 0, "영업이익")
            #per = self._comm_get_data(trcode, rqname, 0, "PER")
            #eps = self._comm_get_data(trcode, rqname, 0, "EPS")
            #roe = self._comm_get_data(trcode, rqname, 0, "ROE")
            #pbr = self._comm_get_data(trcode, rqname, 0, "PBR")
            #ev = self._comm_get_data(trcode, rqname, 0, "EV")
            #bps = self._comm_get_data(trcode, rqname, 0, "BPS")

            if sales == "":
                sales = "0"
            if profit == "":
                profit = "0"
            print(self.req_stock_code, market, sales, profit)

            #종목 코드로 stock_code.kospi, kosdaq 검색해서
            cursor.execute("SELECT count(*) FROM stock_code.kospi WHERE code = \'" + self.req_stock_code + "\';")
            isKospi = cursor.fetchall()[0][0]   #코스피에 없으면 코스닥에 있겠지?

            cursor.execute("SELECT count(*) FROM stock_code.kosdaq WHERE code = \'" + self.req_stock_code + "\';")
            isKosdaq = cursor.fetchall()[0][0]

            print(isKospi, isKosdaq)
            if isKospi == 1:
                cursor.execute("insert INTO basic_info.kospi(code, market, sales, profit) VALUES(\'" + self.req_stock_code + "\',\'" + market + "\',\'" + sales + "\',\'" + profit + "\');")
            elif isKosdaq == 1:
                cursor.execute("insert INTO basic_info.kosdaq(code, market, sales, profit) VALUES(\'" + self.req_stock_code + "\',\'" + market + "\',\'" + sales + "\',\'" + profit + "\');")

            conn.commit()  # 이게 없으면 실제로 반영이 안됨.

        except Exception as e:
            print("error")
            print(e)
            self.isHappendError = True
            print("이미 존재하는 데이터 발견")

        conn.commit()  # 이게 없으면 실제로 반영이 안됨.
        cursor.close()
        conn.close()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()


    kospi_list = kiwoom.get_kospi_list()
    kosdaq_list = kiwoom.get_kosdaq_list()

    code_list = kospi_list + kosdaq_list
    print(len(code_list))
    i = 0
    for code in code_list:
        i += 1
        if i <= 2000:
            continue


        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.req_stock_code = code[0]
        kiwoom.set_input_value("종목코드", kiwoom.req_stock_code)
        kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "0101")

        #kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")