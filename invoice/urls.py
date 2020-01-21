from django.urls import path, re_path

from invoice.views import CommentOnInvoiceView, GetInvoiceDetailView

app_name = 'invoice'

urlpatterns = [
    path('CommentOnInvoice', CommentOnInvoiceView.as_view()),
    re_path(r'^GetInvoiceDetail/(?P<invoiceId>\d+)$', GetInvoiceDetailView.as_view())
]
