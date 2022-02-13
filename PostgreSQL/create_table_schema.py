import psycopg2

host = 'localhost'
dbname = 'stock'
user = 'postgres'
password = 'ks1101'
port = 5432

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host,user,dbname,password,port)

def create_table():
    try:
        conn = psycopg2.connect(conn_string)
        print("connect create_table")

        cursor = conn.cursor()

        #cursor.execute("TRUNCATE TABLE daily_price.kospi CASCADE;")
        #cursor.execute("TRUNCATE TABLE daily_price.kosdaq CASCADE;")
        #cursor.execute("TRUNCATE TABLE daily_price.ETF CASCADE;")
        #cursor.execute("TRUNCATE TABLE basic_info.kospi CASCADE;")
        #cursor.execute("TRUNCATE TABLE basic_info.kosdaq CASCADE;")
        #cursor.execute("TRUNCATE TABLE stock_code.kospi CASCADE;")
        #cursor.execute("TRUNCATE TABLE stock_code.kosdaq CASCADE;")
        #cursor.execute("TRUNCATE TABLE stock_code.ETF CASCADE;")
        #print("테이블 제거")

        #cursor.execute("drop SCHEMA IF EXISTS stock_code;")
        #cursor.execute("drop SCHEMA IF EXISTS daily_price;")
        #cursor.execute("drop SCHEMA IF EXISTS basic_info;")
        #print("스키마 제거")

        #cursor.execute("create SCHEMA IF NOT EXISTS stock_code;")
        #cursor.execute("create SCHEMA IF NOT EXISTS daily_price;")
        #cursor.execute("create SCHEMA IF NOT EXISTS basic_info;")
        #print("스키마 생성")

        #cursor.execute("create TABLE stock_code.kospi(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")
        #cursor.execute("create TABLE stock_code.kosdaq(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")
        #cursor.execute("create TABLE daily_price.kospi(code varchar(6) NOT NULL REFERENCES stock_code.kospi(code), date integer NOT NULL, price integer, PRIMARY KEY(code, date));")
        #cursor.execute("create TABLE daily_price.kosdaq(code varchar(6) NOT NULL REFERENCES stock_code.kosdaq(code), date integer NOT NULL, price integer, PRIMARY KEY(code, date));")
        cursor.execute("create TABLE basic_info.kospi(code varchar(6) NOT NULL REFERENCES stock_code.kospi(code) PRIMARY KEY, price integer, market integer, sales integer, profit integer);")
        cursor.execute("create TABLE basic_info.kosdaq(code varchar(6) NOT NULL REFERENCES stock_code.kosdaq(code) PRIMARY KEY, price integer, market integer, sales integer, profit integer);")
        print("테이블 생성")

    except Exception as e:
        print("connect failed at create_table_schema.py")
        print(e)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_table()