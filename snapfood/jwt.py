import jwt
from django.db import connection

from accounting.services import User
from admin.services import Admin
from snapfood import settings
from snapfood.exceptions import ValidationError


def getUserToken(user):
    return jwt.encode({"phone_number": user.phone_number}, settings.SECRET_KEY)


def getAdminToken(admin):
    return jwt.encode({"username": admin.username}, settings.SECRET_KEY)


def validateAdminToken(request):
    try:
        payload = jwt.decode(request.META['HTTP_AUTHORIZATION'][4:], settings.SECRET_KEY)
        username = (payload.get("username"),)
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM Admin WHERE username=%s", username
                )
                admin = cursor.fetchall()
                if not admin:
                    raise
                admin = admin[0]
                return Admin(username=admin[0], password=admin[1], shopId=admin[2])
            except:
                raise
    except KeyError:
        raise ValidationError("No Token Provided")
    except:
        raise ValidationError("Token Not Valid")


def validateUserToken(request):
    try:
        payload = jwt.decode(request.META['HTTP_AUTHORIZATION'][4:], settings.SECRET_KEY)
        phoneNumber = (payload.get("phone_number"),)
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM User WHERE phone_number=%s", phoneNumber
                )
                user = cursor.fetchall()
                if not user:
                    raise
                user = user[0]
                return User(userId=user[5], password=user[0], first_name=user[1], last_name=user[2],
                            phone_number=user[3], email=user[4])
            except:
                raise
    except KeyError:
        raise ValidationError("No Token Provided")
    except:
        raise ValidationError("Token Not Valid")
