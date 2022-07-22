import logging
from socket import error

import backoff
from clickhouse_driver import Client

from clickhouse_driver.errors import NetworkError, CannotParseUuidError, ErrorCodes

from clickhouse.ETL.pkg.backoff_handlers.req_handler import create_backoff_hdlr

logger = logging.getLogger(__name__)

BACKOFF_MAX_TIME = 60  # sec
back_off_hdlr = create_backoff_hdlr(logger)


class ClickHouse:
    @backoff.on_exception(
        backoff.fibo,
        exception=(ConnectionRefusedError, NetworkError, ConnectionError,BaseException),
        max_time=BACKOFF_MAX_TIME,
        on_backoff=back_off_hdlr,
    )
    def connection(self):

        client = Client(host='127.0.0.1')
        try:
            client.connection.connect()
            return client
        except:
            raise ConnectionRefusedError


    @backoff.on_exception(
        backoff.fibo,
        exception=(NetworkError, CannotParseUuidError),
        max_time=BACKOFF_MAX_TIME,
        # on_backoff=back_off_hdlr,
    )
    def ch_insert(self, insert_values: list):
        try:
            client = self.connection()
            client.execute(f"INSERT INTO default.views (film_id, user_id, timestamp) VALUES ",
                           (tuple(row) for row in insert_values))
        except:
            pass
