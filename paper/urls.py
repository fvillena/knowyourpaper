from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<path:doi>", views.paper, name="paper"),
]