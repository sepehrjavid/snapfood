from django.db import connection

from address.services import Address
from shops.services import Food
from snapfood.exceptions import ValidationError


class Comment(object):
    def __init__(self, **kwargs):
        self.commentId = kwargs.get("commentId")
        self.text = kwargs.get("text")
        self.rate = kwargs.get("rate")

    def insert(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.text, self.rate)
                cursor.execute(
                    "INSERT INTO Comment (text, rate) VALUES (%s, %s);", recordValue
                )
                self.commentId = cursor.lastrowid
            except Exception as ex:
                raise ex

    @property
    def data(self):
        return {
            "commentId": self.commentId,
            "text": self.text,
            "rate": self.rate
        }


class Invoice(object):
    def __init__(self, **kwargs):
        self.invoiceId = kwargs.get("invoiceId")
        self.discountId = kwargs.get("discountId")
        self.commentId = kwargs.get("commentId")
        self.statusId = kwargs.get("statusId")
        self.walletId = kwargs.get("walletId")
        self.addressId = kwargs.get("addressId")

    @property
    def status(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.statusId,)
                cursor.execute(
                    "SELECT name FROM Status WHERE statusId=%s;", recordValue
                )
                return cursor.fetchall()[0][0]
            except Exception as ex:
                raise ex

    @property
    def foods(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.invoiceId,)
                cursor.execute(
                    "SELECT Food.* FROM Food INNER JOIN Food_Invoice_Isin FII on Food.foodId = FII.foodId \
                    INNER JOIN Invoice I on FII.invoiceId = I.invoiceId WHERE I.invoiceId=%s;",
                    recordValue
                )
                foods = cursor.fetchall()
                return [Food(foodId=food[0], price=food[1], about=food[2], name=food[3], discount=food[4],
                             categoryId=food[5], shopId=food[6]) for food in foods]
            except Exception as ex:
                raise ex

    @property
    def comment(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.commentId,)
                cursor.execute(
                    "SELECT * FROM Comment WHERE commentId=%s;", recordValue
                )
                comment = cursor.fetchall()[0]
                return Comment(commentId=comment[0], text=comment[1], rate=comment[2])
            except Exception as ex:
                raise ex

    @property
    def address(self):
        with connection.cursor() as cursor:
            try:
                recordValue = (self.addressId,)
                cursor.execute(
                    "SELECT * FROM Address WHERE addressId=%s;", recordValue
                )
                result = cursor.fetchall()[0]
                return Address(addressId=result[1], cityId=result[0], locationId=result[2],
                               address_text=result[3])
            except Exception as ex:
                raise ex

    @property
    def data(self):
        if self.commentId is not None:
            return {
                "invoiceId": self.invoiceId,
                "comment": self.comment.data,
                "status": self.status,
                "address": self.address.data,
                "foods": [x.data for x in self.foods]
            }
        return {
            "invoiceId": self.invoiceId,
            "status": self.status,
            "address": self.address.data,
            "foods": [x.data for x in self.foods]
        }

    def addComment(self, text, rate):
        if self.commentId is not None:
            raise ValidationError("Invoice already has comment")
        if rate > 5 or rate < 0:
            raise ValidationError("Invalid value for rate")
        comment = Comment(text=text, rate=rate)
        comment.insert()
        with connection.cursor() as cursor:
            try:
                recordValue = (comment.commentId, self.invoiceId)
                cursor.execute(
                    "UPDATE Invoice SET commentId=%s WHERE invoiceId=%s;", recordValue
                )
            except Exception as ex:
                raise ex
        self.commentId = comment.commentId
