from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.Homepage, name="Homepage"),
    path("about/", views.Aboutpage, name="Aboutpage"),
    path("performance/", views.Performancepage, name="Performancepage"),
    path("charts/", views.Chartspage, name="Chartspage"),
    path("<str:album_spotify_id>/", views.Detailpage, name="Detailpage")



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
