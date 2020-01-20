from django.db import connection

from address.services import Address
from shops.services import Food, Shop
from snapfood.exceptions import NotValidatedException, NoValueForIdException, ObjectNotFoundException


class Cart(object):
    def __init__(self, **kwargs):
        self.cartId = kwargs.get("cartId")
        self.userId = kwargs.get("userId")

        with connection.cursor() as cursor:
            try:
                recordValue = (self.cartId,)
                cursor.execute(
                    "SELECT Food.* FROM Cart_Food_Isin INNER JOIN Food ON Cart_Food_Isin.foodId=Food.foodId AND\
                     Cart_Food_Isin.cartId=%s;",
                    recordValue
                )
                results = cursor.fetchall()
            except Exception as ex:
                raise ex
        foods = []
        for food in results:
            foods.append(Food(foodId=food[0], price=food[1], about=food[2], name=food[3], discount=food[4],
                              categoryId=food[5], shopId=food[6]))
        self.foods = foods

    def addFood(self, foodId):
        food = Food.getFoodById(foodId)
        if not food:
            raise ObjectNotFoundException("food not found")

        with connection.cursor() as cursor:
            try:
                recordValue = (foodId, self.cartId)
                cursor.execute(
                    "INSERT INTO Cart_Food_Isin (foodId, cartId) VALUES (%s, %s);", recordValue
                )
            except Exception as ex:
                raise ex

    @property
    def data(self):
        return {
            "cartId": self.cartId,
            "foods": [
                x.data for x in self.foods
            ]
        }


class Wallet(object):
    def __init__(self, **kwargs):
        self.userId = kwargs.get("userId")
        self.walletId = kwargs.get("walletId")


class User(object):
    def __init__(self, **kwargs):
        self.userId = kwargs.get("userId")
        self.password = kwargs.get("password")
        self.phone_number = kwargs.get("phone_number")
        self.email = kwargs.get("email")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.isValidated = False
        self.errors = []

    def is_valid(self):
        self.isValidated = True
        return self.isValidated

    def insert(self):
        if self.isValidated:
            with connection.cursor() as cursor:
                try:
                    recordValue = (self.email, self.first_name, self.last_name, self.password, self.phone_number)
                    cursor.execute(
                        "INSERT INTO User (email, first_name, last_name, password, phone_number) \
                        VALUES (%s, %s, %s, %s, %s);",
                        recordValue
                    )
                    self.userId = cursor.lastrowid
                    recordValue = (self.userId,)
                    cursor.execute("INSERT INTO Cart (userId) VALUES (%s);", recordValue)
                    cursor.execute("INSERT INTO Wallet (userId) VALUES (%s);", recordValue)
                except Exception as ex:
                    raise ex
        else:
            raise NotValidatedException

    def update(self):
        if self.isValidated:
            if self.userId is not None:
                with connection.cursor() as cursor:
                    try:
                        recordValue = (self.email, self.first_name, self.last_name, self.userId)
                        cursor.execute(
                            "UPDATE User SET email=%s, first_name=%s, last_name=%s WHERE userId=%s;",
                            recordValue
                        )
                    except Exception as ex:
                        raise ex
            else:
                raise NoValueForIdException
        else:
            raise NotValidatedException

    def login(self):
        if self.phone_number is None or self.password is None:
            return False
        with connection.cursor() as cursor:
            try:
                recordValue = (self.phone_number, self.password)
                cursor.execute(
                    "SELECT * FROM User WHERE phone_number=%s AND password=%s;", recordValue
                )
                if len(cursor.fetchall()) == 0:
                    return False
                return True
            except Exception as ex:
                raise ex

    @property
    def cart(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.userId,)
                cursor.execute(
                    "SELECT * FROM Cart WHERE userId=%s;", recordValue
                )
                cartId = cursor.fetchall()[0][0]
                return Cart(userId=self.userId, cartId=cartId)
            except Exception as ex:
                raise ex

    @property
    def wallet(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.userId,)
                cursor.execute(
                    "SELECT * FROM Wallet WHERE userId=%s;", recordValue
                )
                walletId = cursor.fetchall()[0][0]
                return Wallet(userId=self.userId, walletId=walletId)
            except Exception as ex:
                raise ex

    def updateData(self, **kwargs):
        fields = list(self.__dict__.keys())[:6]
        for field in fields:
            if field in kwargs.keys():
                self.__dict__[field] = kwargs.get(field)
        self.isValidated = False

    def getAddresses(self):
        addresses = None
        with connection.cursor() as cursor:
            try:
                recordValue = (self.userId,)
                cursor.execute(
                    "SELECT * FROM Address WHERE userId=%s;", recordValue
                )
                addresses = cursor.fetchall()
            except Exception as ex:
                raise ex
        return [Address(cityId=address[0],
                        addressId=address[1],
                        locationId=address[2],
                        address_text=address[3]) for address in addresses]

    def getOrders(self):
        pass

    @property
    def favorites(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.userId,)
                cursor.execute(
                    "SELECT Shop.* FROM Shop INNER JOIN User_Shop_Favorite ON Shop.shopId=User_Shop_Favorite.shopId \
                    WHERE User_Shop_Favorite.userId=%s;",
                    recordValue
                )
                favorites = cursor.fetchall()
            except Exception as ex:
                raise ex
        return [Shop(shopId=shop[0], about_text=shop[1], name=shop[2], minimum_bill_value=shop[3],
                     addressId=shop[4]) for shop in favorites]

    def addFavorite(self, shopId):
        shop = Shop.getShopById(shopId)
        if not shop:
            raise ObjectNotFoundException("shop not found")

        with connection.cursor() as cursor:
            try:
                recordValue = (shopId, self.userId)
                cursor.execute(
                    "INSERT INTO User_Shop_Favorite (shopId, userId) VALUES (%s, %s);",
                    recordValue
                )
            except Exception as ex:
                raise ex
