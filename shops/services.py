from django.db import connection

from address.services import Address
from snapfood.exceptions import NotValidatedException


class Food(object):
    def __init__(self, **kwargs):
        self.foodId = kwargs.get("foodId")
        self.price = kwargs.get("price")
        self.about = kwargs.get("about")
        self.name = kwargs.get("name")
        self.discount = kwargs.get("discount")
        self.categoryId = kwargs.get("categoryId")
        self.shopId = kwargs.get("shopId")
        self.category = kwargs.get("category")
        self.errors = []
        self.isValidated = False

        if kwargs.get("categoryId") is not None:
            with connection.cursor() as cursor:
                try:
                    recordValue = (kwargs.get("categoryId"),)
                    cursor.execute(
                        "SELECT name FROM Category WHERE categoryId=%s;", recordValue
                    )
                    category = cursor.fetchall()[0]
                    self.category = category[0]
                except Exception as ex:
                    raise ex

    @staticmethod
    def getFoodById(foodId):
        with connection.cursor() as cursor:
            try:
                recordValue = (foodId,)
                cursor.execute(
                    "SELECT * FROM Food WHERE foodId=%s;", recordValue
                )
                result = cursor.fetchall()
                if not result:
                    return []
                else:
                    food = result[0]
                    return Food(foodId=food[0], price=food[1], about=food[2], name=food[3], discount=food[4],
                                categoryId=food[5], shopId=food[6])
            except Exception as ex:
                raise ex

    def is_valid(self):
        if self.name is None:
            self.errors.append("name may not be null")
            return False
        if self.price is None:
            self.errors.append("price may not be null")
            return False
        if self.categoryId is None:
            self.errors.append("categoryId may not be null")
            return False
        with connection.cursor() as cursor:
            try:
                recordValue = (self.categoryId,)
                cursor.execute(
                    "SELECT * FROM Category WHERE categoryId=%s;", recordValue
                )
                category = cursor.fetchall()
            except Exception as ex:
                raise ex
        if not category:
            self.errors.append("Category Not Valid")
            return False
        self.isValidated = True
        return self.isValidated

    def insert(self):
        if self.isValidated:
            with connection.cursor() as cursor:
                try:
                    recordValue = (self.price, self.about, self.name, self.discount, self.categoryId, self.shopId)
                    cursor.execute(
                        "INSERT INTO Food (price, about, name, discount, categoryId, shopId) VALUES \
                            (%s, %s, %s, %s, %s, %s);",
                        recordValue
                    )
                except Exception as ex:
                    raise ex
        else:
            raise NotValidatedException

    def delete(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.foodId,)
                cursor.execute(
                    "DELETE FROM Food WHERE foodId=%s;",
                    recordValue
                )
            except Exception as ex:
                raise ex

    @property
    def data(self):
        return {
            "foodId": self.foodId,
            "price": self.price,
            "about": self.about,
            "name": self.name,
            "discount": self.discount,
            "category": self.category,
            "shopId": self.shopId
        }


