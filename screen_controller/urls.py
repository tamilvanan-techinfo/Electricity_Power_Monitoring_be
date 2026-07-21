from django.urls import path
from . import views

urlpatterns = [
    path("", views.screens, name="screens"),
    path("screens/create/", views.create_screen, name="create_screen"),
    path("screens/<int:screen_id>/update/", views.update_screen, name="update_screen"),
    path("screens/<int:screen_id>/delete/", views.delete_screen, name="delete_screen"),
    path("screens/<int:screen_id>/set-live/", views.set_current_screen, name="set_current_screen"),
]