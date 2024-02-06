from decimal import Decimal

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidgetItem, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza edycji produktu '''

    def __init__(self, values):
        super().__init__(parent=None)
        self.values = values
        print("VALUES:", values)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edytucja Produktu")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addNewUnitForm.ui", self)
        self.window.label.setText("Edytuj Produkt")

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

        self.window.pushButtonAdd.setText("Zapisz zmiany")
        self.productid = self.values[0]

        # wprowadzenie jednostek miary z pliku do comboBoxa
        self.window.comboBoxUnit.clear()
        with open('docs/units.txt', 'r', encoding="UTF-8") as file:
            # Odczytanie kolejnych linii z pliku
            lines = file.readlines()
            # wprowadzenie wartości do comboBoxUnit
            for line in lines:
                self.window.comboBoxUnit.addItem(line.strip())

        # ustawienie danych z danego wiersza do odpowiednich boksów
        self.window.PRODUCT_ID.setText(str(int(self.values[0])))
        self.window.lineEditProductName.setText(str(self.values[1]))
        indexUnit = self.window.comboBoxUnit.findText(str(self.values[2]))
        self.window.comboBoxUnit.setCurrentIndex(indexUnit)

        self.window.doubleSpinBoxPrice.setValue(float(self.values[3]))
        print("ilosc:", int(self.values[4]))
        self.window.spinBoxQuantity.setValue(int(self.values[4]))
        self.window.lineEditDescription.setText(str(self.values[5]))
        self.window.lineEditLocDesc.setText(str(self.values[6]))

        self.cords = self.db.execute_query(query=f"SELECT x,y FROM dbo.Lokalizacja_Produktu "
                                                 f"WHERE id_produktu = {int(self.values[0])};")
        if len(self.cords) > 0:
            self.cords = self.cords[0]
            self.window.localization_label.setText(str(self.cords))
        else:
            self.window.localization_label.setText("")

        self.load_recipe()

        # przypisanie akcji do przycisków

        self.window.pushButtonAdd.clicked.connect(self.update_database)
        self.window.pushButtonCancel.clicked.connect(self.close)
        self.window.pushButtonLocalization.clicked.connect(self.add_loc)

        self.window.pushButtonAddComponent.clicked.connect(self.add_component)
        self.window.pushButtonDelComponent.clicked.connect(
            lambda: self.del_component(index=self.window.tableWidget.currentRow()))

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

    def load_recipe(self):
        ''' Metoda do ładowania aktualnej receptury danego roduktu, zwraca listę '''
        actuall_recipe = self.db.execute_query(query=f"SELECT * FROM dbo.Produkty_Skladniki "
                                                          f"WHERE id_produktu = {int(self.values[0])};")
        print("Receptura:", actuall_recipe)
        for component in actuall_recipe:
            componentid = component[1]
            need = component[2]
            components = self.db.execute_query(query=f"SELECT Nazwa_Skladnika, Jednostka_Miary "
                                                 f"FROM dbo.SKladniki "
                                                 f"WHERE id = {componentid}")
            print("Component: ", components, "id:", componentid, "need:", need)
            for _ in components:
                lista = []
                lista.append((_[0], _[1], need))
                print(lista)
                self.productList.append(lista[0])
        self.updateTable()

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
                print("1Dodano do listy:", product, "w ilości:", count, unit)
                print("1Receptura produktu zawiera:", self.productList)

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

    def update_database(self):
        ''' Metoda aktualizująca produkt w bazie danych i jego recepturę'''
        print("\n\n\nAktualizuje produkt w bazie danych... oraz jego recepturę.")

        # pobranie i konwersja zmiennych z okna w celu aktualizacji bazy danych
        nazwaproduktu = self.window.lineEditProductName.text()
        print("Nowa nazwa produktu:", nazwaproduktu, type(nazwaproduktu))

        cena = self.window.doubleSpinBoxPrice.text()
        cena = cena.replace(",", ".")
        cena = Decimal(str(float(cena)))
        print("Nowa cena produktu:", cena, type(cena))
        opis_lokalizacji = self.window.lineEditLocDesc.text()

        ilosc = int(self.window.spinBoxQuantity.text())
        print("Nowa ilość produktu:", ilosc, type(ilosc))

        if self.window.comboBoxUnit.currentIndex() >= 0:
            jednostka = self.window.comboBoxUnit.currentText()
            print("Nowa jednostka Miary:", jednostka, type(jednostka))

        opis = self.window.lineEditDescription.text()
        print("Nowy opis produktu:", opis)

        koordynaty_lokalizacji = self.cords
        print("Kordynaty lokalizacji: x=", koordynaty_lokalizacji[0], "y=", koordynaty_lokalizacji[1])
        print("ID produktu:", self.productid, type(self.productid))

        # Aktualizacja danych w tabeli dbo.Produkty
        self.db.execute_query(query=f"UPDATE dbo.Produkty "
                                    f"SET Nazwa_Produktu = '{nazwaproduktu}', "
                                    f"Jednostka_Miary = '{jednostka}', "
                                    f"Cena = {cena}, "
                                    f"Dostepna_ilosc = {ilosc}, "
                                    f"Opis = '{opis}', "
                                    f"Lokalizacja = '{opis_lokalizacji}' "
                                    f"WHERE ID = {self.productid};")

        # Usuwanie aktualnej receptury
        self.db.execute_query(query=f"DELETE FROM dbo.Produkty_Skladniki "
                                    f"WHERE id_produktu = {self.productid} ;")

        # Aktualizacja receptury w tabeli dbo.Produkty_Skladniki
        # pętla dodająca recepture do odpowiedniej tabeli
        for item in self.productList:
            print("Dodaję Składnik:", item)
            self.skladnikid = self.db.execute_query(query=f"SELECT ID "
                                                          f"FROM dbo.Skladniki "
                                                          f"WHERE Nazwa_SKladnika = '{item[0]}';")
            self.skladnikid = self.skladnikid[0]
            print(self.skladnikid[0], type(self.skladnikid[0]))
            self.db.execute_query(query=f"INSERT INTO dbo.Produkty_Skladniki "
                                        f"VALUES ({self.productid}, {self.skladnikid[0]}, {item[2]});")

        # edycja lokalizacji produktu
        self.db.execute_query(query=f"DELETE FROM dbo.Lokalizacja_Produktu "
                                    f"WHERE id_produktu = {self.productid} ;")
        self.db.execute_query(query=f"INSERT INTO dbo.Lokalizacja_Produktu "
                                    f"VALUES ({self.productid},{koordynaty_lokalizacji[0]},{koordynaty_lokalizacji[1]});")

        self.close()


def main(values):
    '''Formularz Edycji Produktu '''
    win = OrderFormWindow(values)
    win.exec()


if __name__ == "__main__":
    main()
