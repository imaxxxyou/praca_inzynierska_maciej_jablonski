from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza edycji dostawcy '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Edytuj Istniejącego Dostawcę")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("editSupplier.ui", self)

        # przypisanie klas PySide do elementów w oknie ustawień
        self.SUPPLIER_ID = QLabel()
        self.pushButtonAdd = QPushButton()
        self.pushButtonCancel = QPushButton()
        self.lineEditName = QLineEdit()
        self.lineEditAdress = QLineEdit()
        self.lineEditNIP = QLineEdit()
        self.lineEditEmail = QLineEdit()
        self.lineEditTel = QLineEdit()

        # przypisanie akcji do przycisków
        self.window.SUPPLIER_ID.setText("ZMIENNA Z BAZY DANYCH")

        self.window.pushButtonAdd.clicked.connect(self.close)
        self.window.pushButtonCancel.clicked.connect(self.close)


        # Ustawiena tabeli aktualnych produktów w zamówieniu



def main():
    '''Formularz edycji dostawcy '''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
