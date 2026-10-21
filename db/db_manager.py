from config.db import conninfo, AUTH_DB, PRODUCT_DB, PAYMENT_DB
from db.auth_db import AuthDB
from db.payment_db import PaymentDB
from db.product_db import ProductDB


class DBManager:
    """Единая точка доступа ко всем базам стенда."""

    def __init__(self):
        self.auth = AuthDB(conninfo(AUTH_DB))
        self.product = ProductDB(conninfo(PRODUCT_DB))
        self.payment = PaymentDB(conninfo(PAYMENT_DB))

    def close(self):
        for client in (self.auth, self.product, self.payment):
            client.close()
