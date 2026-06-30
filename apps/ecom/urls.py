from django.urls import path
from .views import *


urlpatterns = [
   path('registration/', UserRegistration.as_view(), name='registration'),
   path('verify-email/', EmailVerification.as_view(), name='verify-email'),
   path('resend-email/', ResendEmailVerificationAPIView.as_view(), name='resend-email'),

   path('req-pass-reset/', RequestPasswordResetAPIView.as_view()),
   path('verify-otp/', VerifyPasswordResetOTPAPIView.as_view()),
   path('change-pass/', ChangePasswordAPIView.as_view()),

   path('login/', LoginView.as_view(), name='login'),
   path('refresh/', RefreshTokenView.as_view(), name='refresh'),
   path('logout/', LogoutView.as_view(), name='logout'),
   
   path('update-pass/', UpdatePasswordAPIView.as_view(), name='update-pass'),

   path('products/', ProductListView.as_view(), name='product-list'),
   path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

   path('category/', CategoryListView.as_view(), name='category-list'),
   path('category/<int:pk>/', CategoryDetailAPI.as_view(), name='category-detail'),
   
   path('subcategory/', SubCategoryListView.as_view(), name='subcategory-list'),
   path('subcategory/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),

   path('products-by-subcategory/<int:subcategory_pk>/', ProductsBySubcategoryView.as_view(), name='products-by-subcategory'),
   path('products-by-category/<int:category_pk>/', ProductsByCategoryView.as_view(), name='products-by-category'),

   path('general-settings/', GeneralSettingsView.as_view(), name='general-settings'),
]