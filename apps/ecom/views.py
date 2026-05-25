from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import Product
from .response import base_error_response, base_success_response, Codenco
from .serializer import *
import os


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

        category_serialize = CategorySerializer(category,many=True)

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
        
        category_serializer = CategorySerializer(category)

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



        

    

   


