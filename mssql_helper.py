import pyodbc

class MsSqlHelper:
    def __init__(self, server, database, user, password):
        self.conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};UID={user};PWD={password}'
        )

    def execute_query(self, query, params=None):
        with pyodbc.connect(self.conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results

    def execute_non_query(self, query, params=None):
        with pyodbc.connect(self.conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                conn.commit()

    def execute_scalar(self, query, params=None):
        with pyodbc.connect(self.conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.fetchone()[0]
