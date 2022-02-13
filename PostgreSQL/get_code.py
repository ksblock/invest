import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import psycopg2

host = 'localhost'
dbname = 'stock'
user = 'postgres'
password = 'ks1101'
port = 5432

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host,user,dbname,password,port)

class Program(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        ret = self.kiwoom.dynamicCall("CommConnect()")
        print(ret)
        self.kiwoom.OnEventConnect.connect(self.receiveLoginEvent)

    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("Login Success!")

            try:
                conn = psycopg2.connect(conn_string)
                print("DB Connect")

                cursor = conn.cursor()

                ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["8"])
                ETF_code_list = ret.split(';')

                for code in ETF_code_list:
                    if (code != ""):
                        name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])

                        cursor.execute("SELECT count(*) FROM stock_code.ETF WHERE code = \'" + code + "\';")
                        itemCount = cursor.fetchall()[0][0]

                        if (itemCount == 0):
                            cursor.execute(
                                "INSERT INTO stock_code.ETF(code, name) VALUES(\'" + code + "\',\'" + name + "\');")
                        else:
                            print("Already Exists")

                cursor.execute("SELECT * FROM stock_code.ETF;")
                result = cursor.fetchall()
                print(result)

                ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
                kospi_code_list = ret.split(';')

                for code in kospi_code_list:
                    cursor.execute("SELECT count(*) FROM stock_code.ETF WHERE code = \'" + code + "\';")
                    ETFCount = cursor.fetchall()[0][0]
                    if ETFCount == 1:
                        print("Exist in ETF")
                        continue

                    if(code != ""):
                        name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])

                        if "ETN" in name:
                            print("ETN 제외")
                            continue

                        cursor.execute("SELECT count(*) FROM stock_code.kospi WHERE code = \'" + code + "\';")
                        itemCount = cursor.fetchall()[0][0]

                        if (itemCount == 0):
                            cursor.execute("INSERT INTO stock_code.kospi(code, name) VALUES(\'" + code + "\',\'" + name + "\');")
                        else:
                            print("Already Exists")

                cursor.execute("SELECT * FROM stock_code.kospi;")
                result = cursor.fetchall()
                print(result)

                ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])
                kosdaq_code_list = ret.split(';')

                for code in kosdaq_code_list:
                    if (code != ""):
                        name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])

                        if "스팩" in name:
                            print("스팩 제외")
                            continue

                        cursor.execute("SELECT count(*) FROM stock_code.kosdaq WHERE code = \'" + code + "\';")
                        itemCount = cursor.fetchall()[0][0]

                        if (itemCount == 0):
                            cursor.execute(
                                "INSERT INTO stock_code.kosdaq(code, name) VALUES(\'" + code + "\',\'" + name + "\');")
                        else:
                            print("Already Exists")

                cursor.execute("SELECT * FROM stock_code.kosdaq;")
                result = cursor.fetchall()
                print(result)

                print("get_code.py success")

            except Exception as e:
                print("error")
                print(e)

            conn.commit()
            cursor.close()
            conn.close()
            exit(1)

        else:
            print(err_code)
            print("connect failed")




if __name__ == "__main__":
    print("get_code")
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()
