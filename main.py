import locale
import sys
import os
import hashlib
import pyodbc
import unreal_stylesheet
from datetime import (datetime)

from PySide6.QtGui import (QIcon,
                           QColor,
                           QTextCharFormat,
                           QAction,
                           QBrush,
                           QMovie)
from PySide6.QtWidgets import (QTableWidget,
                               QTableWidgetItem,
                               QApplication,
                               QLineEdit,
                               QMainWindow,
                               QWidget,
                               QPushButton,
                               QAbstractItemView,
                               QMenu,
                               QLabel,
                               QListWidget,
                               QCalendarWidget,
                               QTabWidget,
                               QMessageBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (Slot,
                            Qt,
                            QTimer,
                            QTime,
                            QDate)
from qtpy import QtGui


class ProtectionData():
    '''Klasa odpowiedzialna za bezpieczeństwo danych '''

    def __init__(self):
        print("Sprawdzam autentyczność...")

    def hash_string(self, input_string: str, filename: str):
        '''Metoda odpowiedzialna za zapisanie
        hashowanego łańcucha znaków (input_string)
        do pliku o nazwie (filename)
        pliki znajdują się w katalogu protect'''
        sha512_hash = hashlib.sha512()
        sha512_hash.update(input_string.encode('utf-8'))
        with open("protect//" + filename + ".txt", "w+") as file:
            file.write(sha512_hash.hexdigest())

    def check_hash(self, input_string: str, filename: str):
        '''Metoda odpowiedzialna za porównanie wprowadzonego
        łańcucha znaków (input_string) znajdującego
        się w pliku o nazwie (filename),
        pliki znajdują się w katalogu protect
        Zwraca wartość boolowską True lub False'''
        sha512_hash = hashlib.sha512()
        sha512_hash.update(input_string.encode('utf-8'))
        hashed_string = sha512_hash.hexdigest()
        with open("protect//" + filename + ".txt", "r") as file:
            file_hash = file.read().strip()

        return hashed_string == file_hash


class Database:
    '''Klasa odpowiedzialna za łączenie się z bazą danych'''

    def __init__(self, server, database, username, password):
        '''Konstruktor połączenia z MS-SQL'''
        self.source_db = database
        self.backup_db = database+"_backup"

        try:
            self.connection = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
            self.cursor = self.connection.cursor()
            print("\nPołączono z bazą danych:", database,
                  "na serwerze:", server, "\nUżytkownik Bazy Danych:", username + "\n")

        except Exception as e:
            print("Błąd połączenia z bazą danych:", e)

    def __del__(self):
        '''Destruktor połączenia z bazą danych MS-SQL'''
        try:
            self.close_connection()
            print("Zamknięto połączenie z bazą danych.")
        except Exception as e:
            print("Błąd przy zamykaniu połączenia z bazą danych", e)

    def execute_query(self, query, ):
        ''' Metoda do wykonywania Query zwraca wynik kwarendy '''
        self.cursor.execute(query)
        print("Wykonuję na bazie danych kwerende: ", query)
        try:
            return self.cursor.fetchall()
        except Exception as e:
            print("Polecenia SQL nie w można wykonać ponieważ:", e)
            self.connection.commit()

    def get_items(self, table):
        '''Metoda pobierająca spis rzeczy,
            które znajdują się w magazynie'''
        try:
            self.cursor.execute("SELECT * FROM " + table)
            return self.cursor.fetchall()
        except Exception as e:
            print("Nie znaleziono tabeli:", table)

    def clone_database(self):
        ''' metoda do tworzenia kopii zapasowej bazy danych '''
        clone_query = f'CREATE DATABASE {self.backup_db} AS COPY OF {self.source_db};'
        self.cursor.execute(clone_query)
        self.cursor.commit()
        self.close_connection()

    def backup_database(self):
        ''' metoda do przywracania kopii bazy danych '''
        restore_query = f'RESTORE DATABASE {self.source_db} FROM DATABASE_SNAPSHOT = \'{self.backup_db}\';'
        self.cursor.execute(restore_query)
        self.cursor.commit()
        self.close_connection()

    def close_connection(self):
        ''' Metoda zamykająca połączenie z bazą danych '''
        self.cursor.close()
        self.connection.close()


class MainWindow(QMainWindow):
    '''Konstruktor głównego okna programu'''

    def __init__(self, db):
        super().__init__(parent=None)
        self.db = db
        self.init_ui()

    def scale_app(self):
        ''' Metoda do animacji okna podczas uruchomienia programu '''
        _scale = 1
        while True:
            self.setFixedSize(200 + _scale, 300 + _scale)
            if _scale >= 800:
                break

    def init_ui(self):
        ''' Metoda uruchamiająca GUI '''
        # Inicjalizacja Widgetów PySide6
        self.setWindowTitle("Herbal Store - Maciej Jabłoński - Praca Inżynierska - UJD w Częstochowie")
        self.icon = QIcon("forms/HerbalStoreLogo.png")
        self.setWindowIcon(self.icon)
        print(self.geometry())

        self.setGeometry(0, 0, 1400, 900)
        # self.showMaximized()
        # self.scale_app()

        # Dopisanie parentów do odpowiednich pól
        self.window = QWidget()
        self.window.QOpenElementButton = QPushButton()
        self.window.lineEdit = QLineEdit()
        self.window.tableWidget = QTableWidget()
        self.window.connectStatus = QLabel()
        self.window.itemCountLabel = QLabel()
        self.window.orderCountLabel = QLabel()
        self.window.clientsCountLabel = QLabel()
        self.window.ingredientsCountLabel = QLabel()
        self.actualItem = []
        self.listVat = QListWidget()
        self.listWZ = QListWidget()
        self.window.settingsButton = QPushButton()
        self.window.helpButton = QPushButton()
        self.window.closeButton = QPushButton()
        self.window.calendarWidget = QCalendarWidget()
        self.window.userButton = QPushButton()
        self.window.tabOrders = QTabWidget()
        self.window.listWidgetEvent = QListWidget()
        self.window.EVENT_DATE = QLabel()
        self.window.pushButtonAddEvent = QPushButton()
        self.window.pushButtonEditEvent = QPushButton()
        self.window.pushButtonDelEvent = QPushButton()
        self.window.label = QLabel()
        self.window.pushButtonRefresh = QPushButton()
        self.window.pushButtonOpenLocalization = QPushButton()

        # Załadowanie UserInterface (UI)
        loader = QUiLoader()
        self.window = loader.load("mainwindow.ui", self)

        # Ładowanie pliku GIF
        movie = QMovie("teapot.gif")
        # Ustawianie gifa na etykiecie
        self.window.label.setMovie(movie)
        # Rozpoczęcie odtwarzania gifa
        movie.start()

        # ustawienie statusu połączenia na Offline
        self.window.connectStatus.setText("Brak połączenia z serwerem bazy danych")
        self.window.connectStatus.setStyleSheet("color: red")

        # Dodanie zegara i daty
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)  # odświeżanie co 1000ms, czyli co sekundę
        self.showTime()

        # zaladowanie listy wydarzeń po uruchomieniu programu
        self.selected_date = self.window.calendarWidget.selectedDate()
        self.get_event()
        self.calendarEventsSetBG()

        # Przycisk odswieżenia danych
        self.window.pushButtonRefresh.clicked.connect(self.load_table)
        # Przycisk otwierania lokalizacji produktu
        self.window.pushButtonOpenLocalization.clicked.connect(self.open_loc)

        # Ustawienia klendarza zaznaczenie dzisiejszej daty
        self.current_date = QDate.currentDate()
        self.window.calendarWidget.setSelectedDate(self.current_date)
        self.format = QTextCharFormat()
        self.format.setBackground(QBrush(QColor(25, 112, 194)))  # Ustawienie koloru na dzisiejszy dzień
        self.window.calendarWidget.setDateTextFormat(self.current_date, self.format)

        # do testów kalendarza
        # Ustawienie tła dla dni realizacji najbliższych zamówień
        # self.orderFormatDate = QTextCharFormat()
        # self.orderFormatDate.setBackground(QColor(223, 245, 100))
        # self.window.calendarWidget.setDateTextFormat(QDate(2023,11,11), self.orderFormatDate)

        # Załadowanie danych do tabel
        # oraz w metodzie load_table()Załadowanie listy dokumentów z lokalnego komputera
        self.load_table()

        # Połączenie sygnałów
        # self.window.QOpenElementButton.clicked.connect(self.open_Element)
        self.connect_Search_Signals()
        self.window.settingsButton.clicked.connect(self.openSettings)
        self.window.helpButton.clicked.connect(self.openHelp)
        self.window.closeButton.clicked.connect(self.close)
        self.window.userButton.clicked.connect(self.production_calculator)
        # wyświetlanie wydarzeń w danym dniu
        self.window.calendarWidget.selectionChanged.connect(self.show_date)
        self.window.calendarWidget.selectionChanged.connect(self.get_event)
        self.window.pushButtonAddEvent.clicked.connect(self.addEventForm)
        self.window.pushButtonEditEvent.clicked.connect(self.editEventForm)
        self.window.pushButtonDelEvent.clicked.connect(self.delete_event_from_list)
        # obsuga podwójnegp klikniecia dla tabel
        self.window.listWidgetEvent.itemDoubleClicked.connect(self.editEventForm)
        self.window.tableWidget.itemDoubleClicked.connect(self.open_loc)
        self.window.tableOrders.itemDoubleClicked.connect(self.editOrder)

        # Ustawienie domyślne radiobuttonów
        self.window.search_by_nameRadioButton.setChecked(True)
        self.window.search_by_Supplier_NameRadioButton.setChecked(True)
        # DOPISAC RESZTE USTAWIEŃ DOMYŚLINYCH WYSZUKIWANIA RADIOBUTTONÓW

        # Uruchomienie Aplikacji
        self.set_table_style()
        self.window.tableOrders.setFocus()
        self.show()

    def set_table_style(self):
        ''' Metoda do ustawienia stylizacji tabeli '''
        # Ustawienia wyświetlania się tabel
        # Tabela Produkty
        self.window.tableWidget.verticalHeader().hide()
        self.window.tableWidget.resizeColumnsToContents()
        self.window.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.window.tableWidget.setWordWrap(True)
        self.window.tableWidget.resizeRowsToContents()
        # Stylizacja nagłówków i siatki Tabela Produkty
        self.window.tableWidget.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 2px;
            }
            QHeaderView::section {
                background-color: #03849e;
                color: white;
                padding: 2px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)

        # Tabela Zamówienia
        self.window.tableOrders.verticalHeader().hide()
        self.window.tableOrders.resizeColumnsToContents()
        self.window.tableOrders.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.window.tableOrders.setWordWrap(True)
        self.window.tableOrders.resizeRowsToContents()

        # Stylizacja nagłówków i siatki Tabela Zamówienia
        self.window.tableOrders.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 2px;
            }
            QHeaderView::section {
                background-color: #03849e;
                color: white;
                padding: 2px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)

        # Tabela archiwum zamówień
        self.window.tableOrders_archive.verticalHeader().hide()
        self.window.tableOrders_archive.resizeColumnsToContents()
        self.window.tableOrders_archive.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.window.tableOrders_archive.setWordWrap(True)
        self.window.tableOrders_archive.resizeRowsToContents()

        # Stylizacja nagłówków i siatki Tabela Zamówienia
        self.window.tableOrders_archive.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 2px;
            }
            QHeaderView::section {
                background-color: #03840e;
                color: white;
                padding: 2px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)

        # Tabela Składniki
        self.window.tableSuppliers.verticalHeader().hide()
        self.window.tableSuppliers.resizeColumnsToContents()
        self.window.tableSuppliers.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.window.tableSuppliers.setWordWrap(True)
        self.window.tableSuppliers.resizeRowsToContents()

        # Stylizacja nagłówków i siatki Tabela Składniki
        self.window.tableSuppliers.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 2px;
            }
            QHeaderView::section {
                background-color: #03849e;
                color: white;
                padding: 2px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)
        # Tabela Klienci
        self.window.tableClients.verticalHeader().hide()
        self.window.tableClients.resizeColumnsToContents()
        self.window.tableClients.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.window.tableClients.setWordWrap(True)
        self.window.tableClients.resizeRowsToContents()

        # Stylizacja nagłówków i siatki Tabela Klienci
        self.window.tableClients.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                gridline-width: 2px;
            }
            QHeaderView::section {
                background-color: #03849e;
                color: white;
                padding: 2px;
                font-size: 12px;
                font-weight: bold;
                border-style: none;
                border-bottom: 1px solid black;
                border-right: 1px solid black;
                text-align: center;
            }
        """)

    def load_table(self):
        '''metoda do ladowania danych do tabeli'''
        try:
            countItems = self.load_Data(data=self.window.tableWidget, table="dbo.Produkty")
            countOrders = self.load_Data(data=self.window.tableOrders, table="dbo.Zamowienia")
            countSupplier = self.load_Data(data=self.window.tableSuppliers, table="dbo.Skladniki")
            countClients = self.load_Data(data=self.window.tableClients, table="dbo.Klienci")
            countOrdersArchive = self.load_Data(data=self.window.tableOrders_archive, table="dbo.zamowienia_archiwum")
            self.window.itemCountLabel.setText("Ilość produktów: " + str(countItems))
            self.window.orderCountLabel.setText("Ilość zamówień w realizacji: " + str(countOrders))
            self.window.ingredientsCountLabel.setText("Ilość składników: " + str(countSupplier))
            self.window.clientsCountLabel.setText("Ilość klientów: " + str(countClients))
            self.set_table_style()
        except Exception as e:
            print("Błąd", e)
        self.load_documents()

    def open_loc(self):
        ''' metoda do otwierania lokalizacji z pliku localization.py
            pobiera koordynaty z tabeli localization za pomnocą id produktu
            zaznaczonego aktualnie w tabeli
        '''
        print("Otwieram lokalizację produktu.")
        import open_localization
        try:
            values = self.selection_row(table=self.window.tableWidget)
        except:
            self.info_box("Uwaga!", "Nie zaznaczono żadnego produktu.")
        try:
            if len(values) > 0:
                open_localization.main(values)
            else:
                self.info_box("Uwaga!", "Nie zaznaczono żadnego produktu.")
        except:
            self.info_box("Uwaga!", "Podany produkt nie ma zaznaczonej lokalizacji")

    def info_box(self, title, msg):
        ''' metoda do tworzenia i uruchamiania okienka z infromacją;
        title-tytuł okna, msg-informacja w oknie'''
        info_box = QMessageBox()
        info_box.setIcon(QMessageBox.Icon.Warning)
        info_box.setWindowTitle(title)
        info_box.setText(msg)
        info_box.addButton(QMessageBox.StandardButton.Ok)
        info_box.exec()

    def editEventForm(self):
        ''' metoda służąca do uruchomienia okienka z edycją wydarzenia '''
        print("Uruchamiam okno z edycją wydarzenia.")
        import editEventForm
        # Ustawienie zmiennej do przesłania do formularza tworzenia wydarzenia
        EVENT_DATE = self.selected_date.toString('yyyy-MM-dd')
        description = self.window.listWidgetEvent.currentItem().text()
        print("Opis wydarzenia do edycji:", description)
        editEventForm.main(EVENT_DATE=EVENT_DATE,
                           description=description)
        # Odświeżanie listy po edycji
        self.get_event()
        self.calendarEventsSetBG()

    def delete_event_from_list(self):
        ''' metoda sluzaca do usuwania wpisu z bazdy danych zaznaczonego wydarzenia w liscie wydarzeń '''
        deleteitem = self.window.listWidgetEvent.currentItem().text()
        eventdate = self.selected_date.toString('yyyy-MM-dd')
        print("Usuwam element:", deleteitem)
        try:
            self.db.execute_query(
                query=f"DELETE FROM Events "
                      f"WHERE event_name = '{deleteitem}' "
                      f"AND event_date = '{eventdate}';")
            self.get_event()
        except Exception as e:
            print("błąd w zapytaniu do bazy danych przy usuwaniu wydarzenia z listy:", e)

    def addEventForm(self):
        ''' metoda służąca do uruchomienia okienka z dodaniem wydarzenia '''
        print("Uruchamiam okno z dodaniem wydarzenia.")
        import addEventForm
        # Ustawienie zmiennej do przesłania do formularza tworzenia wydarzenia
        EVENT_DATE = self.selected_date.toString('yyyy-MM-dd')
        addEventForm.main(EVENT_DATE=EVENT_DATE)
        # Odświeżanie listy i kalendarza po edycji
        self.get_event()
        self.calendarEventsSetBG()

    def calendarEventsSetBG(self):
        ''' metoda do ustawiania koloru tła dnia w którym są jakieś wydarzenia '''
        print("Zaznaczam że w dniu", self.selected_date.toString(), "są jakieś wydarzenia.")
        try:
            list_event_setBG = self.db.execute_query("SELECT DISTINCT event_date FROM Events;")
        except Exception as e:
            print("Nie udało się wykonać kwerendy:", e)
            list_event_setBG = []
        # Ustawienie tła dla dni realizacji najbliższych zamówień
        for events in list_event_setBG:
            # Konwersja daty z bazy danych do obiektu QDate
            # print("Event przed konwersją :", events, type(events))
            events = events[0]
            qdate = QDate(events.year, events.month, events.day)
            # print("Event:", qdate, type(qdate))
            self.orderFormatDate = QTextCharFormat()
            self.orderFormatDate.setBackground(QColor(240, 240, 100))
            self.window.calendarWidget.setDateTextFormat(qdate, self.orderFormatDate)

    def show_date(self):
        ''' metoda zwraca aktualnie zaznaczoną datę w calendarWidget '''

        cal = self.sender()
        self.selected_date = cal.selectedDate()
        print(f"Aktualnie zaznaczona data: {self.selected_date.toString('yyyy-MM-dd')}")
        self.calendarEventsSetBG
        return self.selected_date.toString('yyyy-MM-dd')

    def get_event(self):
        ''' metoda sluzaca do aktualizowania listy wydarzeń z danego dnia '''
        EVENT_DATE = self.selected_date.toString('yyyy-MM-dd')
        print("self.Event_date =", EVENT_DATE, type(EVENT_DATE))
        # stworzenie listy z bazy danych
        try:
            list = self.db.execute_query(
                query=f"SELECT event_name FROM dbo.Events WHERE event_date = '{EVENT_DATE}'"
            )
        except Exception as e:
            print("Nie udało się wykonać kwerendy na bazie danych ponieważ:", e)
            list = []
        print("Pobrana lista wydarzeń w dniu", EVENT_DATE, list)
        self.window.listWidgetEvent.clear()
        for event in list:
            self.window.listWidgetEvent.addItem(event[0])
        self.window.EVENT_DATE.setText(EVENT_DATE)
        self.calendarEventsSetBG()

    def edit_client(self):
        ''' Metoda otwierająca formularz edytowania klienta '''
        print("Otwieram okno - edycja klienta")
        import editClient
        values = self.selection_row(table=self.window.tableClients)
        editClient.main(values)
        self.load_table()

    def add_client(self):
        ''' Metoda służąca do otwierania formularza dodawania nowego klienta '''
        print("Otwieram okno - dodawanie nowego klienta")
        import addClient
        addClient.main()
        self.load_table()

    def edit_supplier(self):
        ''' Metoda otwierająca formularz edytowania dostawcy '''
        print("Otwieram okno - edycję dostawcy")
        import editSupplier
        editSupplier.main()
        self.load_table()

    def add_supplier(self):
        ''' Metoda otwierająca formularz dodawania dostawcy '''
        print("Otwieram okno - dodawanie dostawcy")
        import addSupplier
        addSupplier.main()
        self.load_table()

    def selection_row(self, table):
        ''' Metoda do pobierania danych z aktualnie
        zaznaczonego wiersza w tabeli;
        zmienna table = tabela w programie ,
        metoda zwraca listę elementów {values} 0-id, 1-nazwa itd'''
        selected_item = table.selectedItems()
        for item in selected_item:
            if len(selected_item) > 0:
                # print("Zaznaczony wiersz:", selected_item[0].row(), type(item))
                selected_row = selected_item[0].row()
                values = []
                for col in range(table.columnCount()):
                    item = table.item(selected_row, col)
                    values.append(item.text())

        print("Elementy zaznaczone:", values)
        return values

    def del_component(self):
        ''' metoda do usuwania produktu '''
        values = self.selection_row(table=self.window.tableSuppliers)
        reply = QMessageBox.question(self, 'Potwierdzenie Usunięcia',
                                     'Czy na pewno chcesz usunąć ten składnik\n' + values[1] + ' ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.execute_query(query=f"DELETE FROM dbo.Produkty_Skladniki "
                                        f"WHERE id_skladnika = {values[0]}")
            self.db.execute_query(query=f"DELETE FROM dbo.Skladniki "
                                        f"WHERE id = {values[0]};")
            print('Pozycja usunięta!')
        else:
            print('Usunięcie anulowane.')
        self.load_table()

    def del_client(self):
        ''' metoda do usuwania klienta z bazy danych '''
        values = self.selection_row(table=self.window.tableClients)
        reply = QMessageBox.question(self, 'Potwierdzenie Usunięcia',
                                     'Czy na pewno chcesz usunąć klienta\n' + values[1] + ' ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.execute_query(query=f"DELETE FROM dbo.Klienci "
                                        f"WHERE id = {values[0]};")
            print('Pozycja usunięta!')
        else:
            print('Usunięcie anulowane.')
        self.load_table()

    def del_unit(self):
        ''' metoda do usuwania produktu '''
        values = self.selection_row(table=self.window.tableWidget)
        reply = QMessageBox.question(self, 'Potwierdzenie Usunięcia',
                                     'Czy na pewno chcesz usunąć ten produkt\n' + values[1] + ' ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.execute_query(query=f"DELETE FROM dbo.Lokalizacja_Produktu "
                                        f"WHERE ID_produktu = {values[0]}")
            self.db.execute_query(query=f"DELETE FROM dbo.Produkty_Skladniki "
                                        f"WHERE id_produktu = {values[0]}")
            self.db.execute_query(query=f"DELETE FROM dbo.Produkty "
                                        f"WHERE id = {values[0]};")
            print('Pozycja usunięta!')
        else:
            print('Usunięcie anulowane.')
        self.load_table()

    def edit_component(self):
        ''' Metoda otwierająca formularz dodawania produktu'''
        print("Otwieram okno - edycja produktu.")
        import editNewComponent
        # napisac kod, ktory pobiera id zaznaczonego wiersza w aktywnej tabeli
        # przekazac id_produktu do uruchomienia formularza edycji zmienna (index)
        values = self.selection_row(table=self.window.tableSuppliers)
        editNewComponent.main(values)
        self.load_table()

    def edit_unit(self):
        ''' Metoda otwierająca formularz dodawania produktu'''
        print("Otwieram okno - edycja produktu.")
        import editUnitForm
        # napisac kod, ktory pobiera id zaznaczonego wiersza w aktywnej tabeli
        # przekazac id_produktu do uruchomienia formularza edycji zmienna (index)
        values = self.selection_row(table=self.window.tableWidget)
        editUnitForm.main(values)
        self.load_table()

    def addNewUnit(self):
        ''' Metoda otwierająca formularz dodawania produktu'''
        print("Otwieram okno - dodanie nowego produktu.")
        import addNewUnitForm
        addNewUnitForm.main()
        self.load_table()

    def production_calculator(self):
        ''' Metoda do otwierania kalkulatora produkcji'''
        import production
        production.main()

    def openHelp(self):
        ''' Metoda otwierająca formularz pomoc '''
        print("Otwieram formularz pomoc")
        import helpForm
        helpForm.main()

    def openSettings(self):
        ''' Metoda otwierająca formularz ustawień '''
        print("Otwieram okno ustawień")
        import settingsForm
        settingsForm.main()

    def delVatfile(self):
        ''' metoda do usuwania zaznaczonej faktury vat '''
        file = self.window.listVat.currentItem().text()
        path = os.getcwd()
        fullpath = os.remove(path + "//Dokumenty//Faktury Vat//" + file + ".xlsx")
        print("Usuwam:", fullpath)
        # Załadowanie listy dokumentów z lokalnego komputera
        self.load_documents()

    def openVatDocsFile(self):
        ''' meotda do otwioerania zaznaczonej faktury Vat '''
        file = self.window.listVat.currentItem().text()
        path = os.getcwd()
        fullpath = os.startfile(path + "//Dokumenty//Faktury Vat//" + file + ".xlsx")
        print("Otwieram:", fullpath)

    def openWZDocsFile(self):
        ''' meotda do otwioerania zaznaczonej WZ '''
        file = self.window.listWZ.currentItem().text()
        path = os.getcwd()
        fullpath = os.startfile(path + "//Dokumenty//WZ//" + file + ".xlsx")
        print("Otwieram:", fullpath)

    def openPZDocsFile(self):
        ''' meotda do otwioerania zaznaczonej PZ '''
        file = self.window.listPZ.currentItem().text()
        path = os.getcwd()
        fullpath = os.startfile(path + "//Dokumenty//PZ//" + file + ".xlsx")
        print("Otwieram:", fullpath)

    def archive_order(self):
        ''' metoda do archiwizowania zaznaczonego zamówienia '''
        values = self.selection_row(table=self.window.tableOrders)
        print("Values:", values)
        print("archiwizuje zamówienie")
        if ("Opłacone" in values and "Zrealizowane" in values) or "Anulowane" in values:
            print("Archiwizuję zamówienie o id:", values[0])
            self.db.execute_query(query=f"SET IDENTITY_INSERT dbo.zamowienia_archiwum ON;")
            self.db.execute_query(
                query=f"INSERT INTO dbo.zamowienia_archiwum (ID,Klient,Adres_Dostawy,Data_Zamowienia, "
                      f"Data_realizacji,Kwota_zamowienia,status_zamowienia,status_platnosci, "
                      f"data_platnosci,forma_wysylki,uwagi) "
                      f"SELECT ID,Klient,Adres_dostawy,Data_zamowienia, "
                      f"Data_realizacji,Kwota_zamowienia,status_zamowienia,status_platnosci, "
                      f"data_platnosci,forma_wysylki,uwagi "
                      f"FROM dbo.Zamowienia "
                      f"WHERE id = {values[0]};")
            self.db.execute_query(query=f"SET IDENTITY_INSERT dbo.zamowienia_archiwum OFF;")
            self.db.execute_query(query=f"DELETE FROM dbo.Zamowienia WHERE id = {values[0]};")
            self.load_table()
        else:
            info_box = QMessageBox()
            info_box.setIcon(QMessageBox.Icon.Warning)
            info_box.setWindowTitle("Nie można zarchiwizować zamówienia.")
            info_box.setText("Zamówienie nie zostało jeszcze zrealizowane!")
            info_box.addButton(QMessageBox.StandardButton.Ok)
            info_box.exec()

    def dearchive_order(self):
        ''' metoda która przywraca zamówienie z archiwum do tabeli zamowień "w realizacji" '''
        print("przywracam zamówienie z archiwum")
        values = self.selection_row(self.window.tableOrders_archive)
        print("Przywracam zamowienie o id:", values[0])
        self.db.execute_query(query=f"SET IDENTITY_INSERT dbo.zamowienia ON;")
        self.db.execute_query(query=f"INSERT INTO dbo.zamowienia (ID,Klient,Adres_Dostawy,Data_Zamowienia, "
                                    f"Data_realizacji,Kwota_zamowienia,status_zamowienia,status_platnosci, "
                                    f"data_platnosci,forma_wysylki,uwagi) "
                                    f"SELECT ID,Klient,Adres_dostawy,Data_zamowienia, "
                                    f"Data_realizacji,Kwota_zamowienia,status_zamowienia,status_platnosci, "
                                    f"data_platnosci,forma_wysylki,uwagi "
                                    f"FROM dbo.zamowienia_archiwum "
                                    f"WHERE id = {values[0]};")
        self.db.execute_query(query=f"SET IDENTITY_INSERT dbo.zamowienia OFF;")
        self.db.execute_query(query=f"DELETE FROM dbo.zamowienia_archiwum WHERE id = {values[0]};")
        self.load_table()

    def delOrder(self):
        ''' metoda do usuwania zamówienia '''
        values = self.selection_row(table=self.window.tableOrders)
        reply = QMessageBox.question(self, 'Potwierdzenie Usunięcia',
                                     'Czy na pewno chcesz usunąć zaznaczone zamówienie\n' + values[1] + ' ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("usuwam zamowienie")
            # przywracanie stanu magazynowego produktu z ilosci ktora byla w zamowieniu po usunięciu zamówienia
            quantity = self.db.execute_query(query=f"SELECT id_produktu, ilosc "
                                                   f"FROM dbo.zamowione_produkty "
                                                   f"WHERE id_zamowienia = {values[0]};")
            print("QUANTITY:", quantity)
            for product in quantity:
                old_quantity = self.db.execute_query(
                    query=f"SELECT Dostepna_ilosc FROM dbo.Produkty WHERE id = {product[0]};")
                new_quantity = int(product[1]) + int(old_quantity[0][0])
                self.db.execute_query(query=f"UPDATE dbo.Produkty "
                                            f"SET Dostepna_ilosc = {int(new_quantity)} "
                                            f"WHERE id = {product[0]}")

            self.db.execute_query(query=f"DELETE FROM dbo.Zamowienia "
                                        f"WHERE ID = {values[0]}")
            self.db.execute_query(query=f"DELETE FROM dbo.zamowione_produkty "
                                        f"WHERE id_zamowienia = {values[0]}")

            print('Pozycja usunięta!')
        else:
            print('Usunięcie anulowane.')

        self.load_table()

    def editOrder(self):
        ''' metoda do otwierania i edycji zamówienia '''
        print("edit order")
        import editOrder
        values = self.selection_row(self.window.tableOrders)
        print("Values:", values)
        editOrder.main(values)
        # dopisac kod otwierania i edycji zamowienia
        self.load_table()

    def newOrder(self):
        ''' Metoda do tworzenia nowego zamówienia '''
        print("Otwieram formularz nowego zamówienia.")
        import orderForm
        orderForm.main()
        self.load_table()

    # A może dokumenty zapisywać w pdf albo w bazie danych ???? !!!!
    def printVAT(self):
        ''' Metoda przygotowywująca fakturę VAT gotową do druku,
        oraz zapisująca ją do folderu z fakturami '''
        print("Tworzę fakturę Vat")
        import openpyxl
        # ustawienie zmiennych
        values = self.selection_row(self.window.tableOrders)
        print("Values:", values)
        products = self.db.execute_query(query=f"SELECT P.Nazwa_Produktu, P.Cena, ZP.ilosc "
                                               f"FROM dbo.zamowione_produkty ZP "
                                               f"JOIN dbo.Produkty P ON ZP.id_produktu = P.ID "
                                               f"WHERE ZP.id_zamowienia = {values[0]}")
        print(products)
        vat_Nr = 1
        for element in os.listdir("Dokumenty//Faktury Vat//"):
            pelna_sciezka = os.path.join("Dokumenty//Faktury Vat//", element)
            if os.path.isfile(pelna_sciezka):  # Sprawdzamy, czy to plik
                vat_Nr += 1
        print("Numer faktury:", vat_Nr)

        client_Name = str(values[1])
        client_Adress = str(values[2])
        nip = self.db.execute_query(query=f"SELECT NIP FROM dbo.Klienci WHERE Nazwa_Klienta = '{values[1]}';")
        client_NIP = str(nip[0][0])

        # obliczanie daty i przypisanie do zmiennych
        today = datetime.now().date()
        date_14_days = today  # + timedelta(days=14)
        # otwieranie pliku excel
        file_path = "docs//FakturaVAT.xlsx"
        workbook = openpyxl.load_workbook(file_path)
        # wpisujemy odpowiednie dane do komórek w excel
        sheet = workbook.active
        sheet['F1'] = "VAT/Z/" + str(vat_Nr) + "/" + today.strftime("%Y")
        sheet['B12'] = client_Name
        sheet['B13'] = client_Adress
        sheet['B14'] = client_NIP
        sheet['G4'] = today.strftime("%d-%m-%Y")
        sheet['G5'] = date_14_days.strftime("%d-%m-%Y")
        sheet['G6'] = today.strftime("%d-%m-%Y")

        # pętla for odpowiedzialna za wpisanie produktów wierszów na fakturze
        for i, item in enumerate(products):
            sheet[f"A{20 + i}"] = str(i + 1)
            sheet[f"B{20 + i}"] = str(item[0])
            sheet[f"C{20 + i}"] = item[2]
            sheet[f"D{20 + i}"] = item[1]

        new_Name = ("Dokumenty//Faktury Vat//" + "Faktura nr " + str(vat_Nr) +
                    " z dnia " + str(today.strftime("%d-%m-%Y")) + " dla " + client_Name + ".xlsx")
        print("Zapisuję fakturę pod nazwą:", new_Name)

        workbook.save(new_Name)
        workbook.close()
        self.loadDocs(list=self.window.listVat, path="Dokumenty//Faktury Vat//")
        path = os.getcwd()
        os.startfile(path + "//" + new_Name)

    def load_documents(self):
        ''' metoda do ładowania dokumentów z lokalnego komputera '''
        # VAT
        self.loadDocs(list=self.window.listVat, path="Dokumenty//Faktury Vat//")
        # WZ
        self.loadDocs(list=self.window.listWZ, path="Dokumenty//WZ//")

    def loadDocs(self, list, path):
        ''' metoda słłużąca do ładowania listy dokumentów bez rozszerzenia '''
        print("Ładuję listę dokumnetów: " + path)
        self.window.list = list
        self.window.list.clear()
        for plik in os.listdir(path):
            if os.path.isfile(os.path.join(path, plik)):
                nazwa_bez_rozszerzenia, rozszerzenie = os.path.splitext(plik)
                self.window.list.addItem(nazwa_bez_rozszerzenia)

    def changePaymentStatus(self, status):
        ''' metoda do zmiany statusu płatności zamówienia '''
        selected_items = self.window.tableOrders.selectedItems()
        orderid = selected_items[0].text()
        now = datetime.now().strftime("%Y-%m-%d")
        print("Zmieniam status zamówienia na:", status, "id zamówienia:", orderid, "data:", now, type(now))
        if status == "Oczekuje":
            self.changeOrderStatus(status="W trakcie realizacji")
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_platnosci = '{status}', data_platnosci = NULL "
                                        f"WHERE id = {orderid};")
        elif status == "Opłacone":
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_platnosci = '{status}', data_platnosci = GETDATE() "
                                        f"WHERE id = {orderid};")
            check = self.db.execute_query(query=f"SELECT status_zamowienia FROM dbo.Zamowienia WHERE id = {orderid}")
            print("Sprawdzam status zamówienia:", check[0][0])
            if check[0][0] == "Anulowane":
                self.changeOrderStatus(status="W trakcie realizacji")
        else:
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_platnosci = '{status}', data_platnosci = NULL "
                                        f"WHERE id = {orderid};")
            check = self.db.execute_query(query=f"SELECT status_zamowienia FROM dbo.Zamowienia WHERE id = {orderid}")
            print("Sprawdzam status zamówienia:", check[0][0])
            if check[0][0] != "Anulowane":
                self.changeOrderStatus(status="Anulowane")

        self.load_table()

    def changeOrderStatus(self, status):
        ''' Metoda do zmiany statusu zamówienia '''
        # Napisać kod, który pobierze id aktualnie zaznaczonego wiersza,
        # oraz zaktualizuje bazę danych o nowy status zamowienia
        selected_items = self.window.tableOrders.selectedItems()
        orderid = selected_items[0].text()
        now = datetime.now().strftime("%Y-%m-%d")
        print("Zmieniam status zamówienia na:", status, "id zamówienia:", orderid, "data:", now, type(now))

        if status == "Zapakowane":
            print("Zmieniam status na zapakowane, sciagam ilosc potrzebnych skladników ze stanu produktów")

        if status == "Zrealizowane":
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_Zamowienia = '{status}', Data_Realizacji = GETDATE() "
                                        f"WHERE id = {orderid};")
        elif status == "Anulowane":
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_Zamowienia = '{status}', Data_Realizacji = GETDATE() "
                                        f"WHERE id = {orderid};")
            check = self.db.execute_query(query=f"SELECT status_platnosci FROM dbo.Zamowienia WHERE id = {orderid};")
            print("Sprawdzam status platnosci:", check[0][0])
            if check[0][0] != "Anulowane":
                self.changePaymentStatus(status="Anulowane")
        else:
            self.db.execute_query(query=f"UPDATE dbo.Zamowienia "
                                        f"SET Status_Zamowienia = '{status}', Data_Realizacji = NULL "
                                        f"WHERE id = {orderid};")
        self.load_table()

    def contextMenuEvent(self, event):
        ''' Metoda do uruchamiania Menu rozwijanego z prawego przycisku myszy '''
        contextMenu = QMenu(self)
        orderStatusMenu = QMenu(self)
        if self.window.tableAll.currentIndex() == 2 and self.window.tabWidget_orders.currentIndex() == 0:
            orderAct = contextMenu.addAction("Nowe zamówienie")
            orderAct.triggered.connect(self.newOrder)
            contextMenu.addSeparator()
            orderEditAct = contextMenu.addAction("Edycja zamówienia")
            orderEditAct.triggered.connect(self.editOrder)
            contextMenu.addSeparator()

            # dodanie podmenu do zmianu statusu płatności
            changepaymentAct = contextMenu.addMenu("Zmień status płatności")
            readyAct = QAction("Opłacone", self)
            readyAct.triggered.connect(lambda: self.changePaymentStatus(status="Opłacone"))
            changepaymentAct.addAction(readyAct)
            waitingAct = QAction("Oczekuje", self)
            waitingAct.triggered.connect(lambda: self.changePaymentStatus(status="Oczekuje"))
            changepaymentAct.addAction(waitingAct)
            cancelpaymentAct = QAction("Anulowane", self)
            cancelpaymentAct.triggered.connect(lambda: self.changePaymentStatus(status="Anulowane"))
            changepaymentAct.addAction(cancelpaymentAct)

            # Dodanie podmenu do zmiany statusu zamówienia:
            changeAct = contextMenu.addMenu("Zmień status zamówienia")
            completedAct = QAction("Zrealizowane", self)
            completedAct.triggered.connect(lambda: self.changeOrderStatus(status="Zrealizowane"))
            changeAct.addAction(completedAct)
            inProgressAct = QAction("W trakcie realizacji", self)
            inProgressAct.triggered.connect(lambda: self.changeOrderStatus(status="W trakcie realizacji"))
            changeAct.addAction(inProgressAct)
            canceledAct = QAction("Anulowane", self)
            canceledAct.triggered.connect(lambda: self.changeOrderStatus(status="Anulowane"))
            changeAct.addAction((canceledAct))
            contextMenu.addSeparator()
            delOrderAct = QAction("Usuń zamówienie", self)
            contextMenu.addAction((delOrderAct))
            delOrderAct.triggered.connect(self.delOrder)
            contextMenu.addSeparator()
            vatAct = contextMenu.addAction("Wystaw Fakturę VAT")
            vatAct.triggered.connect(self.printVAT)
            archiveAct = contextMenu.addAction("Archiwizuj zamówienie")
            archiveAct.triggered.connect(self.archive_order)
            contextMenu.addSeparator()

        if self.window.tableAll.currentIndex() == 2 and self.window.tabWidget_orders.currentIndex() == 1:
            vatOpenAct = contextMenu.addAction("Pokaż Fakturę VAT")
            vatOpenAct.triggered.connect(self.printVAT)
            dearchiveAct = contextMenu.addAction("Przywróć zamówienie z archiwum")
            dearchiveAct.triggered.connect(self.dearchive_order)
            contextMenu.addSeparator()

        if self.window.tableAll.currentIndex() == 1:
            addProductAct = contextMenu.addAction("Dodaj Produkt")
            addProductAct.triggered.connect(self.addNewUnit)
            editProductAct = contextMenu.addAction("Edytuj Produkt")
            editProductAct.triggered.connect(self.edit_unit)
            contextMenu.addSeparator()
            delProductAct = contextMenu.addAction("Usuń Produkt")
            delProductAct.triggered.connect(self.del_unit)
            contextMenu.addSeparator()
            locProductAct = contextMenu.addAction("Wyświetl lokalizację produktu")
            locProductAct.triggered.connect(self.open_loc)
            # wzAct = contextMenu.addAction("Wydanie Zewnętrzne")
            # wzAct.triggered.connect(self.close)
            contextMenu.addSeparator()
        if self.window.tableAll.currentIndex() == 4:
            addActClient = contextMenu.addAction("Dodaj Nowego Klienta")
            addActClient.triggered.connect(self.add_client)
            editActClient = contextMenu.addAction("Edytuj Dane Klienta")
            editActClient.triggered.connect(self.edit_client)
            contextMenu.addSeparator()
            delActClient = contextMenu.addAction("Usuń Klienta")
            delActClient.triggered.connect(self.del_client)
            contextMenu.addSeparator()
        if self.window.tableAll.currentIndex() == 3:
            addActComponent = contextMenu.addAction("Dodaj Nowy Składnik")
            addActComponent.triggered.connect(self.add_new_component)
            editActComponent = contextMenu.addAction("Edytuj Składnik")
            editActComponent.triggered.connect(self.edit_component)
            contextMenu.addSeparator()
            delActComponent = contextMenu.addAction("Usuń Składnik")
            delActComponent.triggered.connect(self.del_component)
            contextMenu.addSeparator()
        if self.window.tableAll.currentIndex() == 5:
            if self.window.tableDocs.currentIndex() == 0:
                addOpenDocsAction = contextMenu.addAction("Otwórz zaznaczoną fakturę Vat")
                addOpenDocsAction.triggered.connect(self.openVatDocsFile)
                addRmDocsAction = contextMenu.addAction("Usuń zaznaczony dokument")
                addRmDocsAction.triggered.connect(self.delVatfile)
            elif self.window.tableDocs.currentIndex() == 1:
                addOpenDocsAction = contextMenu.addAction("Otwórz zaznaczoną WZ")
                addOpenDocsAction.triggered.connect(self.openWZDocsFile)
                addRmDocsAction = contextMenu.addAction("Usuń zaznaczony dokument")
                addRmDocsAction.triggered.connect(self.close)
            contextMenu.addSeparator()

        helpAct = contextMenu.addAction("Pomoc")
        helpAct.triggered.connect(self.openHelp)
        contextMenu.addSeparator()
        closeAct = contextMenu.addAction("Zamknij Program")
        closeAct.triggered.connect(self.close)

        # Pokaż menu w miejscu kursora
        contextMenu.exec(event.globalPos())

    def add_new_component(self):
        ''' Metoda otwierająca formularz dodawania lub edycji nowego składnika do magazynu '''
        print("Otwieram formularz dodawania lub edycji nowego składnika")
        import addNewComponent
        addNewComponent.main()
        self.load_table()

    def showTime(self):
        ''' Metoda do wyświetlania aktualnego czasu i daty '''
        locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
        currentTime = QTime.currentTime()  # Pobiera aktualny czas
        currentDate = QDate.currentDate()  # Pobiera aktualną datę
        timeText = currentTime.toString('hh:mm:ss')  # Format czasu
        dayOfWeekText = currentDate.toString('dd-MM-yyyy')  # Format daty
        self.window.labelClock.setText(timeText)
        self.window.labelToday.setText(dayOfWeekText.capitalize())

    def connect_Search_Signals(self):
        '''Metoda łączenia sygnałów do możliwości dynamicznego przeszukiwania Tabel'''

        # Sygnał szukania dla Tabeli - Produkty
        self.window.lineEdit.textChanged.connect(lambda: self.filterTable(
            self.window.lineEdit.text(),
            self.window.tableWidget,
            {
                self.window.search_by_nameRadioButton: 1,
                self.window.search_by_supplierRadioButton: 5,
                self.window.search_by_magazineRadioButton: 3
            }
        ))
        # Dodatkowe sygnały dla przycisków radiowych Tabeli - Produkty
        self.window.search_by_nameRadioButton.toggled.connect(lambda: self.filterTable(
            self.window.lineEdit.text(),
            self.window.tableWidget,
            {
                self.window.search_by_nameRadioButton: 1,
                self.window.search_by_supplierRadioButton: 5,
                self.window.search_by_magazineRadioButton: 3
            }
        ))

        # Sygnał szukania dla Tabeli - Składniki
        self.window.lineEditSuppliers.textChanged.connect(lambda: self.filterTable(
            self.window.lineEditSuppliers.text(),
            self.window.tableSuppliers,
            {
                self.window.search_by_Supplier_NameRadioButton: 1,
                self.window.search_by_NIPRadioButton: 2,
                self.window.search_by_AdressRadioButton: 3
            }
        ))
        # Dodatkowe sygnały dla przycisków radiowych Tabeli - Dostawcy
        self.window.search_by_Supplier_NameRadioButton.toggled.connect(lambda: self.filterTable(
            self.window.lineEditSuppliers.text(),
            self.window.tableSuppliers,
            {
                self.window.search_by_Supplier_NameRadioButton: 1,
                self.window.search_by_NIPRadioButton: 2,
                self.window.search_by_AdressRadioButton: 3
            }
        ))

    def load_Data(self, data, table):
        ''' Metoda odpowiedzialna za załadowanie
        elementów z bazy danych do tabel w GUI - nagłowki bedą takie same jak w bazie danych
        data = do czego będzie ładowane
        table = tabela z ktorej bedzie ladowane
        zwraca długość słownika (int) '''
        data.clear()
        items = self.db.get_items(table)
        self.actualItem = items
        print("Pobrana lista z bazy danych:", items)
        # kod programu do obliczania zarobku z zamówień
        if table == "dbo.zamowienia_archiwum":
            calc = 0.0
            for item in items:
                # możliwość rozbudowania o zliczanie zarobku pobierając datę
                # przyda sie do zrobienia raportów
                calc += float(item[5])
                self.calculate = float(calc)
            print("Zarobek ze zrealizowanych zamówień: ", self.calculate, "zł.")
            self.window.labelCalculate.setText(
                f"Zarobek ze zrealizowanych zamówień: <font color='#006400'>{self.calculate:.2f} zł.</font>")

        data.setRowCount(0)
        data.setColumnCount(0)
        if items:  # Sprawdzenie czy lista nie jest pusta
            data.setRowCount(len(items))
            data.setColumnCount(len(items[0]))
            # zmiana nagłówków zgodnie z nagłówkami w bazie danych
            header_labels = [column[0].replace("_", " ") for column in self.db.cursor.description]
            for j, label in enumerate(header_labels):
                # Utwórz nagłówek dla kolumny
                header_item = QTableWidgetItem(label.capitalize())
                header_item.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
                data.setHorizontalHeaderItem(j, header_item)

            for i, row in enumerate(items):
                for j, item in enumerate(row):
                    tableItem = QTableWidgetItem(str(item))
                    # sprawdzenie czy element nie jest pusty
                    if tableItem.text() == "None" or tableItem.text() == "":
                        # print(tableItem.text(), "zamieniam na ------")
                        tableItem = QTableWidgetItem(str("------"))

                    # Zablokowanie możliwości edycji elementu z poziomu wyświetlania Tabeli
                    tableItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                    # kolorowanie komórek w tabelach
                    if i % 2 == 0:
                        tableItem.setBackground(QColor(255, 255, 255))  # Biały
                    else:
                        tableItem.setBackground(QColor(233, 236, 242))  # Bardzo jasny niebieski

                    if item == "Zrealizowane":
                        tableItem.setBackground(QColor(144, 238, 144))  # Jasny zielony
                    elif item == "W trakcie realizacji":
                        tableItem.setBackground(QColor(255, 255, 102))  # Jasny żółty
                    elif item == "Anulowane":
                        tableItem.setBackground(QColor(170, 172, 173))  # Nieciemny szary

                    if item == "Oczekuje":
                        tableItem.setBackground(QColor(255, 255, 102))  # Jasny żółty
                    elif item == "Opłacone":
                        tableItem.setBackground(QColor(144, 238, 144))  # Jasny zielony
                    elif item == "Anulowane":
                        tableItem.setBackground(QColor(170, 172, 173))  # Nieciemny szary

                    # kolorowanie dostępności produktu
                    with open("settings//productlowvalue.txt", "r") as f:
                        dostepnoscproduktu = f.readline()
                    if j == 4 and (data == self.window.tableWidget and int(tableItem.text()) < int(
                            dostepnoscproduktu)) and int(tableItem.text()) > 0:
                        tableItem.setBackground(QColor(255, 255, 102))  # jasny żółty
                    elif j == 4 and data == self.window.tableWidget and int(tableItem.text()) == 0:
                        tableItem.setBackground(QColor(186, 186, 186))  # jasny czerwony
                    elif j == 4 and data == self.window.tableWidget and int(tableItem.text()) >= int(
                            dostepnoscproduktu):
                        tableItem.setBackground(QColor(144, 238, 144))  # jasny zielony
                    elif j == 4 and data == self.window.tableWidget and int(tableItem.text()) < 0:
                        tableItem.setBackground(QColor(245, 130, 130))  # jasny czerwony

                    # kolorowanie dostępności składnika
                    with open("settings//componentlowvalue.txt", "r") as f:
                        dostepnoscproduktu = f.readline()
                    if j == 3 and data == self.window.tableSuppliers and int(tableItem.text()) < int(
                            dostepnoscproduktu) and int(tableItem.text()) > 0:
                        tableItem.setBackground(QColor(255, 255, 102))  # jasny żółty
                    elif j == 3 and data == self.window.tableSuppliers and int(tableItem.text()) == 0:
                        tableItem.setBackground(QColor(186, 186, 186))  # szary
                    elif j == 3 and data == self.window.tableSuppliers and int(tableItem.text()) >= int(
                            dostepnoscproduktu):
                        tableItem.setBackground(QColor(144, 238, 144))  # jasny zielony
                    elif j == 3 and data == self.window.tableSuppliers and int(tableItem.text()) < 0:
                        tableItem.setBackground(QColor(245, 130, 130))  # jasny czerwony

                    data.setItem(i, j, tableItem)

            # Ustawienie Labelu status połączenia
            self.window.connectStatus.setText("Połączono pomyślnie z serwerem bazy danych.")
            self.window.connectStatus.setStyleSheet("color: darkgreen")
            return len(items)
        else:
            return 1

    def filterTable(self, searchText, table, radioButtonMappings):
        ''' Metoda do dynamicznego przeszukiwania wyświetlonej Tabeli, otrzymuje 3 atrybuty
        searchText: poszukiwany tekst (str),
        table: przeszukiwana tabela (QtableWidget),
        radioButtonMappings: po której kolumnie ma szukać (dict)
        wywołujemy ją za pomocą lambdy. '''
        column = 1
        for radioButton, col in radioButtonMappings.items():
            if radioButton.isChecked():
                column = col
                break

        for i in range(table.rowCount()):
            item = table.item(i, column)
            if item:
                table.setRowHidden(i, searchText.lower() not in item.text().lower())

    @Slot(str)
    def open_Element(self):
        ''' metoda do pobierania indeksu aktualnie zaznaczonego produktu, można to zoptymalizować.'''
        self.indexOfElement = self.window.listWidget.selectedItems()[0]
        print("Otwieram element (index elementu = " + str(self.indexOfElement) + " )")


def dbConnectFiles():
    ''' Funkcja odczytująca aktualne ustawienia bazy danych
    zwraca 4 elementy,
    serverName - nazwa serwera;
    DataBaseName - nazwa bazy danych;
    DataBaseUser - nazwa uzytkownika bazy danych;Jednos
    DataBasePassword - haslo do bazy danych,
    obsługa błędów zwraca string do wszystkich zmiennych "false" '''
    print("Ładuję ustawienia dla bazy danych")
    listNames = ["ServerName.txt",
                 "DataBaseName.txt",
                 "DataBaseUserName.txt",
                 "DataBasePassword.txt"]
    try:
        for i, name in enumerate(listNames):

            with open("settings//" + name, "r", encoding="UTF-8") as file:
                if i == 0:
                    serverName = file.readline()
                elif i == 1:
                    DBName = file.readline()
                elif i == 2:
                    DBUser = file.readline()
                elif i == 3:
                    DBPass = file.readline()

        return serverName, DBName, DBUser, DBPass

    except Exception as e:
        print("Nie udało się pobrać danych z plików:", e)
        serverName = "false"
        DBName = "false"
        DBUser = "false"
        DBPass = "false"
        return serverName, DBName, DBUser, DBPass


def setStyle():
    '''Funkcja do ustawienia stylu i animacji loga na początku programu '''
    with open("settings//SetStyle.txt", "r", encoding="UTF-8") as file:
        style = file.readline()
    print("Ustawiam styl: ", style + "\n")

    with open("settings//animationstart.txt", "r") as file:
        animation = file.readline()
    if animation == "True":
        from startingAnimation import logo_animation
        logo_animation()

    return style


def main():
    '''Główna funkcja startowa programu'''

    # Elementy potrzebne do podłaczenia do bazy danych
    # Server = localhost lub Imper
    # database = warehouse
    # username = wh_admin
    # password = administrator

    server, db, user, password = dbConnectFiles()

    db = Database(server=server,
                  database=db,
                  username=user,
                  password=password)

    app = QApplication(sys.argv)

    # Ustawienie motywu wyświetlania programu
    style = setStyle()
    if style == "Dark":
        unreal_stylesheet.setup()
    elif style == "Fusion":
        app.setStyle("Fusion")
    elif style == "Windows":
        app.setStyle("Windows")

    win = MainWindow(db)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
