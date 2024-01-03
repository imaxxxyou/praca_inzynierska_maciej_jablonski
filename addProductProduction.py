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
        self.setWindowTitle("Dodaj produkt")
        self.window = loader.load("addProductForm.ui", self)


        self.cancelButton = QPushButton()
        self.addButton = QPushButton()
        self.comboBox = QComboBox()
        self.spinBox = QSpinBox()
        self.currentProductMagaizne = []


        self.comboUpdate()
        self.window.addButton.clicked.connect(self.accept)
        self.window.cancelButton.clicked.connect(self.reject)
        self.window.label_7.setText("Dodaj produkt do kalkulacji produkcji:")
        self.window.label_3.setText("")
        self.window.labelPrice.setText("")

    def comboUpdate(self):
        ''' Metoda do aktualizacji produktów w liście rozwijanej '''
        import main
        server, db, user, password = main.dbConnectFiles()

        db = main.Database(server=server,
                           database=db,
                           username=user,
                           password=password)

        self.comboBox.clear()
        self.comboList = main.Database.execute_query(query="SELECT Nazwa_Produktu FROM dbo.Produkty;", self=db)
        print("comboList:", self.comboList)
        for i, item in enumerate(self.comboList):
            self.window.comboBox.addItem(item[0])
            print("element:", item[0])

    def add(self):
        ''' Metoda dodaje produkt do listy zamówienia w określonej ilości,
        zwraca nazwę produktu oraz ilość '''
        product = self.window.comboBox.currentText()
        count = self.window.spinBox.value()
        print("Dodaję:", product, "w ilości:", count)
        return product, count


def main():
    '''Formularz Dodania produkt do kalkulatora zapotrzebowania '''
    add_product_form = AddProductWindow()

    # Sprawdź, czy formularz został zakończony poprawnie
    if add_product_form.exec() == QDialog.Accepted:
        product_value = add_product_form.add()
        print("Dodano:", product_value)
    else:
        print("Anulowano dodawanie produktu.")


if __name__ == "__main__":
    main()
