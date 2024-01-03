from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QLineEdit, QComboBox, QSpinBox, QMessageBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza edycji składnika w bazie danych '''

    def __init__(self, values):
        super().__init__(parent=None)
        self.values = values
        print("VALUES:", values)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edycja składnika")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addNewComponentForm.ui", self)
        self.window.label_7.setText("Edycja składnika")

        # Połączenie do bazy danych
        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                           database=db,
                           username=user,
                           password=password)

        # przypisanie klas PySide do elementów w oknie
        self.addButton = QPushButton()
        self.cancelButton = QPushButton()

        self.lineEditName = QLineEdit()
        self.lineEditDesc = QLineEdit()
        self.comboBoxUnit = QComboBox()
        self.spinBox = QSpinBox()
        self.doubleSpinBoxPrice = QDoubleSpinBox()

        self.window.lineEditName.setText(str(self.values[1]))
        self.window.lineEditDesc.setText(str(self.values[5]))
        self.window.comboBoxUnit.clear()
        with open('docs/units.txt', 'r', encoding="UTF-8") as file:
            # Odczytanie kolejnych linii z pliku
            lines = file.readlines()
            # wprowadzenie wartości do comboBoxUnit
            for line in lines:
                self.window.comboBoxUnit.addItem(line.strip())
        indexUnit = self.window.comboBoxUnit.findText(str(self.values[2]))
        self.window.comboBoxUnit.setCurrentIndex(indexUnit)
        self.window.spinBox.setValue(int(self.values[3]))
        try:
            self.window.doubleSpinBoxPrice.setValue(float(self.values[4]))
        except:
            self.window.doubleSpinBoxPrice.setValue(0.0)
        # przypisanie akcji do przycisków
        self.window.addButton.setText("Zapisz zmiany")
        self.window.addButton.clicked.connect(self.update_database)
        self.window.cancelButton.clicked.connect(self.close)

    def update_database(self):
        ''' Metoda do dodawania nowego składnika do bazy danych magazynu '''
        print("dodaję produkt....")
        self.name = self.window.lineEditName.text()
        self.desc = self.window.lineEditDesc.text()
        self.unit = self.window.comboBoxUnit.currentText()
        self.quantity = self.window.spinBox.value()
        self.price = self.window.doubleSpinBoxPrice.value()
        print("Edytuję Składnik:", self.name, type(self.name))
        print(self.unit, type(self.unit))
        print("w ilości:", self.quantity, type(self.quantity))
        print("Cena jednostkowa składnika:", self.price, type(self.price))
        try:
            self.db.execute_query(query=f"UPDATE dbo.Skladniki "
                                        f"SET "
                                        f"Nazwa_Skladnika = '{self.name}', "
                                        f"Jednostka_Miary = '{self.unit}', "
                                        f"Dostepna_ilosc = {self.quantity}, "
                                        f"Opis = '{self.desc}', "
                                        f"Cena_jednostkowa = {self.price} "
                                        f"WHERE id = {self.values[0]};")

            # Wyskakujący Message Box z informacją
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Information)
            info_box.setWindowTitle("Informacja")
            info_box.setText("Pomyślnie edytowano produkt: "+self.name+".")
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()
        except Exception as e:
            print("Błąd:", e)
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Warning)
            info_box.setWindowTitle("Uwaga")
            info_box.setText("Błąd edycji.\nSprawdź pisownię i spróbuj jeszcze raz.\n\nBłąd:\n"+str(e))
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()

        self.close()

    def read(self):
        ''' Metoda która wczytuje aktualne wartości zaznaczonego składnika '''


def main(values):
    '''Formularz Edycji składnika w bazie danych '''
    win = OrderFormWindow(values)
    win.exec()


if __name__ == "__main__":
    main()