class Shop(object):
    def __init__(self, **kwargs):
        self.shopId = kwargs.get("shopId")
        self.about_text = kwargs.get("about_text")
        self.name = kwargs.get("name")
        self.minimum_bill_value = kwargs.get("minimum_bill_value")
        self.addressId = kwargs.get("addressId")

        if self.addressId is not None:
            with connection.cursor() as cursor:
                try:
                    recordValue = (self.addressId,)
                    cursor.execute(
                        "SELECT * FROM Address WHERE addressId=%s;", recordValue
                    )
                    result = cursor.fetchall()[0]
                    self.address = Address(addressId=result[1], cityId=result[0], locationId=result[2],
                                           address_text=result[3])
                except Exception as ex:
                    raise ex

    @property
    def foods(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.shopId,)
                cursor.execute(
                    "SELECT Food.* FROM Shop INNER JOIN Food ON Food.shopId = Shop.shopId WHERE Shop.shopId=%s;",
                    recordValue
                )
                result = cursor.fetchall()
                return [Food(foodId=food[0], price=food[1], about=food[2], name=food[3], discount=food[4],
                             categoryId=food[5], shopId=food[6]) for food in result]
            except Exception as ex:
                raise ex

    @property
    def categories(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.shopId,)
                cursor.execute(
                    "SELECT DISTINCT C.name FROM Shop INNER JOIN Food ON Food.shopId = Shop.shopId \
                    INNER JOIN Category C on Food.categoryId = C.categoryId WHERE Shop.shopId=%s;",
                    recordValue
                )
                result = cursor.fetchall()
                return [x[0] for x in result]
            except Exception as ex:
                raise ex

    @property
    def data(self):
        return {
            "shopId": self.shopId,
            "name": self.name,
            "about_text": self.about_text,
            "minimum_bill_value": self.minimum_bill_value,
            "address": self.address.data
        }

    @staticmethod
    def getShopById(shopId):
        with connection.cursor() as cursor:
            try:
                recordValue = (shopId,)
                cursor.execute(
                    "SELECT * FROM Shop WHERE shopId=%s;", recordValue
                )
                result = cursor.fetchall()
                if not result:
                    return []
                else:
                    shop = result[0]
                    return Shop(shopId=shop[0], about_text=shop[1], name=shop[2], minimum_bill_value=shop[3],
                                addressId=shop[4])
            except Exception as ex:
                raise ex

    @staticmethod
    def getAllShops():
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM Shop;"
                )
                result = cursor.fetchall()
                return [Shop(shopId=shop[0], about_text=shop[1], name=shop[2], minimum_bill_value=shop[3],
                             addressId=shop[4]) for shop in result]
            except Exception as ex:
                raise ex

    @staticmethod
    def _getQuery(key):
        if key == "category":
            return "SELECT DISTINCT Shop.* FROM Shop INNER JOIN Food F on Shop.shopId = F.shopId \
                    INNER JOIN Category C on F.categoryId = C.categoryId WHERE C.name LIKE %s;"
        elif key == "name":
            return "SELECT * FROM Shop WHERE name LIKE %s;"
        elif key == "city":
            return "SELECT Shop.* FROM Shop INNER JOIN Address A on Shop.addressId = A.addressId \
                    INNER JOIN City C on A.cityId = C.cityId WHERE C.name LIKE %s;"
        elif key == "foodName":
            return "SELECT Shop.* FROM Shop INNER JOIN Food F on Shop.shopId = F.shopId WHERE F.name LIKE %s;"
        elif key == "territory":
            return "SELECT Shop.* FROM Shop INNER JOIN Address A on Shop.addressId = A.addressId \
            INNER JOIN Location L on A.locationId = L.locationId WHERE L.x BETWEEN %s AND %s AND L.y BETWEEN %s AND %s;"

    @staticmethod
    def getShopsByQuery(key, value):
        query = Shop._getQuery(key)
        with connection.cursor() as cursor:
            try:
                if key == "territory":
                    recordValue = (float(value.split()[0]) - 100, float(value.split()[0]) + 100,
                                   float(value.split()[1]) - 100, float(value.split()[1]) + 100)
                else:
                    recordValue = ("%" + value + "%",)
                cursor.execute(
                    query,
                    recordValue
                )
                result = cursor.fetchall()
                print(result)
                return [Shop(shopId=shop[0], about_text=shop[1], name=shop[2], minimum_bill_value=shop[3],
                             addressId=shop[4]) for shop in result]
            except Exception as ex:
                raise ex

    @staticmethod
    def geShopByNameSearch(name):
        with connection.cursor() as cursor:
            try:
                recordValue = ("%" + name + "%",)
                cursor.execute(
                    "SELECT * FROM Shop WHERE name LIKE %s;", recordValue
                )
                result = cursor.fetchall()
                return [Shop(shopId=shop[0], about_text=shop[1], name=shop[2], minimum_bill_value=shop[3],
                             addressId=shop[4]) for shop in result]
            except Exception as ex:
                raise ex


class Category(object):
    def __init__(self, **kwargs):
        self.categoryId = kwargs.get("categoryId")
        self.name = kwargs.get("name")

    @staticmethod
    def getAll():
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM Category;"
                )
                result = cursor.fetchall()
                return [Category(categoryId=category[0], name=category[1]) for category in result]
            except Exception as ex:
                raise ex

    @property
    def data(self):
        return {
            "categoryId": self.categoryId,
            "name": self.name
        }
