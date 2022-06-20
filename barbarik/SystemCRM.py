import SQLiteData
from GUI.UiInterface import UiInterface
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from asyncqt import asyncSlot
import openpyxl


def singleton(ui_class):
    instances = {}

    def getinstance(*args, **kwargs):
        if ui_class not in instances:
            instances[ui_class] = ui_class(*args, **kwargs)
        return instances[ui_class]

    return getinstance


@singleton
class SystemCRM(QMainWindow):
    def __init__(self):
        super().__init__()
        self.type_btn = None
        self.suppliers_dict = {}
        self.ui = UiInterface(self)
        self.db = SQLiteData.ex
        self.new_row_warning = True
        self.delete_all_warning = False
        self.async_init()
        self.show()

    @asyncSlot()
    async def async_init(self):
        self.suppliers_dict = await self.db.suppliers_dict_id()
        await self.load_date(self.ui.main_win.supplie_table)
        await self.load_date(self.ui.main_win.suppliers_table)
        await self.clicked_btn()

    async def clicked_btn(self):
        win = self.ui.main_win
        win.btn_load_orders.clicked.connect(lambda: self.load_date(self.ui.main_win.supplie_table))
        win.btn_add_orders.clicked.connect(lambda: self.add_new_row(self.ui.main_win.supplie_table))
        win.btn_del_orders.clicked.connect(lambda: self.delete_row(self.ui.main_win.supplie_table))
        win.btn_save_orders.clicked.connect(lambda: self.save_data(self.ui.main_win.supplie_table))
        win.btn_del_all_orders.clicked.connect(lambda: self.delete_all(self.ui.main_win.supplie_table))
        win.btn_xls_orders.clicked.connect(lambda: self.load_excel(self.ui.main_win.supplie_table))

        win.btn_load_users.clicked.connect(lambda: self.load_date(self.ui.main_win.suppliers_table))
        win.btn_add_users.clicked.connect(lambda: self.add_new_row(self.ui.main_win.suppliers_table))
        win.btn_del_users.clicked.connect(lambda: self.delete_row(self.ui.main_win.suppliers_table))
        win.btn_save_users.clicked.connect(lambda: self.save_data(self.ui.main_win.suppliers_table))
        win.btn_del_all_users.clicked.connect(lambda: self.delete_all(self.ui.main_win.suppliers_table))
        win.btn_xls_users.clicked.connect(lambda: self.load_excel(self.ui.main_win.suppliers_table))

    @asyncSlot()
    async def load_date(self, tbl):
        tbl.setRowCount(0)
        data = []
        if tbl.objectName() == "supplie_table":
            data = await self.db.orders_data()
        elif tbl.objectName() == "suppliers_table":
            data = await self.db.users_data()

        for row_number, row_data in enumerate(data):
            tbl.insertRow(row_number)
            for col_number, col_data in enumerate(row_data):
                tbl.setItem(row_number, col_number, QtWidgets.QTableWidgetItem(str(col_data)))
        self.new_row_warning = True
        self.ui.main_win.lbl_info_tbl.setText('Таблица загружена')
        self.delete_all_warning = False

    @asyncSlot()
    async def save_data(self, tbl):
        self.ui.main_win.lbl_info_tbl.setText('')
        try:
            data = []

            for row in range(tbl.rowCount()):
                data.append([])
                if not tbl.item(row, 0).text().isdigit():
                    raise Exception
                for col in range(tbl.columnCount()):
                    if tbl.objectName() == "supplie_table":
                        if col == 2:
                            data[row].append(self.suppliers_dict[tbl.item(row, col).text()])
                        elif col != 4 and col != 5:
                            data[row].append(tbl.item(row, col).text())
                    elif tbl.objectName() == "suppliers_table":
                        data[row].append(tbl.item(row, col).text())
            self.new_row_warning = True

            if tbl.objectName() == "supplie_table":
                await self.db.orders_save(data)
            elif tbl.objectName() == "suppliers_table":
                await self.db.users_save(data)
                if self.delete_all_warning:
                    await self.load_date(self.ui.main_win.supplie_table)
            self.ui.main_win.lbl_info_tbl.setText('Таблица сохранена')
        except AttributeError:
            self.ui.main_win.lbl_info_tbl.setText('Введите все поял корректно')

    def add_new_row(self, tbl):
        if self.new_row_warning:
            row_position = tbl.rowCount()
            new_id = str(int(tbl.item(row_position - 1, 0).text()) + 1)
            tbl.insertRow(row_position)
            tbl.setItem(row_position, 0, QtWidgets.QTableWidgetItem(new_id))
            if tbl.objectName() == "supplie_table":
                tbl.setItem(row_position, 4, QtWidgets.QTableWidgetItem("-"))
                tbl.setItem(row_position, 5, QtWidgets.QTableWidgetItem("-"))
            self.new_row_warning = False
        else:
            self.ui.main_win.lbl_info_tbl.setText('Сохраните таблицу')

    def delete_row(self, tbl):
        if tbl.rowCount() > 0 and tbl.currentRow() != -1:
            current_row = tbl.currentRow()
            tbl.removeRow(current_row)
        if tbl.objectName() == "suppliers_table":
            self.delete_all_warning = True

    def delete_all(self, tbl):
        tbl.clear()
        tbl.setRowCount(0)
        self.ui.setup_headers()
        if tbl.objectName() == "suppliers_table":
            self.delete_all_warning = True

    def load_excel(self, tbl):
        dict_xls = {}
        k = 0
        data = [[tbl.item(row, column).text() for row in range(tbl.rowCount())] for column in range(tbl.columnCount())]

        if tbl.objectName() == "supplie_table":
            dict_xls = {"Номер поставки": [], "Дата поставки": [], "Поставщик": "", "ТТН": [],
                        "ИНН": [], "КПП": [], "Код продукта": [], "Кол-во продукта": []}
        elif tbl.objectName() == "suppliers_table":
            dict_xls = {"Номер": [], "Поставщик": [], "ИНН": [], "КПП": []}

        for key in dict_xls:
            dict_xls[key] = data[k]
            k += 1

        data_frame = pd.DataFrame(dict_xls)
        data_frame.to_excel(f"./ExcelData/{tbl.objectName()}.xlsx", index=False)
        self.ui.main_win.lbl_info_tbl.setText(f'Данные загружены в {tbl.objectName()}.xlsx')
