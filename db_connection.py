# db_connection.py
import json
import pyodbc

class DatabaseConnection:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)['db_config']

    def get_sql_server_connection(self):
        connection = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={self.config["server"]};DATABASE={self.config["database"]};Trusted_Connection=yes',
            autocommit=True
        )
        return connection

