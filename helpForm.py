from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza pomocy '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Pomoc")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("helpForm.ui", self)

        # przypisanie klas PySide do elementów w oknie
        self.pushButtonClose = QPushButton()

        # przypisanie akcji do przycisków
        self.window.pushButtonClose.clicked.connect(self.close)



def main():
    '''Formularz Pomocy'''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
