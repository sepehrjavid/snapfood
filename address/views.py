from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from address.services import Address
from snapfood.exceptions import ValidationError
from snapfood.jwt import validateUserToken


class GetUserAddressView(APIView):
    def get(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        lst = user.getAddresses()
        out = [x.data for x in lst]
        return Response(out, status=status.HTTP_200_OK)


class CreateUserAddressView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        address = Address(**request.data)
        if address.is_valid():
            try:
                address.insert(user)
                return Response(status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"detail": ex}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(address.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAddressView(APIView):
    def delete(self, request, addressId):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        addresses = user.getAddresses()

        for address in addresses:
            if address.addressId == int(addressId):
                address.delete()
                return Response(status=status.HTTP_200_OK)
        return Response({"detail": "Address Not Found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserAddressView(APIView):
    def put(self, request, addressId):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        addresses = user.getAddresses()

        for address in addresses:
            if address.addressId == int(addressId):
                address.updateData(**request.data)
                if address.is_valid():
                    try:
                        address.update()
                        return Response(status=status.HTTP_200_OK)
                    except Exception as ex:
                        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(address.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Address Not Found"}, status=status.HTTP_404_NOT_FOUND)
