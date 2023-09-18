from logger import Logging
from dataclasses import dataclass
import sqlite3

@dataclass
class DbProcess:
    database_path: str
    column_name: str
    table_name: str
    logger: Logging

    @staticmethod
    def db_connect(database_path):
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_table(self):
        cursor = self.db_connect(self.database_path)
        try:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {self.column_name} TEXT)")
            cursor.commit()
        except sqlite3.OperationalError as err:
            self.logger.error("Ошибка создания таблици: %s", err)
        finally:
            cursor.close()

    def inser_data(self, column_data):
        cursor = self.db_connect(self.database_path)
        try:
            cursor.execute(f"INSERT INTO {self.table_name} ({self.column_name}) VALUES (?)", (column_data,))
            cursor.commit()
            self.logger.info("Данные: %s записаны в таблицу: %s", column_data, self.table_name)
        except sqlite3.OperationalError as err:
            self.logger.error("Ошибка добавления данных в таблицу: %s", err)
        finally:
            cursor.close()

    def select_data(self, column_data):
        cursor = self.db_connect(self.database_path)
        try:
            select = cursor.execute(f"SELECT {self.column_name} FROM {self.table_name} WHERE {self.column_name} = '{column_data}'").fetchone()
        except sqlite3.OperationalError as err:
            self.logger.warning("Ошибка выполнения SQL запроса: %s", err)
        finally:
            cursor.close()
        return select
