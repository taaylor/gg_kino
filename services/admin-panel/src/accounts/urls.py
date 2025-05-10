from accounts.views import experiment_view
from django.urls import path

urlpatterns = [
    path("lala/tata/", experiment_view, name="experiment"),
]
