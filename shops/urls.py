from django.urls import path, re_path

from shops.views import GetCategoriesView, GetShopsView, GetShopFoodView

app_name = 'shops'

urlpatterns = [
    path('GetCategories', GetCategoriesView.as_view()),
    path('GetShopByQuery', GetShopsView.as_view()),
    re_path(r'^GetShopFood/(?P<shopId>\d+)$', GetShopFoodView.as_view())
]
