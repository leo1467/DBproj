# -*- coding: utf-8 -*-

#程式碼是從這邊修改的 https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
#原本是空白的http server，改寫do_GET區塊加入自定義頁面

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
import sqlite3


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
            #這邊要填訂單狀況查詢的結果
            f = open('subpage1.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
        elif path == '/2':
            # f = open('subpage2.html', encoding='UTF-8')
            # subPage = f.read()
            # f.close()
            subPage = "銷售額查詢 頁面未建立"
        elif path == '/3':
            f = open('subpage3.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
            # subPage = "客戶別銷售排名查詢 頁面未建立"
        elif path == '/4':
            f = open('subpage4.html', encoding='UTF-8')
            subPage = f.read()
            f.close()
            # subPage = "產品別銷量查詢 頁面未建立"
        elif path == '/5':
            subPage = "地區別銷量查詢 頁面未建立"
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
                print(sqlstr)
                res = c.execute(sqlstr)
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
                
                print(subPage)
                conn.commit()
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
                conn.commit()
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
                SELECT RANK() over(ORDER BY SUM(orderdetails.quantityOrdered) DESC), orderdetails.productCode, products.productName , SUM(orderdetails.quantityOrdered) AS productAmount
                FROM orders JOIN orderdetails, products
                WHERE orders.orderDate >= '%s' AND orders.orderDate <= '%s' AND orders.orderNumber = orderdetails.orderNumber AND products.productCode = orderdetails.productCode
                GROUP BY orderdetails.productCode
                """ % (start_date, end_date)
                print(sqlstr)
                
                res = c.execute(sqlstr)
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
                conn.commit()
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
        httpd.serve_forever()
        print("Start server")
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stop server')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()