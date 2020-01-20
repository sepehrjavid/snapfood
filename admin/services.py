from django.db import connection

from shops.services import Shop
from snapfood.exceptions import NotValidatedException


class Admin(object):
    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.shopId = kwargs.get("shopId")
        self.errors = []
        self.isValidated = False

    def is_valid(self):
        if self.username is None:
            self.errors.append("Username may not be null")
            return False
        if self.password is None:
            self.errors.append("Password may not be null")
            return False
        if self.shopId is None:
            self.errors.append("ShopId may not be null")
            return False
        self.isValidated = True
        return self.isValidated

    def insert(self):
        if self.isValidated:
            with connection.cursor() as cursor:
                try:
                    recordValue = (self.username, self.password, self.shopId)
                    cursor.execute(
                        "INSERT INTO Admin (username, password, shopId) VALUES (%s, %s, %s);",
                        recordValue
                    )
                except Exception as ex:
                    raise ex
        else:
            raise NotValidatedException

    def login(self):
        if self.username is None or self.password is None:
            return False
        with connection.cursor() as cursor:
            try:
                recordValue = (self.username, self.password)
                cursor.execute(
                    "SELECT * FROM Admin WHERE username=%s AND password=%s;", recordValue
                )
                if len(cursor.fetchall()) == 0:
                    return False
                return True
            except Exception as ex:
                raise ex

    @property
    def shop(self):
        return Shop.getShopById(self.shopId)
