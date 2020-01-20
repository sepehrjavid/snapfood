from django.urls import path, re_path

from address.views import CreateUserAddressView, GetUserAddressView, DeleteUserAddressView, UpdateUserAddressView

app_name = 'address'

urlpatterns = [
    path('CreateUserAddress', CreateUserAddressView.as_view()),
    path('GetUserAddress', GetUserAddressView.as_view()),
    re_path(r'^DeleteUserAddress/(?P<addressId>\d+)$', DeleteUserAddressView.as_view()),
    re_path(r'^UpdateUserAddress/(?P<addressId>\d+)$', UpdateUserAddressView.as_view())
]
