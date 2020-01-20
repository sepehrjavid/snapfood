from django.urls import path

from admin.views import AdminSignUpView, AdminLoginView, AddFoodShopView, RemoveFoodShopView

app_name = "admin"

urlpatterns = [
    path('Signup', AdminSignUpView.as_view()),
    path('Login', AdminLoginView.as_view()),
    path('AddFoodShop', AddFoodShopView.as_view()),
    path('RemoveFoodShop', RemoveFoodShopView.as_view())
]
