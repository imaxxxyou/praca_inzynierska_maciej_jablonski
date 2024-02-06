def load_Data(self, data, table):
    ''' Metoda odpowiedzialna za załadowanie
    elementów z bazy danych do GUI
    data = do czego będzie ładowane
    table = tabela z ktorej bedzie ladowane
    zwraca długość słownika (int) '''
    items = self.db.get_items(table)
    self.actualItem = items
    print("Pobrana lista z bazy danych:", items)

    if items:  # Sprawdzenie czy lista nie jest pusta
        data.setRowCount(len(items))
        data.setColumnCount(len(items[0]))

        for i, row in enumerate(items):
            for j, item in enumerate(row):
                tableItem = QTableWidgetItem(str(item))
                # Zablokowanie możliwości edycji elementu z poziomu wyświetlania Tabeli
                tableItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                data.setItem(i, j, tableItem)

        # Ustawienie Labelu status połączenia
        self.window.connectStatus.setText("Połączono pomyślnie z serwerem.")
        self.window.connectStatus.setStyleSheet("color: darkgreen")
        return len(items)
    else:
        self.window.connectStatus.setText("Brak połączenia z serwerem")
        self.window.connectStatus.setStyleSheet("color: red")
        return ("0")