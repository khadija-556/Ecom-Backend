from django.urls import path
from .views import *


urlpatterns = [
   path('products/', ProductListView.as_view(), name='product-list'),
   path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
   path('category/', CategoryListView.as_view(), name='category-list'),
   path('category/<int:pk>/', CategoryDetailAPI.as_view(), name='category-detail'),
] 