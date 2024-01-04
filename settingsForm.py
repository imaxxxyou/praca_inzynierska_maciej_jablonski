import subprocess
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QComboBox, QLabel, QSpinBox, QCheckBox,
    QMessageBox)
from PySide6.QtUiTools import QUiLoader


class OrderFormWindow(QDialog):
    ''' Konstruktor i klasa formularza ustawień '''

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        ''' stworzenie formularza '''
        self.orderWindow = QUiLoader()
        self.setWindowTitle("Ustawienia Programu")
        self.icon = QIcon("FormIcon.jpeg")
        self.setWindowIcon(self.icon)
        loader = QUiLoader()
        self.window = loader.load("settingsForm.ui", self)

        # przypisanie klas PySide do elementów w oknie ustawień
        self.lineEditIPAdress = QLineEdit()
        self.lineEditServerPort = QLineEdit()
        self.lineEditServerName = QLineEdit()
        self.lineEditDataBaseName = QLineEdit()
        self.lineEditDataBaseUser = QLineEdit()
        self.lineEditDataBasePassword = QLineEdit()
        self.spinBox = QSpinBox()
        self.spinBox_2 = QSpinBox()
        self.ANIMATION = QCheckBox()

        self.comboBoxProgramMotive = QComboBox()
        self.LICENCE_USER = QLabel()
        self.LICENCE_DATE = QLabel()

        self.pushButtonCancel = QPushButton()
        self.pushButtonSave = QPushButton()

        # przypisanie akcji do przycisków
        self.window.pushButtonCancel.clicked.connect(self.close)
        self.window.pushButtonSave.clicked.connect(self.saveSettings)
        self.window.pushButtonCreateDatabase.clicked.connect(self.create_database)
        self.window.pushButtonCloneDatabase.clicked.connect(self.clone_database)
        self.window.pushButtonBackupDatabase.clicked.connect(self.backup_database)

        # Wpisanie aktualnych ustawień w pola

        self.readActuallSetting()

    def open_connection_to_database(self):
        ''' metoda służąca do otwarcia połączenia do bazy danych '''
        import main
        server, db, user, password = main.dbConnectFiles()
        self.db = main.Database(server=server,
                                database=db,
                                username=user,
                                password=password)

    def create_database(self):
        ''' metoda służąca do tworzenia nowej bazy danych z podanych poświadczeń '''
        print("Tworzę bazę danych")
        try:
            self.open_connection_to_database()
            from main import Database
            Database.create_database(self.db)
        except Exception as e:
            print("Błąd:", e)

    def clone_database(self):
        ''' metoda do tworzenia kopii zapasowej bazy danych '''
        print("Tworzę kopię zapasową bazy danych")
        try:
            self.open_connection_to_database()
            from main import Database
            Database.clone_database(self.db)
        except Exception as e:
            print("Błąd:", e)

    def backup_database(self):
        ''' metoda slużąca do przywracania bazy danych z poprzedniej kopii '''
        print("Przywracam bazę danych z poprzedniej kopii")
        try:
            self.open_connection_to_database()
            from main import Database
            Database.backup_database(self.db)
        except Exception as e:
            print("Błąd:", e)


    def readActuallSetting(self):
        ''' Metoda do oczytania aktualnych ustawień z plików w folderze settings '''
        with open("settings/ServerIPAdress.txt", "r", encoding="UTF-8") as file:
            self.window.lineEditIPAdress.setText(file.readline())
        with open("settings/ServerPort.txt", "r", encoding="UTF-8") as file:
            self.window.lineEditServerPort.setText(file.readline())
        with open("settings/ServerName.txt", "r", encoding="UTF-8") as file:
            self.window.lineEditServerName.setText(file.readline())
        with open("settings/DataBaseName.txt", "r", encoding="UTF-8") as file:
            self.window.lineEditDataBaseName.setText(file.readline())
        with open("settings/DataBaseUserName.txt", "r", encoding="UTF-8") as file:
            self.window.lineEditDataBaseUser.setText(file.readline())
        with open("settings/DataBasePassword.txt", "r", encoding="UTF-8") as file:
            # kod służący do ukrywania widoku hasła w lineEdit
            self.window.lineEditDataBasePassword.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
            self.window.lineEditDataBasePassword.setText(file.readline())
        with open("settings/SetStyle.txt", "r", encoding="UTF-8") as file:
            style = file.readline()
            if style == "Dark":
                self.window.comboBoxProgramMotive.setCurrentIndex(0)
            elif style == "Fusion":
                self.window.comboBoxProgramMotive.setCurrentIndex(1)
            elif style == "Windows":
                self.window.comboBoxProgramMotive.setCurrentIndex(2)
        with open("settings/LicenceUser.txt", "r", encoding="UTF-8") as file:
            self.window.LICENCE_USER.setText(file.readline())
        with open("settings/LicenceDate.txt", "r", encoding="UTF-8") as file:
            self.window.LICENCE_DATE.setText(file.readline())
        with open("settings/productlowvalue.txt", "r") as file:
            self.window.spinBox.setValue(int(file.readline()))
        with open("settings/componentlowvalue.txt", "r") as file:
            self.window.spinBox_2.setValue(int(file.readline()))

        with open("settings/animationstart.txt", "r", encoding="UTF-8") as file:
            animation = file.readline()
            if animation == "True":
                self.window.ANIMATION.setChecked(True)
            else:
                self.window.ANIMATION.setChecked(False)


    def saveSettings(self):
        ''' Metoda zapisująca aktualne ustawienia '''
        print("Zapisuję ustawienia")
        IPadress = self.window.lineEditIPAdress.text()
        with open("settings/ServerIPAdress.txt", "w+", encoding="UTF-8") as file:
            file.writelines(IPadress)
        ServerPort = self.window.lineEditServerPort.text()
        with open("settings/ServerPort.txt", "w+", encoding="UTF-8") as file:
            file.writelines(ServerPort)
        ServerName = self.window.lineEditServerName.text()
        with open("settings/ServerName.txt", "w+", encoding="UTF-8") as file:
            file.writelines(ServerName)
        DataBaseName = self.window.lineEditDataBaseName.text()
        with open("settings/DataBaseName.txt", "w+", encoding="UTF-8") as file:
            file.writelines(DataBaseName)
        DataBaseUser = self.window.lineEditDataBaseUser.text()
        with open("settings/DataBaseUserName.txt", "w+", encoding="UTF-8") as file:
            file.writelines(DataBaseUser)
        DataBasePassword = self.window.lineEditDataBasePassword.text()
        with open("settings/DataBasePassword.txt", "w+", encoding="UTF-8") as file:
            file.writelines(DataBasePassword)

        with open("settings/SetStyle.txt", "w+", encoding="UTF-8") as file:
            style = file.readline()
            if self.window.comboBoxProgramMotive.currentIndex() == 0:
                file.writelines("Dark")
            elif self.window.comboBoxProgramMotive.currentIndex() == 1:
                file.writelines("Fusion")
            elif self.window.comboBoxProgramMotive.currentIndex() == 2:
                file.writelines("Windows")

        # spinboxy do ustawienia powiadamiania o małej ilości produktów i składników
        plv = str(self.window.spinBox.value())
        with open("settings/productlowvalue.txt", "w+") as file:
            file.writelines(plv)
        clv = str(self.window.spinBox_2.value())
        with open("settings/componentlowvalue.txt", "w+") as file:
            file.writelines(clv)

        # Checkbox do animacji
        if self.window.ANIMATION.isChecked():
            animation = str("True")
            with open("settings/animationstart.txt", "w+") as file:
                file.writelines(animation)
        else:
            animation = str("False")
            with open("settings/animationstart.txt", "w+") as file:
                file.writelines(animation)

        # DOPISAĆ RESZTĘ ZAPISU LINE EDITÓW DO PLIKÓW

        # Wyskakujący Message Box z informacją
        info_box = QMessageBox()
        info_box.setIcon(QMessageBox.Icon.Information)
        info_box.setWindowTitle("Informacja")
        info_box.setText("Ustawienia zostaną zaktualizowane przy następnym uruchomieniu programu.")
        info_box.addButton(QMessageBox.StandardButton.Ok)
        info_box.exec()
        self.close()

        # restart aplikacji
        # self.restart_application()

    def restart_application(self):
        ''' metoda do zrestartowania aplikacji '''
        # Pobieranie argumentów przekazanych do skryptu
        script_args = sys.argv
        # Uruchamianie skryptu ponownie
        subprocess.Popen([sys.executable] + script_args)


def main():
    '''Formularz Ustawień '''
    win = OrderFormWindow()
    win.exec()


if __name__ == "__main__":
    main()
