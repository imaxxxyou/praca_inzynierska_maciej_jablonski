from PySide6.QtGui import QIcon, QColor, Qt
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza do kalkulatora produkcji '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Kalkulator wytwarzania produktów")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("ProductionForm.ui", self)

        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                           database=db,
                           username=user,
                           password=password)

        # przypisanie klas PySide do elementów w oknie
        self.productList = []
        self.pushButtonClose = QPushButton()
        self.pushButtonExit = QPushButton()
        self.tableWidgetNeed = QTableWidget()
        self.pushButtonRemoveProduct = QPushButton()
        self.pushButtonCalculate = QPushButton()
        self.componentNeedList = []
        self.rowNeed = 0

        # przypisanie akcji do przycisków
        self.window.pushButtonAddProduct.clicked.connect(self.add_product)
        self.window.pushButtonRemoveProduct.clicked.connect(lambda:
                                                            self.remove_product(index=self.window.tableWidgetWant
                                                                                .currentRow()))
        self.window.pushButtonExit.clicked.connect(self.close)
        self.set_table_style()

    def set_table_style(self):
        ''' metoda do ustawiania stylu tabel '''
        self.window.tableWidgetWant.verticalHeader().hide()
        self.window.tableWidgetWant.resizeColumnsToContents()
        self.window.tableWidgetWant.resizeRowsToContents()
        self.window.tableWidgetWant.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Ustaw szerokość kolumn na podstawie zawartości
        header = self.window.tableWidgetWant.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.window.tableWidgetWant.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 1px;
            }
            QHeaderView::section {
                background-color: #03840e;
                color: white;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)
        # Wyłącz edycję komórek
        rows = self.window.tableWidgetWant.rowCount()
        cols = self.window.tableWidgetWant.columnCount()

        for row in range(rows):
            for col in range(cols):
                item = self.window.tableWidgetWant.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        self.window.tableWidgetNeed.verticalHeader().hide()
        self.window.tableWidgetNeed.resizeColumnsToContents()
        self.window.tableWidgetNeed.resizeRowsToContents()
        self.window.tableWidgetNeed.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Ustaw szerokość kolumn na podstawie zawartości
        header = self.window.tableWidgetNeed.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.window.tableWidgetNeed.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 1px;
            }
            QHeaderView::section {
                background-color: #03840e;
                color: white;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)
        # Wyłącz edycję komórek
        rows = self.window.tableWidgetNeed.rowCount()
        cols = self.window.tableWidgetNeed.columnCount()

        for row in range(rows):
            for col in range(cols):
                item = self.window.tableWidgetNeed.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def remove_product(self, index):
        ''' Metoda usuwająca produkt z tabeli na podstawie indeksu '''
        print("Próbuję usunąć produkt o indexie:", index)
        if index < len(self.productList):
            del self.productList[index]
            self.update_table()
            print(f"Usunięto produkt o indeksie {index}")
            if len(self.productList) == 0:
                self.window.tableWidgetNeed.clearContents()
                self.window.tableWidgetNeed.setRowCount(0)

        else:
            print(f"Błąd: Nieprawidłowy indeks {index} do usunięcia produktu.")
        # włączanie przycisku dodawania produktu
        self.window.pushButtonAddProduct.setEnabled(True)

    def add_product(self):
        ''' metoda do dodawania produktów do tablewidget do obliczania produkcji'''
        print("dodaje produkt")
        import addProductProduction
        add_product_form = addProductProduction.AddProductWindow()
        # Otwórz formularz
        if add_product_form.exec_() == QDialog.Accepted:
            # Pobierz wartość skladnika z formularza
            product, count = add_product_form.add()

            # instrukcja z pętlą dodająca
            # do listy składnik jeśli nie został już dodany wcześniej
            if len(self.productList) > 0:
                for tuple in self.productList:
                    if not product in tuple:
                        self.productList.append((product, count))
                        print("Dodano do listy:", product, "w ilości:", count)
                        print("Produkcja zawiera:", self.productList)
                        break
                    else:
                        print("Produkt:", product, "jest już w recepturze.")
            else:
                self.productList.append((product, count))
                print("Dodano do listy:", product, "w ilości:", count)
                print("Receptura produktu zawiera:", self.productList)

            # aktualizacja tabeli zamówionych produktów
            print("aktualizuję tabelę")
            self.update_table()
        # wyłączanie przycisku dodawania produktu - ver 1.0
        self.window.pushButtonAddProduct.setEnabled(False)

    def update_table(self):
        ''' Metoda aktualizująca tabelę na podstawie listy produktów '''
        self.window.tableWidgetWant.setRowCount(len(self.productList))
        self.window.tableWidgetWant.setColumnCount(2)  # ilość kolumn w tabeli
        try:
            product = self.productList[0]
            self.product_name = product[0]
            self.product_count = product[1]
        except:
            product = 0
        print("pn:", self.product_name)

        self.product_id = self.db.execute_query(query=f"SELECT ID "
                                                      f"FROM dbo.Produkty "
                                                      f"WHERE Nazwa_Produktu = '{self.product_name}'")
        self.product_id = self.product_id[0]

        self.component_id = self.db.execute_query(query=f"SELECT ID_skladnika "
                                                              f"FROM dbo.Produkty_Skladniki "
                                                              f"WHERE ID_produktu = {self.product_id[0]} ")
        self.component_need = self.db.execute_query(query=f"SELECT ID_skladnika, Need "
                                                          f"FROM dbo.Produkty_Skladniki "
                                                          f"WHERE ID_produktu = {self.product_id[0]}")
        print("Componet_id:", self.component_id)
        print("Component_need:", self.component_need) # id skladnika, potrzebna ilosc
        self.set_table_style()

        for i, (product, count) in enumerate(self.productList):
            print("Dodaję do tabeli:", product, "w ilości:", count)
            # Wstaw wartości do odpowiednich komórek tabeli
            self.window.tableWidgetWant.setItem(i, 0, QTableWidgetItem(str(product)))
            self.window.tableWidgetWant.setItem(i, 1, QTableWidgetItem(str(count)))

        self.update_table_need()


    def update_table_need(self):
        '''Metoda służąca do aktualizowania tabeli składników potrzebnych do wytworzenia danych produktów '''
        print('Dorzucam składnik do tabeli "tableWidgetNeed" potrzebny do wytworzenia podanej produkcji.')
        # czyszczenie zawartosci tabeli
        with open("docs/slowa_nieskonczone.txt", "r", encoding="UTF-8") as file:
            lista_nieskonczonosci = file.readline().replace("\n", "")
        self.window.tableWidgetNeed.clearContents()
        self.window.tableWidgetNeed.setRowCount(0)
        for i, component_id in enumerate(self.component_id):
            self.window.tableWidgetNeed.setRowCount(len(self.component_id))
            self.componentNeedList = self.db.execute_query(
                query=f"SELECT Nazwa_Skladnika, Jednostka_Miary, Dostepna_Ilosc"
                      f" FROM dbo.Skladniki "
                      f"WHERE ID = {component_id[0]};")
            print("componentList:", self.componentNeedList)
            for item in self.componentNeedList:
                print("Dodaję do tabeli skladnik:", item)
                print("element:", item, "i:", i)
                #Nazwa skladnika
                self.window.tableWidgetNeed.setItem(i, 0, QTableWidgetItem(str(item[0])))
                self.window.tableWidgetNeed.setColumnWidth(0, 250)
                #Jednostka Miary
                self.window.tableWidgetNeed.setItem(i, 4, QTableWidgetItem(str(item[1])))
                #Ilosc na magazynie
                self.window.tableWidgetNeed.setItem(i, 1, QTableWidgetItem(str(item[2])))
                oblicz_zapotrzebowanie = int(item[2])
                print("intitem2", int(item[2]))
            for item in self.component_need:
                self.window.tableWidgetNeed.setItem(i, 2, QTableWidgetItem(str(int(item[1])*int(self.product_count))))
                # obliczanie zapotrzebowania składników do produktu
                oblicz = (int(item[1]) * int(self.product_count)) - oblicz_zapotrzebowanie
                print("OBLICZ ZAPOTRZEBOWANIE:", oblicz_zapotrzebowanie)
                print("Brakuje:", oblicz)
                if oblicz > 0:
                    print("ustawiam czerwony")
                    self.window.tableWidgetNeed.setItem(i, 3, QTableWidgetItem(str(oblicz)))
                    # Kolorowanie komórki na jasny czerwony
                    self.window.tableWidgetNeed.item(i, 3).setBackground(QColor(255, 144, 144))
                    # zresetowanie obliczenia zapotrzebowania w celu obliczenia zapotrzebowania dla kolejnego skladnika
                    oblicz = 0
                # elif item in lista_nieskonczonosci:
                #     print("ustawiam zielony")
                #     self.window.tableWidgetNeed.setItem(i, 3, QTableWidgetItem(str("Ilość wystarczająca")))
                #     # Kolorowanie komórki na jasny zielony
                #     self.window.tableWidgetNeed.item(i, 3).setBackground(QColor(144, 238, 144))
                #     self.window.tableWidgetNeed.setColumnWidth(3, 120)
                #     # zresetowanie obliczenia zapotrzebowania w celu obliczenia zapotrzebowania dla kolejnego skladnika
                #     oblicz = 0
                else:
                    print("ustawiam zielony")
                    self.window.tableWidgetNeed.setItem(i, 3, QTableWidgetItem(str("Ilość wystarczająca")))
                    # Kolorowanie komórki na jasny zielony
                    self.window.tableWidgetNeed.item(i, 3).setBackground(QColor(144, 238, 144))
                    self.window.tableWidgetNeed.setColumnWidth(3, 120)
                    # zresetowanie obliczenia zapotrzebowania w celu obliczenia zapotrzebowania dla kolejnego skladnika
                    oblicz = 0


def main():
    '''Formularz otwierający formularz kalkulatora produkcji '''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
