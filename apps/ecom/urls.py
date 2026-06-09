from django.urls import path
from .views import *


urlpatterns = [
   path('products/', ProductListView.as_view(), name='product-list'),
   path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

   path('category/', CategoryListView.as_view(), name='category-list'),
   path('category/<int:pk>/', CategoryDetailAPI.as_view(), name='category-detail'),
   
   path('subcategory/', SubCategoryListView.as_view(), name='subcategory-list'),
   path('subcategory/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),

   path('products-by-subcategory/<int:subcategory_pk>/', ProductsBySubcategoryView.as_view(), name='products-by-subcategory'),
   path('products-by-category/<int:category_pk>/', ProductsByCategoryView.as_view(), name='products-by-category'),
]