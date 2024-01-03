from datetime import datetime
from decimal import Decimal

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QHeaderView)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza do edycji zamówienia '''

    def __init__(self, values):
        super().__init__(parent=None)
        self.values = values
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edycja zamówienia")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("orderForm.ui", self)

        import main
        server, db, user, password = main.dbConnectFiles()
        self.db = main.Database(server=server,
                                database=db,
                                username=user,
                                password=password)

        # przypisanie klas Pyside6 do elementow w oknie
        self.addProductButton = QPushButton()
        self.acceptOrderButton = QPushButton()
        self.cancelButton = QPushButton()
        self.removeButton = QPushButton()
        self.tableWidget = QTableWidget()
        self.productList = []
        self.lineEditAdress = QLineEdit()
        self.comboList = []


        # Formatowanie i ustawienie daty
        today = datetime.now()
        self.formatted_date = today.strftime("%Y-%m-%d")
        self.window.labelOrderDate.setText(self.formatted_date)

        self.lineEditAdress


        # przypisanie akcji do przycisków
        self.addNewProduct = self.window.addProductButton.clicked.connect(self.add_product)
        self.window.removeButton.clicked.connect(lambda: self.remove_product(index=self.window.tableWidget.currentRow()))
        self.window.acceptOrderButton.clicked.connect(self.update_order)
        self.window.acceptOrderButton.setText("Zapisz zmiany")
        self.window.cancelButton.clicked.connect(self.close)

        productList = self.db.execute_query(query=f"SELECT P.Nazwa_Produktu, ZP.ilosc, ZP.cena "
                                                   f"FROM dbo.zamowione_produkty ZP "
                                                   f"JOIN dbo.Produkty P ON ZP.id_produktu = P.ID "
                                                   f"WHERE ZP.id_zamowienia = {self.values[0]}")
        print(productList)
        self.productList = productList

        self.update_table()
        self.combo_update()

        self.window.labelOrderID.setText(str(self.values[0])) # id zamowienia
        self.orderid = int(self.values[0])
        self.window.comboBox.setCurrentText(str(self.values[1])) # klient
        self.window.lineEditAdress.setText(str(self.values[2])) # adres
        self.window.labelNIP.setText(str(self.client[1])) # nip
        self.window.labelOrderDate.setText(str(self.values[3])) # data zamówienia
        self.window.comboBox_2.setCurrentText(str(self.values[9])) # forma wysylki
        self.adress_update()
        self.window.comboBox.currentIndexChanged.connect(self.adress_update)

    def set_table_style(self):
        ''' metoda do stylizacji tabeli w nowym zamówieniu '''
        self.window.tableWidget.verticalHeader().hide()
        self.window.tableWidget.resizeColumnsToContents()
        self.window.tableWidget.resizeRowsToContents()
        self.window.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Ustaw szerokość kolumn na podstawie zawartości
        header = self.window.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.window.tableWidget.setStyleSheet("""
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
        rows = self.window.tableWidget.rowCount()
        cols = self.window.tableWidget.columnCount()

        for row in range(rows):
            for col in range(cols):
                item = self.window.tableWidget.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def remove_product(self, index):
        ''' Metoda usuwająca produkt z tabeli na podstawie indeksu '''
        print("Próbuję usunąć produkt o indexie:", index)
        if index < len(self.productList):
            del self.productList[index]
            self.update_table()
            print(f"Usunięto produkt o indeksie {index}")
        else:
            print(f"Błąd: Nieprawidłowy indeks {index} do usunięcia produktu.")

    def add_product(self):
        ''' Metoda uruchamiająca formularz dodawania produktu '''
        import addProduct

        # Otwórz formularz
        add_product_form = addProduct.AddProductWindow()


        # Dodaj do listy
        if add_product_form.exec_() == QDialog.Accepted:
            # Pobierz wartość produktu z formularza
            # print(product_value, count)
            product_name, count, price = add_product_form.add()
            print("Okno zaakceptowane")
            print("Lista zawiera", self.productList)
            if len(self.productList) > 0:
                print("Jeżeli dlugosc listy jest wieksza od 0")
                for tuple in self.productList:
                    print("Pętla sprawdzająca listę")
                    print("Tupla:", tuple)
                    print("PRODUCT_NAME="+product_name, "tuple="+tuple[0])
                    if not product_name in tuple[0]:
                        print("Jeżeli produktu nie ma w liscie to go dodaję ")
                        # Sprawdź, czy formularz został zakończony poprawnie
                        self.productList.append((product_name, count, price))
                        print("Dodano:", product_name, "w ilości:", count, "w cenie:", price)
                        print("Zamówienie zawiera:", self.productList)
                        break
                    else:
                        print("Produkt już został dodany do listy w zamówieniu.")
                        break
            else:
                self.productList.append((product_name, count, price))
                print("Dodano do listy:", product_name, "w ilości:", count, "w cenie:", price, type(price))
                print("Receptura produktu zawiera:", self.productList)

        # aktualizacja tabeli zamówionych produktów
        print("aktualizuję tabelę")
        self.update_table()

    def update_order(self):
        ''' Meetoda dodająca zamówienie zwraca listę z produktami '''
        print("Dodaje nowe zamówienie")

        id = self.orderid
        klient = self.client[0]
        adres_dostawy = self.adress
        kwota_zamowienia = round(Decimal(self.allPrice),2)
        print(kwota_zamowienia)
        status_zamowienia = "W trakcie realizacji"
        status_platnosci = "Oczekuje"
        forma_wysylki = self.window.comboBox_2.currentText()
        if self.window.lineEditWarnings.text() != "":
            uwagi = self.window.lineEditWarnings.text()
        else:
            uwagi = None
        try:
            print("Edytuję zamówienie w bazie danych:")
            self.db.execute_query(query=f"SET IDENTITY_INSERT dbo.Zamowienia ON;")
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Klient = '{klient}', "
                                        f"Adres_dostawy = '{adres_dostawy}', "
                                        f"Kwota_zamowienia = {kwota_zamowienia}, "
                                        f"forma_wysylki = '{forma_wysylki}', "
                                        f"uwagi = '{uwagi}' "
                                        f"WHERE id = {id};")

            try:
                # przywracam stan magazynowy poprzez usuniecie w bazie danych informacji o produktach
                # a następnie dodaję jeszcze raz zakutalizowaną listę produktów
                quantity = self.db.execute_query(query=f"SELECT id_produktu, ilosc "
                                                       f"FROM dbo.zamowione_produkty "
                                                       f"WHERE id_zamowienia = {self.values[0]};")
                print("QUANTITY:", quantity)
                for product in quantity:
                    old_quantity = self.db.execute_query(
                        query=f"SELECT Dostepna_ilosc FROM dbo.Produkty WHERE id = {product[0]};")
                    new_quantity = int(product[1]) + int(old_quantity[0][0])
                    self.db.execute_query(query=f"UPDATE dbo.Produkty "
                                                f"SET Dostepna_ilosc = {int(new_quantity)} "
                                                f"WHERE id = {product[0]}")
                self.db.execute_query(query=f"DELETE FROM dbo.zamowione_produkty "
                                            f"WHERE id_zamowienia = {self.values[0]}")
                print("Dodawanie produktów do zamówienia do tabeli zamowione_produkty:")
                for item in self.productList:
                    self.productid = self.db.execute_query(query=f"SELECT ID "
                                                                 f"FROM dbo.Produkty "
                                                                 f"WHERE Nazwa_produktu = '{item[0]}';")
                    print(f"VALUES ({self.orderid},{self.productid[0][0]},{item[1]},{item[2]});")

                    # Obliczanie zużytej ilości produktu do zamowienia
                    product_quantity = self.db.execute_query(query=f"SELECT Dostepna_ilosc FROM dbo.Produkty WHERE ID = {self.productid[0][0]};")
                    product_quantity = product_quantity[0][0]
                    upadate_quantity = int(product_quantity)-int(item[1])

                    self.db.execute_query(query=f"INSERT INTO dbo.zamowione_produkty "
                                                f"VALUES ({self.orderid},{self.productid[0][0]},{item[1]},{item[2]});")
                    self.db.execute_query(query=f"UPDATE dbo.Produkty "
                                                f"SET Dostepna_Ilosc = {upadate_quantity} "
                                                f"WHERE ID = {self.productid[0][0]}")

            except Exception as e:
                print("Błąd w dodawaniu produktów do zamówienia:", e)
        except Exception as e:
            print("Błąd:", e)


        # self.db.execute_query(
        #     query=f"INSERT INTO dbo.Zamówienia (event_name, event_date) "
        #           f"VALUES ('{newdescription}', '{self.EVENTDATE}');"
        # )
        # Przykładowe dane
        # order_id = self.window.tableWidgetOrderProduct pierwszy index
        # event_name = 'Przykładowe zamówienie'
        # event_date = '2023-12-01'

        # Wywołaj procedurę składowaną
        # self.db.cursor.execute("EXEC InsertEventAfterOrderUpdate ?, ?, ?;", order_id, event_name, event_date)

        self.db.close_connection
        self.close()

    def adress_update(self):
        ''' metoda do aktualizacji linii adresu i nipu '''
        print("Aktualizuję adres dostawy")
        client = self.window.comboBox.currentIndex()
        self.client = self.comboList[client]
        self.adress = self.db.execute_query(query=f"SELECT Adres "
                                                  f"FROM dbo.Klienci "
                                                  f"WHERE Nazwa_Klienta = '{self.client[0]}' "
                                                  f"AND NIP = {self.client[1]};")
        print(self.client, type(self.client), self.adress, type(self.adress))
        self.adress = self.adress[0][0]
        self.window.labelNIP.setText(str(self.client[1]))
        self.window.lineEditAdress.setText(self.adress)

    def combo_update(self):
        ''' Metoda do aktualizacji klientów w liście rozwijanej '''

        self.window.comboBox.clear()
        try:
            self.comboList = self.db.execute_query(query="SELECT Nazwa_Klienta, NIP FROM dbo.Klienci;")
            print("comboList:", self.comboList)
            for i, item in enumerate(self.comboList):
                self.window.comboBox.addItem(str(item[0]))
                print("element:", str(item[0])+" NIP: "+str(item[1]))
        except Exception as e:
            print("Błąd ładowania comboBox: ", e)
            self.window.labelError.setText(str(e))
            self.window.labelError.setStyleSheet("font-size: 10px; color: blue;")
            self.window.comboBox.addItem("BŁĄD BAZY DANYCH")
        self.adress_update()

    def update_table(self):
        ''' Metoda aktualizująca tabelę na podstawie listy produktów '''
        self.allPrice = 0.0
        self.window.tableWidget.setRowCount(len(self.productList))
        if len(self.productList) > 0:
            self.window.tableWidget.setColumnCount(len(self.productList[0]))  # ilość kolumn w tabeli
        else:
            self.window.tableWidget.setColumnCount(3)

        for i, (product, count, price) in enumerate(self.productList):
            print("Dodaję do tabeli:", product, "w ilości:", count)
            # Wstaw wartości do odpowiednich komórek tabeli
            self.window.tableWidget.setItem(i, 0, QTableWidgetItem(str(product)))
            self.window.tableWidget.setItem(i, 1, QTableWidgetItem(str(count)))
            self.window.tableWidget.setItem(i, 2, QTableWidgetItem(str(price)))
            self.allPrice += float(price)
        self.window.labelOrderCash.setText(str(self.allPrice)+" zł.")
        self.set_table_style()


def main(values):
    '''Formularz Nowego Zamówienia'''
    win = OrderFormWindow(values=values)
    win.exec()


if __name__ == "__main__":
    main()
