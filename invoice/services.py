from django.db import connection

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
