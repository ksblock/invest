import psycopg2
from create_table_schema import create_table
from get_code import get_code
from get_info import get_info

def main():
    host = 'localhost'
    dbname = 'stock'
    user = 'postgres'
    password = 'ks1101'
    port = 5432

    conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host,user,dbname,password,port)

    create_table(conn_string)
    get_code()
    get_info()

if __name__ == "__main__":
	main()