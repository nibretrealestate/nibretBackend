from rest_framework import serializers
from .models import Location, Property, Image, Amenties, Auction, Wishlist, Reviews


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    property = serializers.UUIDField(read_only=True)
    class Meta:
        model = Image
        fields = '__all__'

class AmentiesSerializer(serializers.ModelSerializer):
    property = serializers.UUIDField(read_only=True)
    class Meta:
        model = Amenties
        fields = '__all__'

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    pictures = ImageSerializer(many=True)
    amenties = AmentiesSerializer()

    class Meta:
        model = Property
        fields = '__all__'

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        amenties_data = validated_data.pop('amenties')
        image_data = validated_data.pop('pictures')
        
        # Create location first
        location = Location.objects.create(**location_data)
        # validated_data['created_by'] = request.user
        # Create property
        property = Property.objects.create(location=location, **validated_data)
        
        # Create amenities with property reference
        amenties_data['property'] = property
        Amenties.objects.create(**amenties_data)

        for image in image_data:
            image['property'] = property
            Image.objects.create(**image)
        
        return property

    def update(self, instance, validated_data):
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            Location.objects.filter(id=instance.location.id).update(**location_data)
        
        if 'amenties' in validated_data:
            amenties_data = validated_data.pop('amenties')
            Amenties.objects.filter(property=instance).update(**amenties_data)
            
        return super().update(instance, validated_data)
    
class WishListSerializer(serializers.ModelSerializer):
      class Meta:
        model = Wishlist
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
      class Meta:
        model = Reviews
        fields = '__all__'
