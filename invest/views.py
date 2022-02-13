from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Memo
from .forms import MemoForm

import psycopg2
import json
import base64

from sqlalchemy import create_engine
from pandas import DataFrame, read_sql, concat

host = 'localhost'
dbname = 'stock'
user = 'postgres'
password = 'ks1101'
port = 5432

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host,user,dbname,password,port)


# Create your views here.
def index(request):
    return render(request, 'invest/index.html')

def chart(request):
    return render(request, 'invest/chart.html')

def chart_result(request):
    if request.method == 'POST':
        search_word = request.POST['searched']
        print(search_word)

        try:
            conn = psycopg2.connect(conn_string)
            print("connect")

            cursor = conn.cursor()

            cursor.execute("SELECT count(*) FROM stock_code.kospi WHERE name = \'" + search_word + "\';")
            isKospi = cursor.fetchall()[0][0]
            print(isKospi)
            if isKospi == 1:
                cursor.execute("SELECT code FROM stock_code.kospi WHERE name = \'" + search_word + "\';")
                code = cursor.fetchall()[0][0]
                print(code)
                cursor.execute("SELECT date, price FROM daily_price.kospi WHERE code = \'" + code + "\' ORDER BY date ASC;")
                data = cursor.fetchall()
                print(data)
                # 이 데이터로 그래프 만들기

            else:
                cursor.execute("SELECT code FROM stock_code.kosdaq WHERE name = \'" + search_word + "\';")
                code = cursor.fetchall()[0][0]
                print(code)
                cursor.execute("SELECT date, price FROM daily_price.kosdaq WHERE code = \'" + code + "\' ORDER BY date ASC;")
                data = cursor.fetchall()
                print(data)
                # 이 데이터로 그래프 만들기

            datalist = []
            test_data = {}
            i=0
            for today in data:
                if(today[0] != ''):
                    temp = {}
                    temp['time'] = today[0]
                    temp['price'] = today[1]
                    datalist.append(temp)
                    test_data["" + str(i)] = (json.dumps(temp, ensure_ascii=False))
                    i+=1
            print(test_data)
            print(type(test_data))
            json_data = json.dumps(datalist, ensure_ascii=False)
            json_test_data = {'test_data': test_data}
            stock_data = {'json_data': json_data}
            raw_data = {'raw_data': data}
            return render(request, 'invest/chart_result.html', json_test_data)


        except Exception as e:
            print("error")
            print(e)
            return HttpResponse("db connect failed")

    else:
        return HttpResponse("잘못된 기업명입니다.")

def info(request):
    return render(request, 'invest/info.html')

def info_result(request):
    if request.method == 'POST':
        search_word = request.POST['searched']
        print(search_word)

        try:
            conn = psycopg2.connect(conn_string)
            print("connect info_result")

            cursor = conn.cursor()

            cursor.execute("SELECT count(*) FROM stock_code.kospi WHERE name = \'" + search_word + "\';")
            isKospi = cursor.fetchall()[0][0]  # 코스피에 없으면 코스닥에 있겠지?

            cursor.execute("SELECT count(*) FROM stock_code.kosdaq WHERE name = \'" + search_word + "\';")
            isKosdaq = cursor.fetchall()[0][0]

            cursor.execute("SELECT count(*) FROM stock_code.ETF WHERE name = \'" + search_word + "\';")
            isETF = cursor.fetchall()[0][0]

            print(isKospi, isKosdaq, isETF)
            if isKospi == 1:
                cursor.execute("SELECT code FROM stock_code.kospi WHERE name = \'" + search_word + "\';")
                code = cursor.fetchall()[0][0]
                print(code)
                cursor.execute(
                    "SELECT market, sales, profit FROM basic_info.kospi WHERE code = \'" + code + "\';")
                data = cursor.fetchall()
                print(data)
                print(type(data))

            elif isKosdaq == 1:
                cursor.execute("SELECT code FROM stock_code.kosdaq WHERE name = \'" + search_word + "\';")
                code = cursor.fetchall()[0][0]
                print(code)
                cursor.execute(
                    "SELECT market, sales, profit FROM basic_info.kosdaq WHERE code = \'" + code + "\';")
                data = cursor.fetchall()
                print(data)
                print(type(data))

            elif isETF == 1:
                return render(request, 'invest/info.html')

            market = data[0][0]
            sales = data[0][1]
            profit = data[0][2]

            print(market, sales, profit)

            info_data = {'market':market, 'sales':sales, 'profit':profit}

            return render(request, 'invest/info_result.html', info_data)


        except Exception as e:
            print("error")
            print(e)
            return HttpResponse("db connect failed")

    else:
        return HttpResponse("잘못된 기업명입니다.")

def memo(request):
    memo_list = Memo.objects.order_by('-create_date')
    context = {'memo_list': memo_list}
    return render(request, 'invest/memo_title.html', context)

def memo_content(request, memo_id):
    memo = get_object_or_404(Memo, pk = memo_id)
    context = {'memo': memo}
    return render(request, 'invest/memo_content.html', context)

def memo_create(request):
    if request.method == 'POST':
        form = MemoForm(request.POST)
        if form.is_valid():
            memo = form.save(commit=False)
            memo.create_date = timezone.now()
            memo.save()
            return redirect('invest:memo')
    else:
        form = MemoForm()
    context = {'form':form}
    return render(request, 'invest/memo_form.html', context)
