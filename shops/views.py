from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shops.services import Category, Shop


class GetCategoriesView(APIView):
    def get(self, request):
        categories = Category.getAll()
        return Response([x.data for x in categories], status=status.HTTP_200_OK)


class GetShopsView(APIView):
    def get(self, request):
        if request.GET.get("category") is not None:
            shops = Shop.getShopsByQuery("category", request.GET.get("category"))
        elif request.GET.get("city") is not None:
            shops = Shop.getShopsByQuery("city", request.GET.get("city"))
        elif request.GET.get("foodName") is not None:
            shops = Shop.getShopsByQuery("foodName", request.GET.get("foodName"))
        elif request.GET.get("name") is not None:
            shops = Shop.getShopsByQuery("name", request.GET.get("name"))
        elif request.GET.get("territory") is not None:
            try:
                request.GET.get("territory").split()[1]
            except:
                return Response({"detail": "Invalid territory"}, status=status.HTTP_400_BAD_REQUEST)
            shops = Shop.getShopsByQuery("territory", request.GET.get("territory"))
        else:
            shops = Shop.getAllShops()
        return Response([x.data for x in shops], status=status.HTTP_200_OK)


class GetShopFoodView(APIView):
    def get(self, request, shopId):
        shop = Shop.getShopById(shopId)
        foods = shop.foods
        return Response([x.data for x in foods])
