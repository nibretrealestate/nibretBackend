from rest_framework import serializers
from .models import AuctionImage, Location, Property, Image, Amenties, Auction, Wishlist, Reviews, RequestedTour


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
    start_date = serializers.SerializerMethodField()
    location = LocationSerializer()
    pictures = ImageSerializer(many=True)

    class Meta:
        model = Auction
        fields = '__all__'

    def get_start_date(self, obj):
        return obj.start_date.strftime("%Y-%m-%d")

    def create(self, validated_data):
        # Extract nested data
        location_data = validated_data.pop('location')
        pictures_data = validated_data.pop('pictures', [])

        # Create location first
        location = Location.objects.create(**location_data)

        # Create auction with the location
        auction = Auction.objects.create(location=location, **validated_data)

        # Create pictures
        for picture_data in pictures_data:
            AuctionImage.objects.create(auction=auction, **picture_data)

        return auction

    def update(self, instance, validated_data):
        # Handle location update
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            location = instance.location
            for attr, value in location_data.items():
                setattr(location, attr, value)
            location.save()

        # Handle pictures update
        if 'pictures' in validated_data:
            pictures_data = validated_data.pop('pictures')
            # Optional: Delete existing pictures
            instance.pictures.all().delete()
            # Create new pictures
            for picture_data in pictures_data:
                AuctionImage.objects.create(auction=instance, **picture_data)

        # Update remaining auction fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

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
    property = PropertySerializer(many=True, read_only=True)  # Include properties
    auctions = serializers.PrimaryKeyRelatedField(many=True, queryset=Auction.objects.all())  # Allow IDs for auctions

    class Meta:
        model = Wishlist
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
      class Meta:
        model = Reviews
        fields = '__all__'


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        models = RequestedTour
        fields = '__all__'