from clickhouse_driver import Client


class ClickHouse:
    def __init__(self):
        self.client = Client(host='127.0.0.1')

    def ch_insert(self, insert_values: list):
        try:
            self.client.execute(f"INSERT INTO default.views (film_id, user_id, timestamp) VALUES ",
                            (tuple(row) for row in insert_values))
        except Exception as ex:
            pass
# # client.execute("INSERT INTO default.views (film_id, user_id,timestamp) VALUES ('61f0c404-5cb3-11e7-907b-a6006ad3dba0', '61f0c404-5cb3-11e7-907b-a6006ad3dba1', 654764)")
