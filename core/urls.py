from django.urls import path

from core.views import update_now

urlpatterns = [
    path('update_now', update_now),
]