from rest_framework import serializers
from .models import *

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'first_name', 'last_name',]


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['image1', 'image2', 'image3', 'image4', 'image5']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        for field in ['image1', 'image2', 'image3', 'image4', 'image5']:
            image_field = getattr(instance, field)
            if image_field and hasattr(image_field, 'url'):
                representation[field] = request.build_absolute_uri(image_field.url)
            else:
                representation[field] = None
        return representation
        

class ProductDetailSerializer(serializers.ModelSerializer):

    created_by = UserInfoSerializer(read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_code', 'title', 'slug', 'ingredients', 'product_type', 'product_status', 'thumbnail','short_description', 'long_description', 'images', 'created_by', 'created_at', 'updated_at']

        read_only_fields = ['created_by', 'created_at', 'slug', 'updated_at', 'images']
        write_only_fields = ['thumbnail']

        extra_kwargs = {
            'product_code': {'required': False, },
            'title': {'required': False, },
            'ingredients': {'required': False,},
            'product_type': {'required': False, },
            'product_status': {'required': False,  },
            'short_description': {'required': False,  },
            'long_description': {'required': False,  },
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.thumbnail and hasattr(instance.thumbnail, 'url'):
            representation['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
        else:
            representation['thumbnail'] = None
        return representation
    
    def create(self, validated_data):
        user = CustomUser.objects.get(id = 1)
        validated_data['created_by'] = user
        return super().create(validated_data)

    def get_images(self, obj):
        image = obj.images.first()
        thumbnail = obj.thumbnail
        if thumbnail and hasattr(thumbnail, 'url'):
            thumbnail_url = self.context.get('request').build_absolute_uri(thumbnail.url)
        if image:
            data = ProductImageSerializer(image, context=self.context).data
            data['thumbnail'] = thumbnail_url if thumbnail_url else None
            return data
        return None
 

class ProductSerializer(serializers.ModelSerializer):
    created_by = UserInfoSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_code', 'title', 'slug', 'product_status', 'thumbnail', 'created_by', 'created_at']

        read_only_fields = ['created_by', 'created_at', 'slug', 'product_code']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.thumbnail and hasattr(instance.thumbnail, 'url'):
            representation['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
        else:
            representation['thumbnail'] = None
        return representation