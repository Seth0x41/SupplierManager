from unicodedata import decimal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import sqlite3
from numpy import double, logical_and
from pymysql import NULL
import secrets
import pandas as pd
Generated_code = secrets.randbelow(5000000)
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
        self.Generated_Code_label.setText(str(Generated_code))
        print(str(secrets.randbelow(5000000)))
        self.supplier_overview_table()
        self.overview_table()
        self.fetch_wating_product_taple()
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
        self.Push_Button_Recive_Product.clicked.connect(self.receive_product)
        self.Wating_Products_fetch_data_pushButton.clicked.connect(self.fetch_spacific_product_taple)
        self.pushButtondeloperation_3.clicked.connect(self.delete_operation)
        self.pushButtondeleteSupplierName_4.clicked.connect(self.delete_supplier)
        self.pushButtondeleteproductName_5.clicked.connect(self.delete_product)

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

            # calling affected functions
            self.supplier_overview_table()
            self.fetch_suppliers_names()

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

            # calling affected functions
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
            if fetched_amount >= amount and amount >= 0:
                self.cur.execute(f"INSERT INTO operation(remain,quantity,products_id,supplierID,operation_code) VALUES(?,?,?,?,?)",(operation_price,quantity,fetched_product_id,fetched_supplier_id,operation_code))
                self.cur.execute(f'''UPDATE supplier SET prepaid ='{amount}'  WHERE supplier.name='{supplier_name}' ''')            
                history_statment = f"تم اضافة {quantity} عنصر جديد من المورد {supplier_name} بقيمة {'{:,}'.format(operation_price)}"
                self.cur.execute('''
                INSERT INTO operations_history(Action) VALUES(?)
                    ''',(history_statment,))        
                self.db.commit()
                QMessageBox.about(self, "نجاح العملية", "تم إضافة المنتج")

                # Calling affected Functions
                self.supplier_overview_table()
                self.overview_table()
            else:
                QMessageBox.about(self, "Error Message", "الكمية المطلوبة أكبر من المبلغ المتوفر")
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])

    def receive_product(self):
        product_name= self.recive_Product_comboBox.currentText()
        if self.OperationCode_EditLine.text().strip() != '':
            operation_code= self.OperationCode_EditLine.text()
        else:
            operation_code= None 
        if self.Recived_Quantity_EditLine.text().strip() != '':
            recived_quantity= int(self.Recived_Quantity_EditLine.text())
        else:
            recived_quantity= None
        try:
            self.cur.execute(f'''SELECT product.price FROM operation,product WHERE operation.operation_code ='{operation_code}' and product.id = operation.products_id ;''')
            fetched_data = self.cur.fetchone()
            print(fetched_data)
            fetched_product_price=int(fetched_data[0])

            recieved_amount = recived_quantity * fetched_product_price 
            print(recieved_amount)
            self.cur.execute('''UPDATE operation SET remain = remain-?,delivered = delivered +?  WHERE operation_code = ?;
                    ''',(recieved_amount,recived_quantity,operation_code))
            history_statment = f"تم استلام {recived_quantity} عنصر من العملية رقم {operation_code}"

            self.cur.execute('''UPDATE operation SET status = 1 WHERE quantity = delivered and operation_code = ?;
            ''',(operation_code,))
            self.cur.execute('''DELETE FROM operation WHERE status = 1 and quantity = delivered  and operation_code = ?;
            ''',(operation_code,))

            self.cur.execute('''INSERT INTO operations_history(Action) VALUES(?);

            ''',(history_statment,))
            self.db.commit()
            QMessageBox.about(self, "نجاح العملية", "تم تأكيد الاستلام")

            # Calling affected functions
            self.overview_table()
            self.supplier_overview_table()
        except Exception as Error_message:
            if Error_message.args[0] == "'NoneType' object is not subscriptable":
                QMessageBox.about(self, "Error Message", "لا توجد عملية بهذا الرقم")
            else:
               QMessageBox.about(self, "Error Message", Error_message.args[0])           
    # Fetching data section

    def fetch_products_names(self):
        self.listWidgetProducts.clear()
        self.recive_Product_comboBox.clear()
        self.deleteproductNamecomboBox_3.clear()
        self.Wating_product_name_comboBox.clear()
        try:
            self.cur.execute('''SELECT product_name FROM product ''')
            products_names=self.cur.fetchall()
            for name in products_names:
                self.listWidgetProducts.addItem(str(name[0]))
                self.recive_Product_comboBox.addItem(str(name[0]))
                self.deleteproductNamecomboBox_3.addItem(str(name[0]))
                self.Wating_product_name_comboBox.addItem(str(name[0]))
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])

    def fetch_suppliers_names(self):
        self.New_Operation_Supplier_Name.clear()
        self.deleteSupplierNamecomboBox_2.clear()
        try:
            self.cur.execute('''SELECT name FROM supplier''')
            suppliers_names=self.cur.fetchall()
            for name in suppliers_names:
                self.New_Operation_Supplier_Name.addItem(str(name[0]))
                self.deleteSupplierNamecomboBox_2.addItem(str(name[0]))
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
    def overview_table(self):
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        try:
            sql_quary='''
    SELECT count(*) From (select distinct name From supplier, product, operation 
    WHERE  supplier.id=operation.supplierID and product.id = operation.products_id);
    '''       
            self.cur.execute(sql_quary,)
            counted_fetched_data = self.cur.fetchone()
            numbers_of_rows =  counted_fetched_data[0]
            self.tableWidget.setRowCount(numbers_of_rows)

            sql_select_quary=f'''
    Select name, country,sum(operation.quantity),sum(operation.delivered),sum(operation.quantity)-sum(operation.delivered),sum(operation.remain),supplier.prepaid,supplier.description AS total
    From supplier, product, operation 
    where  supplier.id=operation.supplierID and product.id = operation.products_id group by name'''     
            tablerow=0
            for row in self.cur.execute(sql_select_quary):
                self.tableWidget.setItem(tablerow,0,QTableWidgetItem(row[0]))
                self.tableWidget.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(tablerow,2,QTableWidgetItem(str(row[2])))
                self.tableWidget.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(tablerow,4,QTableWidgetItem(str(row[4])))
                self.tableWidget.setItem(tablerow,5,QTableWidgetItem('{:,}'.format(row[5])))
                self.tableWidget.setItem(tablerow,6,QTableWidgetItem('{:,}'.format(row[6])))
                self.tableWidget.setItem(tablerow,7 ,QTableWidgetItem(str(row[7])))
                tablerow+=1
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])


    def fetch_wating_product_taple(self):
        header = self.wating_product_taple.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        try:
            count_sql_quary='''
    select count(name) From supplier, product, operation where 
    supplier.id=operation.supplierID and operation.Status = 0 and operation.products_id = product.id and operation.supplierID = supplier.id'''        
            self.cur.execute(count_sql_quary,)
            fetched_data = self.cur.fetchone()
            number_of_rows =  fetched_data[0]
            self.wating_product_taple.setRowCount(number_of_rows)

            select_sql_quary=f'''
    select name, product_name, quantity, delivered,operation_code From supplier, product, operation where 
    supplier.id=operation.supplierID and operation.Status = 0 and operation.products_id = product.id and operation.supplierID = supplier.id '''     
            tablerow=0
            for row in self.cur.execute(select_sql_quary):
                self.wating_product_taple.setItem(tablerow,0,QTableWidgetItem(row[0]))
                self.wating_product_taple.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                self.wating_product_taple.setItem(tablerow,2,QTableWidgetItem(str(row[2])))
                self.wating_product_taple.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
                self.wating_product_taple.setItem(tablerow,4,QTableWidgetItem(str(row[4])))
                tablerow+=1
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])

    def fetch_spacific_product_taple(self):
        
        header = self.Wating_Spacific_product_taple.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        product_name=self.Wating_product_name_comboBox.currentText()
        try:
            count_sql_quary=f'''
    select count(*) From (select distinct name From supplier, product, operation 
    WHERE product.product_name ='{product_name}' and supplier.id=operation.supplierID and product.id = operation.products_id)'''
            self.cur.execute(count_sql_quary,)
            fetched_data = self.cur.fetchone()
            number_of_rows =  fetched_data[0]
            self.Wating_Spacific_product_taple.setRowCount(number_of_rows)

            sql_quary=f'''
    Select name, sum(operation.quantity),sum(operation.remain) AS total,date,price,type
    From supplier, product, operation 
    where product.product_name='{product_name}' and supplier.id=operation.supplierID and product.id = operation.products_id group by name;   '''
            tablerow=0
            for row in self.cur.execute(sql_quary):
                self.Wating_Spacific_product_taple.setItem(tablerow,0,QTableWidgetItem(row[0]))
                self.Wating_Spacific_product_taple.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                self.Wating_Spacific_product_taple.setItem(tablerow,2,QTableWidgetItem('{:,}'.format(row[2])))
                self.Wating_Spacific_product_taple.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
                self.Wating_Spacific_product_taple.setItem(tablerow,4,QTableWidgetItem(str(row[4])))
                self.Wating_Spacific_product_taple.setItem(tablerow,5,QTableWidgetItem(str(row[5])))
                tablerow+=1
        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])


    # Edit Section

    def edit_product_price(self):
        product_name= self.EditProductcomboBox.currentText()
        if self.EditProducgtPricecomboBox.text() != '':
            product_price=int(self.EditProducgtPricecomboBox.text())#coverted
        else:
            product_price= None
        try:
            sql_quary=f'''UPDATE product SET price={product_price} WHERE product_name='{product_name}'
            '''
            self.cur.execute(sql_quary,)
            history_statment = f"تم تعديل سعر المنتج {product_name} وسعره الجديد هو {product_price}"
            self.cur.execute('''
            INSERT INTO operations_history(Action) VALUES(?)
                ''',(history_statment,))
            self.db.commit()
            # calling affected functions
        except Exception as e:
            if e.args[0] == "no such column: None":
                QMessageBox.about(self, "Error Message", "الرجاء إدخال سعر المنتج ")
            else:
                QMessageBox.about(self, "Error Message", e.args[0])


    def edit_supplier(self):
        if self.EditSupplierNamecomboBox.currentText().strip() != '':
            supplier_name=self.EditSupplierNamecomboBox.currentText()
        else:
            supplier_name = None
        try:
            if self.lineEdit_5.text().strip() != '':
                initial_amount=int(self.lineEdit_5.text())
                self.cur.execute(f'''
                UPDATE supplier SET prepaid = {initial_amount} where name='{supplier_name}'
                    ''',())
                history_statment = f"تم تعديل القيمة المبدئية للمورد {supplier_name} والقيمة الجديدة هى {initial_amount}"
                self.cur.execute('''
                INSERT INTO operations_history(Action) VALUES(?)
                    ''',(history_statment,))
            if self.countrynamecombobox_2.currentText().strip() != '':
                country=self.countrynamecombobox_2.currentText()
                self.cur.execute(f'''
                UPDATE supplier SET country = '{country}' where name='{supplier_name}'
                    ''',())
                history_statment = f"تم تعديل  بلد المورد {supplier_name} والقيمة الجديدة هى {country}"
                self.cur.execute('''
                INSERT INTO operations_history(Action) VALUES(?)
                    ''',(history_statment,))
            if self.textEdit_2.toPlainText().strip() != '':
                supplier_description=self.textEdit_2.toPlainText()
                self.cur.execute(f'''
                UPDATE  supplier SET description = '{supplier_description}' where name='{supplier_name}'
                    ''',())
                history_statment = f"تم تعديل  وصف المورد {supplier_name} والقيمة الجديدة هى {supplier_description}"
                self.cur.execute('''
                INSERT INTO operations_history(Action) VALUES(?)
                    ''',(history_statment,))
            if self.lineEdit_4.text().strip() != '':
                new_name=self.lineEdit_4.text()
                self.cur.execute(f'''
                    UPDATE supplier SET name = '{new_name}' where name='{supplier_name}'
                        ''',())
            self.db.commit()
            QMessageBox.about(self, "عملية ناجحة.", "تم تحديث البيانات")

            # calling affected functions
            self.supplier_overview_table()
            self.fetch_suppliers_names()
            self.overview_table()

        except Exception as Error_message:
            QMessageBox.about(self, "Error Message", Error_message.args[0])



    # Delete Section

    def delete_operation(self):
        try:
            if self.lineEdit.text().strip() == str(Generated_code):
                if self.OperationCodeEditLine_4.text().strip() != '':
                    operation_code = int(self.OperationCodeEditLine_4.text())
                    self.cur.execute('''
SELECT remain, supplierID from operation where operation_code = ?      ''',(operation_code,))

                    fetched_data = self.cur.fetchone()
                    amount= int(fetched_data[0])
                    supplier_id = fetched_data[1]
                    self.cur.execute(f'''
UPDATE supplier SET prepaid= prepaid+{amount}  where id= '{supplier_id}'    ''',())         

                    self.cur.execute('''
                    DELETE FROM operation WHERE operation_code = ?
                    ''',(operation_code,))
                    QMessageBox.about(self, "عملية ناجحة.", "تم حذف العملية") 
                    history_statment = f"تم حذف العملية رقم {operation_code}"
                    self.cur.execute('''
                    INSERT INTO operations_history(Action) VALUES(?)
                        ''',(history_statment,))
                else:
                    operation_code = None
                self.db.commit()
            else:
                QMessageBox.about(self, "خطأ", "الرجاء إدخال كود التأكيد بطريقة صحيحة  ")
        except Exception as e:
              QMessageBox.about(self, "Error Message", e.args[0]) 

        #calling affected functions

        self.fetch_wating_product_taple()
        self.overview_table()
        self.supplier_overview_table()

    def delete_supplier(self):
            try:
                if self.lineEdit.text().strip() == str(Generated_code):
                    
                    if self.deleteSupplierNamecomboBox_2.currentText().strip() != '':
                        supplierName = self.deleteSupplierNamecomboBox_2.currentText()
                        self.cur.execute('''
                        DELETE FROM supplier WHERE name = ?
                        ''',(supplierName,))
                        QMessageBox.about(self, "عملية ناجحة.", "تم حذف المورد") 
                        HistoryInsertion = f"تم حذف المورد {supplierName}"
                        self.cur.execute('''
                        INSERT INTO operations_history(Action) VALUES(?)
                            ''',(HistoryInsertion,))
                    else:
                        supplierName: None
                    self.db.commit()
                else:
                    QMessageBox.about(self, "خطأ", "الرجاء إدخال كود التأكيد بطريقة صحيحة  ")
                self.fetch_suppliers_names()
                self.overview_table()
                self.supplier_overview_table()
            except Exception as Error_message:
                QMessageBox.about(self, "Error Message", Error_message.args[0])
    def delete_product(self):
        try:
            if self.lineEdit.text().strip() == str(Generated_code):
                if self.deleteproductNamecomboBox_3.currentText().strip() != '':
                    productname = self.deleteproductNamecomboBox_3.currentText()
                    self.cur.execute('''
                    DELETE FROM product WHERE product_name = ?
                    ''',(productname,))
                    QMessageBox.about(self, "عملية ناجحة.", "تم حذف المنتج") 
                    HistoryInsertion = f"تم حذف المنتج {productname}"
                    self.cur.execute('''
                    INSERT INTO operations_history(Action) VALUES(?)
                        ''',(HistoryInsertion,))
                else:
                    productname = None
                self.db.commit()
            else:
                QMessageBox.about(self, "خطأ", "الرجاء إدخال كود التأكيد بطريقة صحيحة  ")
            self.fetch_products_names()
            self.overview_table()
            self.supplier_overview_table()
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




# To do list:
# 1 - Edit delete and edit logic
# when you edit or delete operation, you must change the amount of user .
