from unicodedata import decimal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import sqlite3
from numpy import double
from pymysql import NULL
import secrets
import pandas as pd

# from App_DB import Supplier
ui,_ = loadUiType('mainwindow.ui')
class MainApp(QMainWindow , ui):
    def __init__(self , parent=None):
        super(MainApp , self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.UI_changes()
        self.db_connection()
        self.buttons_handling()
        self.fetch_products_names()
        self.fetch_suppliers_names()
        self.fetch_history_table()
        self.label_40.setText(str(secrets.randbelow(5000000)))

    def UI_changes(self):
        self.tabWidget.tabBar().setVisible(False)
    
    def db_connection(self):
        self.db = sqlite3.connect('database.db')
        self.cur = self.db.cursor()
        print("Database Connected!")


    def buttons_handling(self):
        self.OverviewTap.clicked.connect(self.open_overview_tap)
        self.AddingTap.clicked.connect(self.open_adding_tap)
        self.RepoTap.clicked.connect(self.open_repo_tap)
        self.HistoryTap.clicked.connect(self.open_history_tap)
        self.ReceivingTap.clicked.connect(self.open_reciving_tap)
        self.ManageTap.clicked.connect(self.open_manage_tap)
        self.Add_New_Supllier_PushButton.clicked.connect(self.add_new_supplier)
        self.Add_New_Product_PushButton.clicked.connect(self.add_new_product)
        self.Add_New_Operation_pushButton.clicked.connect(self.add_new_operation)



    # Adding Section
    def add_new_supplier(self):
        if self.AddSupplier_SupplierName.text().strip() != '':
             supplier_name= self.AddSupplier_SupplierName.text()
        else:
            supplier_name= None
        supplier_country= self.AddSupplier_CountryName.currentText()
        supplier_description=self.AddSupplier_Description.toPlainText()

        if self.AddSupplier_InitialAmount.text().strip() != '':
            initial_amount =int(self.AddSupplier_InitialAmount.text())
        else:
            initial_amount = None
        try:
            self.cur.execute(f"""INSERT INTO supplier(name,country,description,prepaid) VALUES(?,?,?,?  )""",(supplier_name,supplier_country,supplier_description,initial_amount))
            history_satament = f"تم اضافة مورد جديد{supplier_name} بمبلغ مبدأى قدره {initial_amount}"
            self.cur.execute(''' INSERT INTO operations_history(Action) VALUES(?) ''',(history_satament,))
            self.db.commit()
            QMessageBox.about(self, "عملية ناجحة", "تم إضافة المورد بنجاح")
            # self.SuppliersOverview()
            self.fetch_suppliers_names()
            # self.HistoryTable

        except Exception as Error_message:
            if Error_message.args[0] == "NOT NULL constraint failed: supplier.name":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال اسم المورد")
            elif Error_message.args[0] == "NOT NULL constraint failed: supplier.country":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال اسم البلد")
            else:
                QMessageBox.about(self, "Error Message", Error_message.args[0])


    def add_new_product(self):
        if self.AddProduct_ProductName.text().strip() != '':
            product_name= self.AddProduct_ProductName.text()
        else:
            product_name= None
        if self.AddProduct_ProductPrice.text().strip() != '':
            product_price= int(self.AddProduct_ProductPrice.text())
        else:
            product_price= None

        product_type= self.AddProduct_ProductType.currentText()

        try:
            self.cur.execute(f"INSERT INTO product(product_name,type,price) VALUES(?,?,?)",(product_name,product_type,product_price,))
            history_satament = f"تم اضافة منتج جديد {product_name} قيمته {product_price}"
            self.cur.execute('''INSERT INTO operations_history(Action) VALUES(?)''',(history_satament,))            
            self.db.commit()
            QMessageBox.about(self, "نجاح العملية", "تم إضافة المنتج")

            self.fetch_products_names()

        except Exception as Error_message:
            if Error_message.args[0] == "UNIQUE constraint failed: product.product_name":
                QMessageBox.about(self, "Error Message", "المنتج موجود بالفعل.")
            elif Error_message.args[0] == "NOT NULL constraint failed: product.type":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال نوع المنتج")
            elif Error_message.args[0] == "NOT NULL constraint failed: product.price":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال سعر المنتج")
            elif Error_message.args[0] == "NOT NULL constraint failed: product.product_name":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال اسم المنتج")
            else:
                QMessageBox.about(self, "Error Message", Error_message.args[0])

    def add_new_operation(self):
        supplier_name = self.New_Operation_Supplier_Name.currentText()
        if self.New_Operation_Quantuty.text().strip() != '':
            quantity = int(self.New_Operation_Quantuty.text())
        else:
            quantity = None
        product_name = [item.text() for item in self.listWidgetProducts.selectedItems()][0]
        # fetch supplier amount and product price 
        sql_quary= f'''SELECT supplier.prepaid, product.price,product.id,supplier.id FROM supplier,product where product.product_name='{product_name}' and supplier.name='{supplier_name}'; '''
        self.cur.execute(sql_quary,())
        fetched_data = self.cur.fetchone()
        fetched_amount = int(fetched_data[0])
        fetched_product_price = fetched_data[1]
        fetched_product_id=fetched_data[2]
        fetched_supplier_id=fetched_data[3]
        operation_price= quantity* fetched_product_price
        operation_code= secrets.randbelow(5000000)
        amount= fetched_amount - operation_price
        try:
            if fetched_amount >= amount:
                self.cur.execute(f"INSERT INTO operation(remain,quantity,products_id,supplierID,operation_code) VALUES(?,?,?,?,?)",(amount,quantity,fetched_product_id,fetched_supplier_id,operation_code))
                self.cur.execute(f'''update supplier SET prepaid ='{amount}'  WHERE supplier.name='{supplier_name}' ''')            
                history_statment = f"تم اضافة {quantity} عنصر جديد من المورد {supplier_name} بقيمة {'{:,}'.format(amount)}"
                self.cur.execute('''
                INSERT INTO operations_history(Action) VALUES(?)
                    ''',(history_statment,))        
                self.db.commit()
                QMessageBox.about(self, "نجاح العملية", "تم إضافة المنتج")
        except Exception as Error_message:
            if Error_message.args[0] == "CHECK constraint failed: remain >= 0":
                QMessageBox.about(self, "Error Message", "الكمية المطلوبة أكبر من المبلغ المتوفر")
            else:
               QMessageBox.about(self, "Error Message", Error_message)           
    # Fetching data section

    def fetch_products_names(self):
        self.listWidgetProducts.clear()
        try:
            self.cur.execute('''SELECT product_name FROM product ''')
            products_names=self.cur.fetchall()
            for name in products_names:
                self.listWidgetProducts.addItem(str(name[0]))
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])

    def fetch_suppliers_names(self):
        self.New_Operation_Supplier_Name.clear()
        try:
            self.cur.execute('''SELECT name FROM supplier''')
            suppliers_names=self.cur.fetchall()
            for name in suppliers_names:
                self.New_Operation_Supplier_Name.addItem(str(name[0]))
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])
            
    def fetch_countries_names(self):
        self.countrynamecombobox.clear()
        try:
            self.cur.execute('''SELECT country_name FROM currency''')
            country_name=self.cur.fetchall()

            for name in country_name:
                self.countrynamecombobox.addItem(str(name[0]))
                self.countrynamecombobox_2.addItem(str(name[0]))
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])        


    def fetch_history_table(self):
        header = self.history_tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        try:
            conunt_sql_quary='''SELECT count("Action") FROM operations_history'''
            self.cur.execute(conunt_sql_quary,)
            fetched_data = self.cur.fetchone()
            number_of_rows =  fetched_data[0]
            self.history_tableWidget.setRowCount(number_of_rows)

            sql_quary=f'''SELECT date, Action From operations_history'''     
            tablerow=0
            for row in self.cur.execute(sql_quary):
                print(row)
                self.history_tableWidget.setItem(tablerow,0,QTableWidgetItem(row[0]))
                self.history_tableWidget.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                tablerow+=1
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])    

    def supplier_overview_table(self):
        header = self.Suppliers_information_tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        try:
            count_sql_quary='''SELECT count(*) From (select name,country,prepaid,description from supplier); '''       
            self.cur.execute(count_sql_quary,)
            fetched_data = self.cur.fetchone()
            number_of_rows =  fetched_data[0]
            self.Suppliers_information_tableWidget.setRowCount(number_of_rows)

            sql_quary=f'''SELECT name,country,prepaid,description from supplier'''     
            tablerow=0
            for row in self.cur.execute(sql_quary):
                print(row)
                self.Suppliers_information_tableWidget.setItem(tablerow,0,QTableWidgetItem(str(row[0])))
                self.Suppliers_information_tableWidget.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                self.Suppliers_information_tableWidget.setItem(tablerow,2,QTableWidgetItem('{:,}'.format(row[2])))
                self.Suppliers_information_tableWidget.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
                tablerow+=1

            total_price='''Select sum(prepaid) from supplier;''' 
            self.cur.execute(total_price,)
            fetched_total_price = self.cur.fetchone()
            total_price=fetched_total_price[0]
            if total_price:
                self.total_price_label.setText('{:,}'.format(total_price)+' EGP')
            else:
                pass
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])  



#         Handling UI Section

    def open_overview_tap(self):
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_4.setCurrentIndex(0)
    def open_adding_tap(self):
        self.tabWidget.setCurrentIndex(3) 
        self.tabWidget_3.setCurrentIndex(0)

    def open_repo_tap(self):
        self.tabWidget.setCurrentIndex(1)
    def open_history_tap(self):
        self.tabWidget.setCurrentIndex(2)
    def open_reciving_tap(self):
        self.tabWidget.setCurrentIndex(4)
    def open_manage_tap(self):
        self.tabWidget.setCurrentIndex(5)
        self.tabWidget_2.setCurrentIndex(0)



def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
