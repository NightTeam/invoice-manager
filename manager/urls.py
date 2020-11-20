from django.urls import path

from . import views

app_name = "manager"

urlpatterns = [
    path("merge_invoices/", views.merge_invoices, name="merge_invoices"),
    path("dump_invoices/", views.dump_invoices, name="dump_invoices"),
]
