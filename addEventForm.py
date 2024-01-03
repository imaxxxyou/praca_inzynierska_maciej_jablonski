from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza dodawania dostawcy '''

    def __init__(self, EVENT_DATE):
        super().__init__(parent=None)
        self.EVENTDATE = EVENT_DATE
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edytuj wydarzenie")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("addEventForm.ui", self)

        # przypisanie klas PySide do elementów w oknie ustawień
        self.EVENT_DATE = QLabel()


        # przypisanie akcji do przycisków
        print(self.EVENTDATE, type(self.EVENTDATE))
        self.window.pushButtonAddEvent.clicked.connect(self.saveChanges)
        self.window.pushButtonCancel.clicked.connect(self.close)

        self.window.EVENT_DATE.setText(self.EVENTDATE)

    def saveChanges(self):
            ''' metoda do zapisywania zmiany opisu wydarzenia w bazie danych '''
            newdescription = self.window.lineEditEventDisc.text()
            print("Nowy opis do wydarzenia:", newdescription, type(newdescription))
            import main
            server, db, user, password = main.dbConnectFiles()
            self.db = main.Database(server=server,
                                    database=db,
                                    username=user,
                                    password=password)

            self.db.execute_query(
                query=f"INSERT INTO Events (event_name, event_date) "
                      f"VALUES ('{newdescription}', '{self.EVENTDATE}');"
            )
            self.db.close_connection
            self.close()



def main(EVENT_DATE):
    '''Formularz Dodawania Wydarzenia do kalendarza '''
    win = OrderFormWindow(EVENT_DATE=EVENT_DATE)
    win.exec()


if __name__ == "__main__":
    main()
