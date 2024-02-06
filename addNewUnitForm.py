from decimal import Decimal

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidgetItem, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox, QMessageBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza dodawania nowego produktu '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Dodaj Nowy Produkt")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addNewUnitForm.ui", self)

        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                           database=db,
                           username=user,
                           password=password)

        # przypisanie klas PySide do elementów w oknie ustawień
        self.PRODUCT_ID = QLabel()
        self.pushButtonAdd = QPushButton()
        self.pushButtonCancel = QPushButton()
        self.lineEditProductName = QLineEdit()
        self.doubleSpinBoxPrice = QDoubleSpinBox()
        self.spinBoxQuantity = QSpinBox()
        self.comboBoxUnit = QComboBox()
        self.comboBoxSupplier = QComboBox()
        self.comboBoxLoc = QComboBox()
        self.lineEditDescription = QLineEdit()
        self.pushButtonAddComponent = QPushButton()
        self.pushButtonDelComponent = QPushButton()
        self.productList = []
        self.pushButtonLocalization = QPushButton()
        self.localization_label = QLabel()
        self.lineEditLocDesc = QLineEdit()
        self.cords = ""

        # ustawienie ostatniego id produktu + 1 w celu wyświetlenia nowego id dodawanego produktu
        self.productid = self.db.execute_query(query=f"SELECT MAX(ID) AS ID FROM dbo.Produkty;")
        print(self.productid[0])
        self.productid = self.productid[0]
        self.window.PRODUCT_ID.setText(str(int(self.productid[0])+1))

        self.window.localization_label.setText("")

        # wprowadzenie jednostek miary z pliku do comboBoxa
        self.window.comboBoxUnit.clear()
        with open('docs/units.txt', 'r', encoding="UTF-8") as file:
            # Odczytanie kolejnych linii z pliku
            lines = file.readlines()
            # wprowadzenie wartości do comboBoxUnit
            for line in lines:
                self.window.comboBoxUnit.addItem(line.strip())


        # przypisanie akcji do przycisków

        self.window.pushButtonAdd.clicked.connect(self.add_to_database)
        self.window.pushButtonCancel.clicked.connect(self.close)
        self.window.pushButtonLocalization.clicked.connect(self.add_loc)

        self.window.pushButtonAddComponent.clicked.connect(self.add_component)
        self.window.pushButtonDelComponent.clicked.connect(lambda: self.del_component(index=self.window.tableWidget.currentRow()))

    def add_loc(self):
        ''' metoda do ustawiania lokalizacji w magazynie '''
        import add_localization
        print(self.cords, type(self.cords))
        if len(self.cords) > 0:
            self.cords = add_localization.main(self.cords[0], self.cords[1])
        else:
            self.cords = add_localization.main(300, 300)
        print("Ustawiam lokalizację:", self.cords, type(self.cords))
        self.window.localization_label.setText(str(self.cords))

    def del_component(self, index):
        ''' Metoda usuwająca produkt z tabeli na podstawie indeksu '''
        print("Próbuję usunąć produkt o indexie:", index)
        if index < len(self.productList):
            del self.productList[index]
            self.updateTable()
            print(f"Usunięto produkt o indeksie {index}")
        else:
            print(f"Błąd: Nieprawidłowy indeks {index} do usunięcia produktu.")

    def add_component(self):
        ''' Metoda uruchamiająca formularz dodawania skladnika do receptury '''
        import addComponent

        # Otwórz formularz dodaania skladnika
        add_product_form = addComponent.AddProductWindow()

        # Sprawdź, czy formularz został zakończony poprawnie
        if add_product_form.exec_() == QDialog.Accepted:
            # Pobierz wartość skladnika z formularza
            product, unit, count = add_product_form.add()

            # instrukcja z pętlą dodająca
            # do listy składnik jeśli nie został już dodany wcześniej
            if len(self.productList) > 0:
                for tuple in self.productList:
                    if not product in tuple:
                        self.productList.append((product, unit, count))
                        print("Dodano do listy:", product, "w ilości:", count, unit)
                        print("Receptura produktu zawiera:", self.productList)
                        break
                    else:
                        print("Produkt:", product, "jest już w recepturze.")
                        break
            else:
                self.productList.append((product, unit, count))
                print("Dodano do listy:", product, "w ilości:", count, unit)
                print("Receptura produktu zawiera:", self.productList)

            # aktualizacja tabeli zamówionych produktów
            print("aktualizuję tabelę")
            self.updateTable()

    def updateTable(self):
        ''' Metoda aktualizująca tabelę na podstawie listy produktów '''
        self.window.tableWidget.setRowCount(len(self.productList))
        self.window.tableWidget.setColumnCount(3)  # ilość kolumn w tabeli

        for i, (product, unit, count) in enumerate(self.productList):
            print("Dodaję do tabeli:", product, "w ilości:", count)
            # Wstaw wartości do odpowiednich komórek tabeli
            self.window.tableWidget.setItem(i, 0, QTableWidgetItem(str(product)))
            self.window.tableWidget.setItem(i, 1, QTableWidgetItem(str(unit)))
            self.window.tableWidget.setItem(i, 2, QTableWidgetItem(str(count)))

    def add_to_database(self):
        ''' Metoda dodająca produkt do bazy danych i jego recepturę'''
        print("\n\n\nDodaje nowy produkt do bazy danych... oraz jego recepturę.")

        # pobranie i konwersja zmiennych z okna w celu zapisania do bazy danych
        nazwaproduktu = self.window.lineEditProductName.text()
        print("Nazwa produktu:", nazwaproduktu, type(nazwaproduktu))

        # pobranie i konwersja ceny z text na float i na decimal aby mozna bylo wprowadzic ją do bazy danych
        cena = self.window.doubleSpinBoxPrice.text()
        cena = cena.replace(",", ".")
        cena = Decimal(str(float(cena)))
        print("Cena produktu:", cena, type(cena))

        # pobranie ilości wprowadzanego produktu
        ilosc = int(self.window.spinBoxQuantity.text())
        print("Ilość produktu:", ilosc, type(ilosc))

        # Pobranie aktualnej wartości z QComboBox
        print(self.window.comboBoxUnit.currentIndex())
        if self.window.comboBoxUnit.currentIndex() >= 0:
            jednostka = self.window.comboBoxUnit.currentText()
            print("Jednostka Miary:", jednostka, type(jednostka))

        opis = self.window.lineEditDescription.text()
        print("Opis produktu:", opis)
        opis_lokalizacji = self.window.lineEditLocDesc.text()
        koordynaty_lokalizacji = self.cords

        print("ID produktu:", self.productid[0], type(self.productid[0]))
        if koordynaty_lokalizacji != "" and nazwaproduktu != "":
            print("Kordynaty lokalizacji: x=", koordynaty_lokalizacji[0], "y=", koordynaty_lokalizacji[1])
            print("Próba wgrania do bazy danych:")
            try:
                self.db.execute_query(query=f"INSERT INTO dbo.Produkty "
                                            f"VALUES ('{nazwaproduktu}','{jednostka}',{cena},{ilosc},'{opis}','{opis_lokalizacji}');")
                try:
                    # dodawanie lokalizacji produktu
                    self.db.execute_query(query=f"INSERT INTO dbo.Lokalizacja_Produktu "
                                                f"VALUES ({self.productid[0]+1},{koordynaty_lokalizacji[0]},{koordynaty_lokalizacji[1]});")
                    try:
                        # pętla dodająca recepture do odpowiedniej tabeli
                        for item in self.productList:
                            print("Dodaję Składnik:", item)
                            self.skladnikid = self.db.execute_query(query=f"SELECT ID "
                                                                          f"FROM dbo.SKladniki "
                                                                          f"WHERE Nazwa_SKladnika = '{item[0]}';")
                            self.skladnikid = self.skladnikid[0]
                            print(self.skladnikid[0], type(self.skladnikid[0]))

                            self.db.execute_query(query=f"INSERT INTO dbo.Produkty_Skladniki "
                                                        f"VALUES ({self.productid[0]+1}, {self.skladnikid[0]}, {item[2]});")

                    except Exception as e:
                        print("Błąd:", e)
                except Exception as e:
                    print("Blad", e)
                print("Dodano pomyślnie nowy produkt do bazy danych.")
                info_box = QMessageBox()
                info_box.setIcon(QMessageBox.Icon.Warning)
                info_box.setWindowTitle("Uwaga")
                info_box.setText(
                    "Dodano produkt: "+nazwaproduktu+" do bazy danych." )
                info_box.addButton(QMessageBox.StandardButton.Ok)
                info_box.exec()
                self.close()
            except Exception as e:
                print("Błąd: ", e)
                info_box = QMessageBox()
                info_box.setIcon(QMessageBox.Icon.Warning)
                info_box.setWindowTitle("Uwaga")
                info_box.setText(
                    "Wprowadź nazwę produktu i lokalizację w magazynie.\n\nBłąd:\n" + str(e))
                info_box.addButton(QMessageBox.StandardButton.Ok)
                info_box.exec()
        else:
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Warning)
            info_box.setWindowTitle("Uwaga")
            info_box.setText(
                "Wprowadź nazwę i lokalizację w magazynie.")
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()


def main():
    '''Formularz Dodawania Nowego Produktu '''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
