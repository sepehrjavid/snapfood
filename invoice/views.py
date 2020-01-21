from django.db import connection
import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from snapfood.exceptions import ValidationError
from snapfood.jwt import validateUserToken


class CommentOnInvoiceView(APIView):
    def post(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if data.get("invoiceId") is None:
            return Response({"detail": "invoiceId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if data.get("text") is None:
            return Response({"detail": "text is required"}, status=status.HTTP_400_BAD_REQUEST)
        if data.get("rate") is None:
            return Response({"detail": "rate is required"}, status=status.HTTP_400_BAD_REQUEST)

        userInvoices = user.invoices
        for invoice in userInvoices:
            if invoice.invoiceId == data.get("invoiceId"):
                if invoice.statusId != 3:
                    return Response({"detail": "Cannot add comment in this stage"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    invoice.addComment(data.get("text"), data.get("rate"))
                    return Response(status=status.HTTP_200_OK)
                except ValidationError as ex:
                    return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "invoiceId is not valid"}, status=status.HTTP_400_BAD_REQUEST)


class GetInvoiceDetailView(APIView):
    def get(self, request, invoiceId):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)
        userInvoices = user.invoices
        for invoice in userInvoices:
            if invoice.invoiceId == int(invoiceId):
                return Response(invoice.data, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "invoiceId is not valid"}, status=status.HTTP_400_BAD_REQUEST)


class GetAllInvoicesView(APIView):
    def get(self, request):
        try:
            user = validateUserToken(request)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_401_UNAUTHORIZED)

        userInvoices = user.invoices
        out = []
        for invoice in userInvoices:
            price = 0
            out.append(invoice.data)
            for food in invoice.foods:
                price += food.price
            out[-1]["totalPrice"] = price

        return Response(out, status=status.HTTP_200_OK)
