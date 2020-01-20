from django.urls import path

from accounting.views import SignupView, LoginView, Test, UserRetrieveView, UserUpdateView, GetUserCartView, \
    AddFoodToCartView, GetUserFavoriteView, AddUserFavoriteView

app_name = 'accounting'

urlpatterns = [
    path('Signup', SignupView.as_view()),
    path('Login', LoginView.as_view()),
    path('Retrieve', UserRetrieveView.as_view()),
    path('Update', UserUpdateView.as_view()),
    path('GetUserCart', GetUserCartView.as_view()),
    path('AddFoodToCart', AddFoodToCartView.as_view()),
    path('GetUserFavorite', GetUserFavoriteView.as_view()),
    path('AddUserFavorite', AddUserFavoriteView.as_view()),
    path('test', Test.as_view()),
]
