from django.urls import path

from admin.views import AdminSignUpView, AdminLoginView, AddFoodShopView

app_name = "admin"

urlpatterns = [
    path('Signup', AdminSignUpView.as_view()),
    path('Login', AdminLoginView.as_view()),
    path('AddFoodShop', AddFoodShopView.as_view()),
]
