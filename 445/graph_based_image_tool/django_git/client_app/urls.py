from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("outports", views.send_outports, name="outports"),
]