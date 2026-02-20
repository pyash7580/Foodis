from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_root_view, name='ai-root'),
]
