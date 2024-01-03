from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza edycji klienta '''

    def __init__(self, values):
        super().__init__(parent=None)
        self.values = values
        print("Values:", values)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edytuj Dane Klienta")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addSupplier.ui", self)

        import main
        server, db, user, password = main.dbConnectFiles()

        self.db = main.Database(server=server,
                                database=db,
                                username=user,
                                password=password)


        # przypisanie klas PySide do elementów w oknie ustawień
        self.CLIENT_ID = QLabel()
        self.pushButtonAdd = QPushButton()
        self.pushButtonCancel = QPushButton()
        self.lineEditName = QLineEdit()
        self.lineEditAdress = QLineEdit()
        self.lineEditNIP = QLineEdit()
        self.lineEditEmail = QLineEdit()
        self.lineEditTel = QLineEdit()
        self.lineEditDesc = QLineEdit()

        #Ustawienia danych wejsciowych
        self.window.label.setText("Edytuj Dane Klienta:")
        self.window.CLIENT_ID.setText(str(int(self.values[0])))
        self.window.lineEditName.setText(str(self.values[1]))
        self.window.lineEditNIP.setText(str(self.values[2]))
        self.window.lineEditAdress.setText(str(self.values[3]))
        self.window.lineEditTel.setText(str(self.values[4]))
        self.window.lineEditEmail.setText(str(self.values[5]))
        self.window.lineEditDesc.setText(str(self.values[6]))

        # przypisanie akcji do przycisków
        self.window.pushButtonAdd.setText("Zapisz zmiany")
        self.window.pushButtonAdd.clicked.connect(self.edit_in_database)
        self.window.pushButtonCancel.clicked.connect(self.close)

    def edit_in_database(self):
        ''' Metoda do edcyji klienta w bazie danych'''
        nazwaklienta = self.window.lineEditName.text()
        adresklienta = self.window.lineEditAdress.text()
        nipklienta = int(self.window.lineEditNIP.text())
        emailklienta = self.window.lineEditEmail.text()
        telklienta  = int(self.window.lineEditTel.text())
        opisklienta = self.window.lineEditDesc.text()
        print("Edytuję klienta:\n   ", nazwaklienta, adresklienta, nipklienta,
              emailklienta, telklienta, opisklienta)
        print("Zapisuję zmiany w bazie danych")

        self.db.execute_query(query=f"UPDATE dbo.Klienci "
                                    f"SET Nazwa_Klienta = '{nazwaklienta}', "
                                    f"NIP = '{nipklienta}', "
                                    f"Adres = '{adresklienta}', "
                                    f"Nr_Telefonu = '{telklienta}', "
                                    f"Adres_Email = '{emailklienta}', "
                                    f"Opis = '{opisklienta}' "
                                    f"WHERE ID = {int(self.values[0])};")
        self.close()


def main(values):
    '''Formularz Edycji Klienta '''
    win = OrderFormWindow(values=values)
    win.exec()


if __name__ == "__main__":
    main()
