
from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.frontend_view, name='frontend'),  # Serve the frontend at the root URL
    # Other paths
]