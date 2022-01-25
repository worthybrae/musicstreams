from django.urls import path
from . import views

urlpatterns = [
    path("", views.Homepage, name="Homepage"),
    path("about/", views.Aboutpage, name="Aboutpage"),
    path("<str:album_spotify_id>/", views.Detailpage, name="Detailpage"),
]
