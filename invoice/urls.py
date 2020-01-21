from django.urls import path

from invoice.views import CommentOnInvoiceView

app_name = 'invoice'

urlpatterns = [
    path('CommentOnInvoice', CommentOnInvoiceView.as_view())
]
