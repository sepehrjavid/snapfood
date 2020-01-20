from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from admin.services import Admin
from shops.services import Food
from snapfood.exceptions import ValidationError
from snapfood.jwt import getAdminToken, validateAdminToken


class AdminSignUpView(APIView):
    def post(self, request):
        admin = Admin(**request.data)
        if admin.is_valid():
            try:
                admin.insert()
                return Response({"token": getAdminToken(admin)}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(admin.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        admin = Admin(**request.data)
        if admin.login():
            return Response({"token": getAdminToken(admin)}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "wrong phone number or password"}, status=status.HTTP_400_BAD_REQUEST)


class AddFoodShopView(APIView):
    def post(self, request):
        try:
            admin = validateAdminToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        food = Food(**request.data)
        food.shopId = admin.shopId
        if food.is_valid():
            try:
                food.insert()
                return Response(status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(food.errors, status=status.HTTP_400_BAD_REQUEST)
