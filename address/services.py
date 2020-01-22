from django.db import connection

from snapfood.exceptions import NotValidatedException


def updateLocation(x, y, locationId):
    with connection.cursor() as cursor:
        try:
            recordValue = (x, y, locationId)
            cursor.execute(
                "UPDATE Location SET x=%s, y=%s WHERE locationId=%s;", recordValue
            )
            return cursor.lastrowid
        except Exception as ex:
            raise ex


def createLocation(x, y):
    with connection.cursor() as cursor:
        try:
            recordValue = (x, y)
            cursor.execute(
                "INSERT INTO Location (x, y) VALUES (%s, %s);", recordValue
            )
            return cursor.lastrowid
        except Exception as ex:
            raise ex


class Address(object):
    def __init__(self, **kwargs):
        self.cityId = kwargs.get("cityId")
        self.addressId = kwargs.get("addressId")
        self.locationId = kwargs.get("locationId")
        self.address_text = kwargs.get("address_text")
        self.city = kwargs.get("city")
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.errors = []
        self.isValidated = False
        self.modifiedFields = []

        if kwargs.get("locationId") is not None:
            with connection.cursor() as cursor:
                try:
                    recordValue = (kwargs.get("locationId"),)
                    cursor.execute(
                        "SELECT * FROM Location WHERE locationId=%s;", recordValue
                    )
                    location = cursor.fetchall()[0]
                    self.x = location[1]
                    self.y = location[2]
                except Exception as ex:
                    raise ex

        if kwargs.get("cityId") is not None:
            with connection.cursor() as cursor:
                try:
                    recordValue = (kwargs.get("cityId"),)
                    cursor.execute(
                        "SELECT * FROM City WHERE cityId=%s;", recordValue
                    )
                    self.city = cursor.fetchall()[0][1]
                except Exception as ex:
                    raise ex

    def is_valid(self):
        if self.city is None:
            self.errors.append("city may not be null")
            return False
        if self.x is None:
            self.errors.append("X may not be null")
            return False
        if self.y is None:
            self.errors.append("Y may not be null")
            return False
        if self.address_text is None:
            self.errors.append("Address Text may not be null")
            return False
        with connection.cursor() as cursor:
            try:
                recordValue = (self.city,)
                cursor.execute(
                    "SELECT * FROM City WHERE name=%s;", recordValue
                )
                city = cursor.fetchall()
            except Exception as ex:
                raise ex
        if not city:
            self.errors.append("City Not Valid")
            return False
        self.cityId = city[0][0]
        self.isValidated = True
        return self.isValidated

    def insert(self, user):
        if self.isValidated:
            locationId = createLocation(self.x, self.y)

            with connection.cursor() as cursor:
                try:
                    recordValue = (self.cityId, locationId, self.address_text, user.userId)
                    cursor.execute(
                        "INSERT INTO Address (cityId, locationId, address_text, userId) VALUES (%s, %s, %s, %s);",
                        recordValue
                    )
                except Exception as ex:
                    raise ex
        else:
            raise NotValidatedException

    def delete(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.addressId,)
                cursor.execute(
                    "DELETE FROM Location WHERE locationId=(SELECT locationId FROM Address WHERE addressId=%s);",
                    recordValue
                )
                cursor.execute(
                    "DELETE FROM Address WHERE addressId=%s;", recordValue
                )
            except Exception as ex:
                raise ex

    def update(self):
        if self.isValidated:
            if "x" in self.modifiedFields or "y" in self.modifiedFields:
                updateLocation(self.x, self.y, self.locationId)
            with connection.cursor() as cursor:
                try:
                    recordValue = (self.address_text, self.cityId, self.addressId,)
                    cursor.execute(
                        "UPDATE Address SET address_text=%s, cityId=%s WHERE addressId=%s;",
                        recordValue
                    )
                except Exception as ex:
                    raise ex
            self.modifiedFields = []
        else:
            raise NotValidatedException

    def updateData(self, **kwargs):
        fields = list(self.__dict__.keys())[:7]
        for field in fields:
            if field in kwargs.keys():
                self.__dict__[field] = kwargs.get(field)
                self.modifiedFields.append(field)
        self.isValidated = False

    @property
    def data(self):
        return {
            "addressId": self.addressId,
            "address_text": self.address_text,
            "location": {"id": self.locationId, "x": self.x, "y": self.y},
            "city": {"id": self.cityId, "name": self.city}
        }
