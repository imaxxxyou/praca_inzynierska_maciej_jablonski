from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza dodawania klienta '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Dodaj Klienta")
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

        self.window.label.setText("Dodaj Nowego Klienta:")
        # Przypisanie nowego ID
        self.clientid = self.db.execute_query(query=f"SELECT MAX(ID) AS ID FROM dbo.Klienci;")
        self.clientid = self.clientid[0]
        print(self.clientid, type(self.clientid))
        self.clientid = str(int(self.clientid[0]) + 1)
        self.window.CLIENT_ID.setText(str(int(self.clientid[0])))

        # przypisanie akcji do przycisków
        self.window.pushButtonAdd.clicked.connect(self.add_to_database)
        self.window.pushButtonCancel.clicked.connect(self.close)

    def add_to_database(self):
        ''' Metoda służąca do dodawania nowego klienta do bazy danych '''
        print("Dodaję nowego klienta do bazy danych")

        nazwaklienta = self.window.lineEditName.text()
        adresklienta = self.window.lineEditAdress.text()
        nipklienta = int(self.window.lineEditNIP.text())
        emailklienta = self.window.lineEditEmail.text()
        telklienta  = int(self.window.lineEditTel.text())
        opisklienta = self.window.lineEditDesc.text()
        print("Dodaję klienta:\n   ", nazwaklienta, adresklienta, nipklienta,
              emailklienta, telklienta, opisklienta)

        self.db.execute_query(
            query=f"INSERT INTO dbo.Klienci "
                  f"VALUES ("
                  f"'{nazwaklienta}', "
                  f"'{nipklienta}', "
                  f"'{adresklienta}', "
                  f"'{telklienta}', "
                  f"'{emailklienta}', "
                  f"'{opisklienta}');")

        self.close()


def main():
    '''Formularz Dodawania Klienta '''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
