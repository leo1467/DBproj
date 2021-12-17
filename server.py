# -*- coding: utf-8 -*-

#程式碼是從這邊修改的 https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
#原本是空白的http server，改寫do_GET區塊加入自定義頁面

from sys import argv as argv
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
import sqlite3

import matplotlib.pyplot as plt #畫圖表用，直接matplot畫好圖，包成base64傳出去
import io
import base64

dbPath = "db/data.sqlite"

class Server(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print("get: %s" % self.path)
        
        #載入主頁
        f = open('index.html', encoding='UTF-8')
        page = f.read()
        f.close()
        
        # /action_page.php?fname=1223
        #urlPaths = self.path.split("?")
        #urlPath = urlPaths[0]
        getPath = urlparse(self.path)
        
        #scheme='', netloc='', path='/action_page.php', params='', query='fname=123', fragment=''
        path = getPath.path
        
        print(getPath)
            
        
        subPage = ""
        if path == '/1':
            #訂單狀況查詢
            f = open('subpage1.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
        elif path == '/2':
            #銷售額查詢
            f = open('subpage2.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
        elif path == '/3':
            #客戶別銷售排名查詢
            f = open('subpage3.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
            # subPage = "客戶別銷售排名查詢 頁面未建立"
        elif path == '/4':
            #產品別銷量查詢
            f = open('subpage4.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
            # subPage = "產品別銷量查詢 頁面未建立"
        elif path == '/5':
            #國家別銷量查詢
            f = open('subpage5.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
        elif path == '/action1':
            #訂單查詢，回傳結果
            qArgs = parse_qs(getPath.query)
            print(qArgs)
            if "order_no" in qArgs:
                order_no = qArgs["order_no"][0]
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                sqlstr = """
                SELECT orders.orderNumber, orderdetails.productCode, orders.orderDate, orders.status
                FROM orders, orderdetails
                WHERE orders.orderNumber='%s'
                AND orders.orderNumber = orderdetails.orderNumber
                """ % (order_no)
                #print(sqlstr)
                res = c.execute(sqlstr)
                conn.commit()
                subPage = "<table>"
                
                subPage += "<tr>"
                subPage += "<th>訂單號碼</th> <th>產品編號</th> <th>訂購日期</th> <th>出貨狀況</th>"
                subPage += "</tr>"
                for row in res:
                    subPage += "<tr>"
                    for tar in row:
                        subPage += "<td>"
                        subPage += tar
                        subPage += "</td>"
                    subPage += "</tr>"    
                
                subPage += "</table>"
                
                #print(subPage)
                
                conn.close()
        elif path == '/action2':
            #訂單查詢，回傳結果
            qArgs = parse_qs(getPath.query)
            print(qArgs)
            if "year" in qArgs:
                year = qArgs["year"][0]
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                sqlstr = """
                SELECT strftime("%%m", orders.orderDate) as 'month',
                CAST(SUM(orderdetails.priceEach * orderdetails.quantityOrdered) as INT) as Income
                FROM orders, orderdetails
                WHERE orders.orderNumber = orderdetails.orderNumber
                AND strftime("%%Y", orders.orderDate) = '%s'
                GROUP BY strftime("%%m", orders.orderDate)
                ORDER BY 'month' ASC
                """ % (year)
                res = c.execute(sqlstr)
                conn.commit()
                
                x = []
                y = []
                for row in res:
                    x.append(row[0])
                    y.append(row[1] / 1000)
                plt.figure(figsize=(12,8))
                plt.title("%s year" % year)
                plt.plot(x, y, label="Income(thousand)")
                plt.xlabel('Month')
                plt.legend()
                #plt.show()
                #plt 轉 base64 參照 https://stackoverflow.com/questions/38061267/matplotlib-graphic-image-to-base64
                pic_IObytes = io.BytesIO()
                plt.savefig(pic_IObytes,  format='jpg')
                pic_IObytes.seek(0)
                pic_hash = base64.b64encode(pic_IObytes.read()).decode("utf-8").replace("\n", "")
                
                
                subPage = "<img src=\"data:image/jpeg;base64, " + str(pic_hash) + "\" />"
                
                conn.close()
        elif path == '/action3':
            qArgs = parse_qs(getPath.query)
            print(qArgs)
            if "start_date" in qArgs and "end_date" in qArgs:
                start_date = qArgs["start_date"][0]
                end_date = qArgs["end_date"][0]
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                sqlstr = """ 
                SELECT RANK() over(ORDER BY b.totalPrice DESC), customers.customerName, customers.customerNumber, b.totalPrice
                FROM customers, (SELECT orders.customerNumber, orders.orderNumber, orders.orderDate, a.totalPrice
                FROM orders NATURAL JOIN (SELECT orderdetails.orderNumber, sum(orderdetails.priceEach*orderdetails.quantityOrdered) AS totalPrice
                FROM orderdetails
                GROUP BY orderdetails.orderNumber) AS a
                WHERE orders.orderDate >= '%s' AND orders.orderDate <= '%s') AS b
                WHERE customers.customerNumber = b.customerNumber
                """ % (start_date, end_date)
                print(sqlstr)
                
                res = c.execute(sqlstr)
                conn.commit()
                subPage = "<table>"
                subPage += "<tr>"
                subPage += "<th>金額排名</th> <th>公司名稱</th> <th>顧客編號</th> <th>總金額</th>"
                subPage += "</tr>"
                for row in res:
                    subPage += "<tr>"
                    for tar in row:
                        subPage += "<td>"
                        if type(tar) == float:
                            tar = round(tar, 2)
                        subPage += str(tar)
                        subPage += "</td>"
                    subPage += "</tr>"    
                
                subPage += "</table>"
                
                print(subPage)
                conn.close()
        elif path == '/action4':
            qArgs = parse_qs(getPath.query)
            print(qArgs)
            if "start_date" in qArgs and "end_date" in qArgs:
                start_date = qArgs["start_date"][0]
                end_date = qArgs["end_date"][0]
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                sqlstr = """ 
                SELECT RANK() 
                over(ORDER BY SUM(orderdetails.quantityOrdered) DESC), orderdetails.productCode, products.productName , SUM(orderdetails.quantityOrdered) AS productAmount
                FROM orders JOIN orderdetails, products
                WHERE orders.orderDate >= '%s' AND orders.orderDate <= '%s' AND orders.orderNumber = orderdetails.orderNumber AND products.productCode = orderdetails.productCode
                GROUP BY orderdetails.productCode
                """ % (start_date, end_date)
                print(sqlstr)
                
                res = c.execute(sqlstr)
                conn.commit()
                subPage = "<table>"
                subPage += "<tr>"
                subPage += "<th>數量排名</th> <th>產品編號</th> <th>產品名稱</th> <th>銷售量</th>"
                subPage += "</tr>"
                for row in res:
                    subPage += "<tr>"
                    for tar in row:
                        subPage += "<td>"
                        subPage += str(tar)
                        subPage += "</td>"
                    subPage += "</tr>"    
                
                subPage += "</table>"
                
                print(subPage)
                conn.close()
        elif path == '/action5':
            qArgs = parse_qs(getPath.query)
            print(qArgs)
            if "start_date" in qArgs and "end_date" in qArgs:
                start_date = qArgs["start_date"][0]
                end_date = qArgs["end_date"][0]
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                sqlstr = """ 
                SELECT RANK() 
                over(ORDER BY SUM(orderdetails.quantityOrdered) DESC) AS CountrySalesRank, customers.country, SUM(orderdetails.quantityOrdered) AS productAmount
                FROM orders 
                LEFT JOIN orderdetails ON orders.orderNumber = orderdetails.orderNumber
                LEFT JOIN customers ON orders.customerNumber = customers.customerNumber
                WHERE orders.orderDate >= '%s' AND orders.orderDate <= '%s'
                GROUP BY customers.country;
                """ % (start_date, end_date)
                print(sqlstr)

                res = c.execute(sqlstr)
                conn.commit()
                subPage = "<table>"
                subPage += "<tr>"
                subPage += "<th>國家銷售量排名</th> <th>國家名稱</th> <th>總銷售量</th>"
                subPage += "</tr>"
                for row in res:
                    subPage += "<tr>"
                    for tar in row:
                        subPage += "<td>"
                        subPage += str(tar)
                        subPage += "</td>"
                    subPage += "</tr>"

                subPage += "</table>"

                print(subPage)
                conn.close()

        page = page.replace("%sub_page%", subPage)

        
        self._set_response()
        self.wfile.write(page.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Server, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        print("Start server")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stop server')

if __name__ == '__main__':
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()