from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QLineEdit, QComboBox, QLabel, QSpinBox, QMessageBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza dodawania nowego składnika do bazy danych '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Dodaj nowy składnik do magazynu")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addNewComponentForm.ui", self)

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

        # przypisanie akcji do przycisków
        self.window.addButton.clicked.connect(self.add_to_database)
        self.window.cancelButton.clicked.connect(self.close)

    def add_to_database(self):
        ''' Metoda do dodawania nowego składnika do bazy danych magazynu '''
        print("dodaję produkt....")
        self.name = self.window.lineEditName.text()
        self.desc = self.window.lineEditDesc.text()
        self.unit = self.window.comboBoxUnit.currentText()
        self.price = self.window.doubleSpinBoxPrice.value()
        self.quantity = self.window.spinBox.value()
        print("Dodaję Składnik:", self.name, type(self.name))
        print(self.unit, type(self.unit))
        print("w ilości:", self.quantity, type(self.quantity))
        print("Cena składnika:", self.price, type(self.price))
        try:
            self.db.execute_query(query=f"INSERT INTO dbo.Skladniki "
                                        f"VALUES ('{self.name}','{self.unit}',{self.quantity},{self.price}, '{self.desc}');")

            # Wyskakujący Message Box z informacją
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Information)
            info_box.setWindowTitle("Informacja")
            info_box.setText("Pomyślnie dodano nowy składnik: " + self.name + " do magazynu.")
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()
        except Exception as e:
            print("Błąd: ", e)
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Warning)
            info_box.setWindowTitle("Uwaga")
            info_box.setText("Nie dodano składnika do magazynu.\nSprawdź pisownię i spróbuj jeszcze raz.\n\nBłąd:\n"+str(e))
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()

        self.close()


def main():
    '''Formularz Dodawania nowego składnika do magazynu'''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
