import sys
import time
import psycopg2
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

    def _event_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

            # 받은 데이터를 하나씩 읽는 함수에 전달
            # 여러 종류의 TR을 요청해도 모두 이 메서드 내에서 처리해야한다.
        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        try:
            self.tr_event_loop.exit()  # 사용되어 필요없는 이벤트 루프를 종료한다.
        except AttributeError:
            pass

    def comm_connect(self):
        print("connect?")
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

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

    def get_ETF_list(self):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()

            cursor.execute("SELECT code FROM stock_code.ETF")
            ETF_list = cursor.fetchall()

        except Exception as e:
            print("error in get_info.py/get_ETF_list")
            print(e)
            print(type(e))

        cursor.close()
        conn.close()
        return ETF_list

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code, real_type, field_name, index, item_name)
        return ret.strip()

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _opt10081(self, rqname, trcode):
        data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        print(data_cnt)

        if data_cnt > 300:
            data_cnt = 300

        try:
            conn = psycopg2.connect(conn_string)
            print("연결성공")
            cursor = conn.cursor()

            for i in range(data_cnt):
                date = self._comm_get_data(trcode, "", rqname, i, "일자")
                close = self._comm_get_data(trcode, "", rqname, i, "현재가")
                volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

                print(date, self.req_stock_code, close, volume)

                #종목 코드로 stock_code.kospi, kosdaq 검색해서
                cursor.execute("SELECT count(*) FROM stock_code.kospi WHERE code = \'" + self.req_stock_code + "\';")
                isKospi = cursor.fetchall()[0][0]   #코스피에 없으면 코스닥에 있겠지?

                cursor.execute("SELECT count(*) FROM stock_code.kosdaq WHERE code = \'" + self.req_stock_code + "\';")
                isKosdaq = cursor.fetchall()[0][0]

                cursor.execute("SELECT count(*) FROM stock_code.ETF WHERE code = \'" + self.req_stock_code + "\';")
                isETF = cursor.fetchall()[0][0]

                if isKospi == 1:
                    cursor.execute("insert INTO daily_price.kospi(code, date, price) VALUES(\'" + self.req_stock_code + "\',\'" + date + "\',\'" + close + "\');")
                elif isKosdaq == 1:
                    cursor.execute("insert INTO daily_price.kosdaq(code, date, price) VALUES(\'" + self.req_stock_code + "\',\'" + date + "\',\'" + close + "\');")
                elif isETF == 1:
                    cursor.execute("insert INTO daily_price.ETF(code, date, price) VALUES(\'" + self.req_stock_code + "\',\'" + date + "\',\'" + close + "\');")

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

    argument = []
    argument.append(sys.argv[0])
    market = sys.argv[1]

    app = QApplication(argument)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    if market == 'kospi':
        code_list = kiwoom.get_kospi_list()
    elif market == 'kosdaq':
        code_list = kiwoom.get_kosdaq_list()
    elif market == 'etf':
        code_list = kiwoom.get_ETF_list()
    else:
        print("Wrong market")
        sys.exit()

    i = 1
    for code in code_list:
        print(i)
        i+=1

        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.req_stock_code = code[0]
        kiwoom.set_input_value("종목코드", kiwoom.req_stock_code)
        kiwoom.set_input_value("기준일자", STANDARD_DATE)
        kiwoom.set_input_value("수정주가구분", 0)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        '''
        while (kiwoom.remained_data == True) and (kiwoom.isHappendError == False):
            time.sleep(TR_REQ_TIME_INTERVAL)
            kiwoom.set_input_value("종목코드", kiwoom.req_stock_code)
            kiwoom.set_input_value("기준일자", STANDARD_DATE)
            kiwoom.set_input_value("수정주가구분", 0)
            kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
        '''