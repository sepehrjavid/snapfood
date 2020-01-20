from django.urls import path

from admin.views import AdminSignUpView, AdminLoginView, GetAdminShopView

app_name = "admin"

urlpatterns = [
    path('Signup', AdminSignUpView.as_view()),
    path('Login', AdminLoginView.as_view()),
    path('GetAdminShop', GetAdminShopView.as_view())
]
