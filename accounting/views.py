from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection

from accounting.services import User
from snapfood.exceptions import ValidationError, ObjectNotFoundException, ObjectAlreadyExistsException, \
    InsertNotAllowedException
from snapfood.jwt import getUserToken, validateUserToken


class SignupView(APIView):
    def post(self, request):
        user = User(**request.data)
        if user.is_valid():
            try:
                user.insert()
                return Response({"token": getUserToken(user)}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        user = User(**request.data)
        if user.login():
            return Response({"token": getUserToken(user)}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "wrong phone number or password"}, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(APIView):
    def get(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email
        }
        return Response(data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    def put(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)
        user.updateData(**request.data)
        if user.is_valid():
            try:
                user.update()
                return Response(status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserCartView(APIView):
    def get(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(user.cart.data, status=status.HTTP_200_OK)


class AddFoodToCartView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if "foodId" not in data.keys():
            return Response({"detail": "FoodId is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = user.cart
        try:
            cart.addFood(data.get("foodId"))
        except ObjectNotFoundException as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except InsertNotAllowedException as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class GetUserFavoriteView(APIView):
    def get(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        favorites = user.favorites

        return Response([x.data for x in favorites], status=status.HTTP_200_OK)


class AddUserFavoriteView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        if data.get("shopId") is None:
            return Response({"detail": "shopId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.addFavorite(data.get("shopId"))
        except ObjectNotFoundException as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectAlreadyExistsException as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class RemoveUserFavoriteView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        if data.get("shopId") is None:
            return Response({"detail": "shopId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.removeFavorite(data.get("shopId"))
        except ObjectNotFoundException as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class CommitCartView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if data.get("addressId") is None:
            return Response({"detail": "addressId is required"}, status=status.HTTP_400_BAD_REQUEST)

        addresses = user.getAddresses()
        for address in addresses:
            if address.addressId == data.get("addressId"):
                user.cart.commit(data.get("discountId"), data.get("addressId"), user.wallet.walletId)
                return Response(status=status.HTTP_200_OK)

        return Response({"detail": "addressId not valid "}, status=status.HTTP_400_BAD_REQUEST)
