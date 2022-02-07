from django.urls import path
from . import views

urlpatterns = [
    path("", views.Homepage, name="Homepage"),
    path("about/", views.Aboutpage, name="Aboutpage"),
    path("performance/", views.Performancepage, name="Performancepage"),
    path("<str:album_spotify_id>/", views.Detailpage, name="Detailpage")


]
