from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shops.services import Category, Shop


class GetCategoriesView(APIView):
    def get(self, request):
        categories = Category.getAll()
        return Response([x.data for x in categories], status=status.HTTP_200_OK)


class GetShopByCategoryView(APIView):
    def get(self, request):
        query = request.GET.get("category")
        if query is None:
            shops = Shop.getAllShops()
            return Response([x.data for x in shops], status=status.HTTP_200_OK)
        shops = Shop.getShopByCategory(query)
        return Response([x.data for x in shops], status=status.HTTP_200_OK)


class GetShopFoodView(APIView):
    def get(self, request, shopId):
        shop = Shop.getShopById(shopId)
        foods = shop.foods
        return Response([x.data for x in foods])
