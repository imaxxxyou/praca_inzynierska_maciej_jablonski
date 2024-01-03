from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza dodawania dostawcy '''

    def __init__(self, EVENT_DATE, description):
        super().__init__(parent=None)
        self.description = description
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
        self.window.pushButtonAddEvent.setText("Zapisz Zmiany")
        self.window.pushButtonCancel.clicked.connect(self.close)

        self.window.EVENT_DATE.setText(self.EVENTDATE)
        self.window.label.setText("Edytuj wydarzenie w dniu:")
        self.window.label_2.setText("Opis wydarzenia:")
        self.window.lineEditEventDisc.setText(self.description)

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
        print("Edycja wydarzenia:\n", newdescription, type(newdescription),"\n",
              self.description, type(self.description),"\n",
              self.EVENTDATE, type(self.EVENTDATE))

        self.db.execute_query(
            query=f"UPDATE Events SET event_name = '{newdescription}' "
                  f"WHERE event_name = '{self.description}' "
                  f"AND event_date = '{self.EVENTDATE}';")
        self.db.close_connection
        self.close()


def main(EVENT_DATE, description):
    '''Formularz Edycji Wydarzenia do kalendarza '''
    win = OrderFormWindow(EVENT_DATE=EVENT_DATE, description=description)
    win.exec()


if __name__ == "__main__":
    main()
