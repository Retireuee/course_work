from PyQt5.uic import loadUi


class UiInterface:
    """Загрузка ui файла"""

    def __init__(self, main_win):
        self.main_win = main_win
        self.setup_ui()

    def setup_ui(self):
        loadUi('./GUI/UI.ui', self.main_win)
        self.main_win.setWindowTitle('Table')

    def setup_headers(self):
        self.main_win.supplie_table.setHorizontalHeaderLabels(['Номер поставки', 'Дата поставки', 'Поставщик', 'ТТН',
                                                               'ИНН', 'КПП', 'Код продукта', 'Кол-во продукта'])
        self.main_win.suppliers_table.setHorizontalHeaderLabels(['Номер', 'Поставщик', 'ИНН', 'КПП'])
