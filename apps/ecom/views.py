from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product
import datetime
from datetime import timedelta
from django.utils.http import http_date
from django.core.mail import send_mail
from .response import base_error_response, base_success_response, Codenco
from .serializer import *
from .shortcuts import get_object_or_false
from django.conf import settings
import os


########  Registration API ##########

class UserRegistration(APIView):
    def post(self,request):
        data = request.data

        if data.get('password') != data.get('confirm_password'):
            return Response(base_error_response("Passwords do not match"),
                            status= status.HTTP_400_BAD_REQUEST)

        if not data.get('email'):
            return Response(base_error_response("Email is Required"))
        
        if CustomUser.objects.filter(email = data.get('email')).exists():
            return Response(base_error_response("User with this email already exist"),
                            status = status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save()

            
            user = serializer.instance

            try:
                self.send_email_verification_mail(user=user)

            except Exception as e:
                return Response(base_error_response("Failed to send verification email: {}".format(str(e))), 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(base_success_response("User Registered Successfully and Token Send to the Email" ,data= serializer.data),
                            status = status.HTTP_201_CREATED)

        return Response(base_error_response('Serilizer Error',errors = serializer.errors),
                        status = status.HTTP_400_BAD_REQUEST)

    def send_email_verification_mail(self,user):
        token = user.generate_email_verification_token()

        send_mail(
            subject='Email Verification Token',
            message='Your email verification token is: {}'.format(token),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=f"""
            <p>Hi {user.first_name},</p>
            <p>Your email verification token is: <strong>{token}</strong>. This
            will expire in 1 hour.</p> """
        )


class EmailVerification(APIView):
    def post(self,request):
        data = request.data
        token = data.get("token")

        if not token:
            return Response(base_error_response("Token not found"), 
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_false(CustomUser, email_token=token)

        if not user:
            return Response(base_error_response("Invalid token"), 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if user.email_token_expired < timezone.now():
            return Response(base_error_response("Token has expired"), 
                            status=status.HTTP_400_BAD_REQUEST)
        
        user.is_email_verified = True
        user.email_token = None
        user.email_token_expired = None
        user.save()

        return Response(base_success_response("Email verified successfully"),
                                            status=status.HTTP_200_OK)


class ResendEmailVerificationAPIView(APIView):
    def post(self,request):
        data = request.data
        email = data.get("email")

        if not email:
            return Response(base_error_response("Email is required"), 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(base_error_response("User with this email does not exist"), 
                            status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response(base_error_response("Email is already verified"), 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            self.send_email_verification_mail(user)
        except Exception as e:
            return Response(base_error_response("Failed to send verification email: {}".format(str(e))), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(base_success_response("Verification email sent successfully"), status=status.HTTP_200_OK)

    def send_email_verification_mail(self, user):
        token = user.generate_email_verification_token()

        send_mail(
            subject='Email Verification Token',
            message='Your email verification token is: {}'.format(token),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=f"""
            <p>Hi {user.first_name},</p>
            <p>Your email verification token is: <strong>{token}</strong>. This
            will expire in 1 hour.</p> """
        )


class LoginView(APIView):
    def post(self,request):
        data = request.data

        email = data.get("email")
        password = data.get("password")

        try:
            user = CustomUser.objects.get(email = email)
        except CustomUser.DoesNotExist:
            return Response(base_error_response("Invalid Email and Password"),
                            status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response(base_error_response("User is not Active"),
                            status=status.HTTP_400_BAD_REQUEST)
        if not user.is_email_verified:
            return Response(base_error_response("Email is not verified"), 
                            status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response(base_error_response("Invalid Email and Password"),
                            status=status.HTTP_400_BAD_REQUEST)

        ecom_refresh_token = RefreshToken.for_user(user)
        ecom_access_token = str(ecom_refresh_token.access_token)

        data = {
            'user_id' : user.id,
            'email' : user.email,
            'ecom_access_token' : ecom_access_token,
        }

        response = Response(base_success_response("Login successful",data = data),
                        status=status.HTTP_200_OK)

        cookie_max_age = 60*60*24*30
        host = request.get_host()

        if host.startswith('127.0.0.1') or host.startswith('localhost'):
            cookie_domain = None
        else:
            cookie_domain = os.getenv('COOKIE_DOMAIN')

        response.set_cookie(
            key = 'ecom_refresh_token',
            value= ecom_refresh_token,
            httponly=True,
            secure=True,
            samesite='None',
            domain=cookie_domain,
            max_age=cookie_max_age,
        )

        response.set_cookie(
            key = 'ecom_access_token',
            value= ecom_access_token,
            httponly=True,
            secure=True,
            samesite='None',
            domain=cookie_domain,
            max_age=cookie_max_age,
        )

        return response


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('ecom_refresh_token')
        if not refresh_token:
            return Response(base_error_response("Refresh token not found"), 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            old_refresh_token = RefreshToken(refresh_token)
            old_refresh_token.blacklist()

            payload = old_refresh_token.payload
            user_id = payload.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)
            
            response = Response(base_success_response("Token refreshed successfully"),status=status.HTTP_200_OK)
            cookie_max_age = 60 * 60 * 24 * 30
            host = request.get_host()

            if host.startswith('127.0.0.1') or host.startswith('localhost'):
                cookie_domain = None
            else:
                cookie_domain = os.getenv('COOKIE_DOMAIN')
       
            response.set_cookie(
                key = 'ecom_access_token',
                value= new_access_token,
                httponly=True,
                secure=True,
                samesite='None',
                domain=cookie_domain,
                max_age=cookie_max_age,
            )

            response.set_cookie(
                key='ecom_refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=cookie_max_age,
                domain=cookie_domain
            )

            return response
        except CustomUser.DoesNotExist:
            return Response(base_error_response("User not found"), 
                            status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(base_error_response("Invalid refresh token"), 
                            status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get('ecom_refresh_token')
        if not refresh_token:
            return Response(base_error_response("Refresh token not found"), 
                            status=status.HTTP_400_BAD_REQUEST)
        
        old_refresh_token = RefreshToken(refresh_token)
        old_refresh_token.blacklist()

        response = Response(base_success_response("Logout Successfully"),
                            status=status.HTTP_200_OK)

        past_date = http_date((datetime.datetime.now(datetime.UTC) - timedelta(days=1)).timestamp())

        host = request.get_host()

        if host.startswith('127.0.0.1') or host.startswith('localhost'):
            cookie_domain = None
        else:
            cookie_domain = os.getenv('COOKIE_DOMAIN')

        response.set_cookie(
            key='ecom_access_token',
            value='',
            httponly=True,
            secure=True,
            samesite='None',
            max_age=0,
            expires=past_date,
            domain=cookie_domain
        )

        response.set_cookie(
            key='ecom_refresh_token',
            value='',
            httponly=True,
            secure=True,
            samesite='None',
            max_age=0,
            expires=past_date,
            domain=cookie_domain
        )
        
        return response

class UpdatePasswordAPIView(APIView):
    
    #authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            old_pass = data.get('old_password')
            new_pass = data.get('new_password')

            if not old_pass:
                return Response(base_error_response("Old password is required"), 
                                status=status.HTTP_400_BAD_REQUEST)

            if not new_pass:
                return Response(base_error_response("New password is required"), 
                                status=status.HTTP_400_BAD_REQUEST)

            if not user_id:
                return Response(base_error_response("User ID is required"), 
                                status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_false(CustomUser, id=user_id)

            if not user:
                return Response(base_error_response("User not found"), 
                                status=status.HTTP_400_BAD_REQUEST)
            
            if not user.check_password(old_pass):
                return Response(base_error_response("Old password is incorrect"), 
                                status=status.HTTP_400_BAD_REQUEST)
    
            user.set_password(new_pass)
            user.save()
            
            return Response(base_success_response("Password updated successfully"),
                            status = status.HTTP_200_OK)
            
        except Exception as e:
            return Response(base_error_response("Failed to update password: {}".format(str(e))), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#==    Request Password Reset API    ==#
class RequestPasswordResetAPIView(APIView):
    def post(self,request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response(base_error_response('email is required'),
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(base_error_response("User with this email does not exist"), 
                            status=status.HTTP_404_NOT_FOUND)

        try:
            self.send_password_reset_email(user)
        except Exception as e:
            return Response(base_error_response("Failed to send password reset email: {}".format(str(e))), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(base_success_response("Password reset link sent to your email"), 
                    status=status.HTTP_200_OK)

        
    def send_password_reset_email(self, user):
        token = user.generate_password_reset_token()

        send_mail(
                    subject='Password Reset Token',
                    message='Your password reset token is: {}'.format(token),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    html_message=f"""
                    <p>Hi {user.first_name},</p>
                    <p>Your password reset token is: <strong>{token}</strong>. This
                    will expire in 24 hours.</p> """
                )

#==    Verify Password Reset OTP    ==#
class VerifyPasswordResetOTPAPIView(APIView):
    def post(self,request):
        data = request.data
        token = data.get('otp')

        if not token:
            return Response(base_error_response('OTP is Required'))

        user = get_object_or_false(CustomUser, password_reset_token=token)

        if not user:
            return Response(base_error_response("Invalid OTP"),
                            status=status.HTTP_400_BAD_REQUEST)

        if user.paasword_token_expired < timezone.now():
            return Response(base_error_response("OTP has Expired"))

        return Response(base_success_response("OTP verified successfully"),
                        status=status.HTTP_200_OK)


#==    Chnage Password API    ==#
class ChangePasswordAPIView(APIView):
    def post(self,request):
        data = request.data
        token = data.get('otp')
        new_password = data.get('new_password')

        if not new_password:
            return Response(base_error_response("New password is required"),
                            status=status.HTTP_400_BAD_REQUEST)
        
        if not token:
                return Response(base_error_response("OTP is required"), 
                                status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_false(CustomUser, password_reset_token=token)

        if not user:
                return Response(base_error_response("Invalid OTP"), 
                                status=status.HTTP_400_BAD_REQUEST)

        if user.paasword_token_expired < timezone.now():
            return Response(base_error_response("OTP has expired"), 
                                status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expire = None
        user.save()

        return Response(base_success_response("Password updated successfully"),
                        status=status.HTTP_200_OK)

        
    






    
            


        



        






########  Product List API ##########

class ProductListView(APIView):

    def get(self, request):
        products = Product.objects.filter(product_status='publish')
        if not products.exists():
            return Response(base_error_response("No products found"), 
                            status=status.HTTP_404_NOT_FOUND)
        product_serializer = ProductSerializer(products, many=True, context={'request': request})
        if not product_serializer.data:
            return Response(base_error_response("Failed to serialize product data"), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(base_success_response("Products retrieved successfully", 
                                              data=product_serializer.data),
                                              status=status.HTTP_200_OK)
    

    def post(self, request):
        data = request.data
        serializer = ProductDetailSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(base_success_response("Product created successfully", 
                                                  data=serializer.data),
                                                  status=status.HTTP_201_CREATED)
        return Response(base_error_response("Failed to create product", errors=serializer.errors), 
                        status=status.HTTP_400_BAD_REQUEST)


########  Product Detail API ##########

class ProductDetailView(APIView):

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, product_status='publish')
        except Product.DoesNotExist:
            return Response(base_error_response("Product not found"), 
                            status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductDetailSerializer(product, context={'request': request})
        if not product_serializer.data:
            return Response(base_error_response("Failed to serialize product data"), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(base_success_response("Product retrieved successfully", 
                                              data=product_serializer.data),
                                              status=status.HTTP_200_OK)
    

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(base_error_response("Product not found"), 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(base_success_response("Product updated successfully", 
                                                  data=serializer.data),
                                                  status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to update product", errors=serializer.errors), 
                        status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):

        product = Product.objects.get(id=pk)

        if not product:
            return Response(
                base_error_response("Product not found"),
                status=status.HTTP_404_NOT_FOUND
            )
        

        # store thumbnail path before deleting object
        thumbnail_path = product.thumbnail.path if product.thumbnail else None

        thumbnail_deletion_failed = False

        # delete product from database
        product.delete()

        # delete image file from media folder
        if thumbnail_path:
            if os.path.exists(thumbnail_path):
                try:
                    os.remove(thumbnail_path)
                except Exception:
                    thumbnail_deletion_failed = True
            else:
                thumbnail_deletion_failed = True

        message = "Product deleted successfully"

        if thumbnail_deletion_failed:
            message += " (but failed to delete thumbnail file)"

        return Response(
            base_success_response(message),
            status=status.HTTP_200_OK
        )


########  Category List API ##########

class CategoryListView(APIView):

    def get(self,request):
        category = Category.objects.filter(is_active=True)
        if not category:
            return Response(base_error_response("Category not found"),
            status = status.HTTP_404_NOT_FOUND)

        category_serialize = CategoryListSerializer(category,many=True)

        if not category_serialize.data:
            return Response(base_error_response("Failed to serialize category data"),
            status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(base_success_response("Category Retrived Successfully",
        data = category_serialize.data), status = status.HTTP_200_OK)


    def post(self,request):
        data = request.data
        serialize = CategorySerializer(data = data)
        if serialize.is_valid():
            serialize.save()
            return Response(base_success_response("Category Create Successfully",
            data= serialize.data),status=status.HTTP_201_CREATED)

        return Response(base_error_response("Faild to create category",errors = serialize.errors),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


########  Category Detail API ##########

class CategoryDetailAPI(APIView):

    def get(self,request,pk):
        category = Category.objects.get(id=pk)
        if not category:
            return Response(base_error_response("Cateogory not found"),
            status=status.HTTP_404_NOT_FOUND)

        if not category.is_active:
            return Response(base_error_response("Cateogory not active"),
            status=status.HTTP_404_NOT_FOUND)
        
        category_serializer = CategorySerializer(category , context={'request': request})

        if category_serializer.data:
            return Response(base_success_response("Category retrived successfully",
            data=category_serializer.data),status=status.HTTP_200_OK)

        return Response(base_error_response("Category failed to serialized",errors=category_serializer.errors),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self,request,pk):
        data = request.data
        category = Category.objects.get(id=pk)

        if not category:
            return Response(base_error_response("Cateogory not found"),
            status=status.HTTP_404_NOT_FOUND)

        category_serializer = CategorySerializer(category,data=data,partial=True)

        if category_serializer.is_valid():
            category_serializer.save()
            return Response(base_success_response("Category updated successfully",data=category_serializer.data),
            status=status.HTTP_200_OK)

        return Response(base_error_response("Category can not update",errors=category_serializer.errors),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self,request,pk):
        category = Category.objects.get(id=pk)

        if not category:
            return Response(base_error_response("Cateogory not found"),
            status=status.HTTP_404_NOT_FOUND)


        category.delete()

        return Response(base_success_response("Category delate successfully"),
        status=status.HTTP_200_OK)


########  Subcategory List API ##########

class SubCategoryListView(APIView):

    def get(self, request):

        subcategories = SubCategory.objects.filter(is_active=True)
        if not subcategories.exists():
            return Response(base_error_response("No subcategories found"), 
                            status=status.HTTP_404_NOT_FOUND)

        subcategory_serializer = SubCategorySerializer(subcategories, many=True)
        if subcategory_serializer.data:
            return Response(base_success_response("Subcategories retrieved successfully", 
                                              data = subcategory_serializer.data),
                                            status=status.HTTP_200_OK,)
        
        return Response(base_error_response("Failed to serialize subcategory data", errors=subcategory_serializer.errors),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):

        subcategory_serializer = SubCategorySerializer(data=request.data, context={'request': request})
        if subcategory_serializer.is_valid():
            subcategory_serializer.save()
            return Response(base_success_response("Subcategory created successfully", 
                                                  data = subcategory_serializer.data ), 
                                                  status=status.HTTP_201_CREATED)
        return Response(base_error_response("Failed to create subcategory", 
                                            errors=subcategory_serializer.errors),
                                            status=status.HTTP_400_BAD_REQUEST)


########  Subcategory Detail API ##########

class SubCategoryDetailView(APIView):

    def get(self, request, pk):

        try:
            subcategory = SubCategory.objects.get(id=pk, is_active=True)
        except SubCategory.DoesNotExist:
            return Response(base_error_response("Subcategory not found or inactive"), 
                            status=status.HTTP_404_NOT_FOUND)

        subcategory_serializer = SubCategorySerializer(subcategory, context={'request': request})
        if subcategory_serializer.data:
            return Response(base_success_response("Subcategory retrieved successfully", 
                                              data=subcategory_serializer.data), 
                                              status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to serialize subcategory data",  
                                            errors=subcategory_serializer.errors),
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)     

    def put(self, request, pk):

        try:
            subcategory = SubCategory.objects.get(id=pk)
        except SubCategory.DoesNotExist:
            return Response(base_error_response("Subcategory not found"), 
                            status=status.HTTP_404_NOT_FOUND)
        subcategory_serializer = SubCategorySerializer(subcategory, data=request.data, partial=True, context={'request': request})
        if subcategory_serializer.is_valid():
            subcategory_serializer.save()
            return Response(base_success_response("Subcategory updated successfully", 
                                                  data=subcategory_serializer.data), 
                                                  status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to update subcategory", 
                                            errors=subcategory_serializer.errors),
                                            status=status.HTTP_400_BAD_REQUEST) 
    
    def delete(self, request, pk):
        try:
            subcategory = SubCategory.objects.get(id=pk)
        except SubCategory.DoesNotExist:
            return Response(base_error_response("Subcategory not found"), 
                            status=status.HTTP_404_NOT_FOUND)

        subcategory.delete()

        return Response(base_success_response("Subcategory deleted successfully"), 
                        status=status.HTTP_200_OK)


########  Products by Subcategory API ##########    

class ProductsBySubcategoryView(APIView):

    def get(self, request, subcategory_pk):

        try:
            subcategory = SubCategory.objects.get(id=subcategory_pk, is_active=True)
        except SubCategory.DoesNotExist:
            return Response(base_error_response("Subcategory not found or inactive"), 
                            status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(subcategory=subcategory, product_status='publish')
        if not products.exists():
            return Response(base_error_response("No products found for this subcategory"), 
                            status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductSerializer(products, many=True, context={'request': request})
        if product_serializer.data:
            return Response(base_success_response("Products retrieved successfully", 
                                              data=product_serializer.data), 
                                              status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to serialize product data", 
                                            errors=product_serializer.errors),
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


########  Products by Category API ##########  

class ProductsByCategoryView(APIView):

    def get(self, request, category_pk):

        try:
            category = Category.objects.get(id=category_pk, is_active=True)
        except Category.DoesNotExist:
            return Response(base_error_response("Category not found or inactive"), 
                            status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(subcategory__category=category, product_status='publish')
        if not products.exists():
            return Response(base_error_response("No products found for this category"), 
                            status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductSerializer(products, many=True, context={'request': request})
        if product_serializer.data:
            return Response(base_success_response("Products retrieved successfully", 
                                              data=product_serializer.data), 
                                              status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to serialize product data", 
                                            errors=product_serializer.errors),
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        

class GeneralSettingsView(APIView):

    def get(self, request):
        settings = GeneralSettings.objects.first()
        if not settings:
            return Response(base_error_response("General settings not found"), 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = GeneralSettingsSerializer(settings, context={'request': request})
        if serializer.data:
            return Response(base_success_response("General settings retrieved successfully", 
                                              data=serializer.data), 
                                              status=status.HTTP_200_OK)
        return Response(base_error_response("Failed to serialize general settings data", 
                                            errors=serializer.errors),
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)





