from PySide6.QtWidgets import (
    QDialog, QPushButton, QComboBox, QSpinBox, QLabel)
from PySide6.QtUiTools import QUiLoader


class AddProductWindow(QDialog):
    ''' Konstruktor i klasa formularza dodania składnika do produktu '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()



    def init_ui(self):
        ''' załadowanie formularza dodania produktu'''
        loader = QUiLoader()
        self.window = loader.load("addComponentForm.ui", self)
        self.window.setWindowTitle("Dodaj składnik do receptury")
        self.cancelButton = QPushButton()
        self.addButton = QPushButton()
        self.comboBox = QComboBox()
        self.spinBox = QSpinBox()
        self.labelUnit = QLabel()
        self.currentProductMagaizne = [("testhello")]

        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                           database=db,
                           username=user,
                           password=password)

        self.comboUpdate()
        self.window.addButton.clicked.connect(self.accept)
        self.window.cancelButton.clicked.connect(self.reject)
        self.window.comboBox.currentIndexChanged.connect(self.update_label)

    def update_label(self):
        ''' metoda do ustawiania jednostki
        miary danego składnika wybranego
        z comboBox w labelu '''
        self.unit = self.db.execute_query(query=f"SELECT Jednostka_Miary "
                                                f"FROM dbo.Skladniki "
                                                f"WHERE Nazwa_Skladnika = '{self.window.comboBox.currentText()}' ")
        self.unit = self.unit[0]
        self.window.labelUnit.setText(str(self.unit[0]))


    def comboUpdate(self):
        ''' Metoda do aktualizacji składników w liście rozwijanej '''

        self.comboBox.clear()
        try:
            self.comboList = self.db.execute_query(query="SELECT Nazwa_Skladnika FROM dbo.Skladniki;")
            print("comboList:", self.comboList)
            for i, item in enumerate(self.comboList):
                self.window.comboBox.addItem(item[0])
                print("element:", item[0])
        except Exception as e:
            print("Bląd:", e)
        self.update_label()

    def add(self):
        ''' Metoda dodaje produkt do listy zamówienia w określonej ilości,
        zwraca nazwę produktu oraz ilość '''
        product = self.window.comboBox.currentText()
        count = self.window.spinBox.value()
        print("Dodaję:", product, "w ilości:", count, self.unit[0])
        return product, self.unit[0], count


def main():
    ''' Formularz Dodania skladnika do recepty '''
    add_product_form = AddProductWindow()

    # Sprawdź, czy formularz został zakończony poprawnie
    if add_product_form.exec() == QDialog.Accepted:
        product_value = add_product_form.add()
        print("Dodano:", product_value)
    else:
        print("Anulowano dodawanie produktu.")


if __name__ == "__main__":
    main()
