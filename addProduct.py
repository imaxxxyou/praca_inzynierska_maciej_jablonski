from PySide6.QtWidgets import (
    QDialog, QPushButton, QComboBox, QSpinBox)
from PySide6.QtUiTools import QUiLoader


class AddProductWindow(QDialog):
    ''' Konstruktor i klasa formularza dodania produktu zamówienia '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' załadowanie formularza dodania produktu'''
        loader = QUiLoader()
        self.setWindowTitle("Dodaj produkt do zamówienia")
        self.window = loader.load("addProductForm.ui", self)

        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                                database=db,
                                username=user,
                                password=password)

        self.cancelButton = QPushButton()
        self.addButton = QPushButton()
        self.comboBox = QComboBox()
        self.spinBox = QSpinBox()
        self.currentProductMagaizne = []


        self.window.addButton.clicked.connect(self.accept)
        self.window.cancelButton.clicked.connect(self.reject)

        self.comboUpdate()
        self.window.comboBox.currentIndexChanged.connect(self.price_update)
        self.window.spinBox.valueChanged.connect(self.price_update)

    def price_update(self):
        ''' metoda do aktualizacji ceny w labelPrice '''
        print("aktualizuję cenę")
        product = self.window.comboBox.currentText()
        self.count = self.window.spinBox.value()
        print("zaznaczony produkt:", product, type(product))
        self.price = self.db.execute_query(query=f"SELECT Cena FROM dbo.Produkty WHERE Nazwa_produktu ='{product}';")
        self.allPrice = self.price[0][0]*self.count
        self.window.labelPrice.setText(str(self.allPrice)+" zł.")

    def comboUpdate(self):
        ''' Metoda do aktualizacji produktów w liście rozwijanej '''

        self.comboBox.clear()
        self.comboList = self.db.execute_query(query="SELECT Nazwa_Produktu FROM dbo.Produkty;")
        print("comboList:", self.comboList)
        for i, item in enumerate(self.comboList):
            self.window.comboBox.addItem(item[0])
            print("element:", item[0])
        self.price_update()

    def add(self):
        ''' Metoda dodaje produkt do listy zamówienia w określonej ilości,
        zwraca nazwę produktu oraz ilość '''
        product = self.window.comboBox.currentText()
        count = self.window.spinBox.value()
        price = self.window.labelPrice.text()
        print("Dodaję:", product, "w ilości:", count)
        return product, count, self.allPrice


def main():
    '''Formularz Dodania produkt do nowego zamówienia'''
    add_product_form = AddProductWindow()

    # Sprawdź, czy formularz został zakończony poprawnie
    if add_product_form.exec() == QDialog.Accepted:
        product_value = add_product_form.add()
        print("Dodano:", product_value)
    else:
        print("Anulowano dodawanie produktu.")


if __name__ == "__main__":
    main()
