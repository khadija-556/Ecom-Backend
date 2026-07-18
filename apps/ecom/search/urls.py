from django.urls import path
from .views import *


urlpatterns = [
   path('search/', UniversalSearchView.as_view(), name='universal-search'),
]