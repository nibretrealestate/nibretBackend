from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from properties.serializers import *
from properties.permissions import *


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    # permission_classes = [IsAuthenticated]

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [PropertyPermission]


    def get_queryset(self):
        queryset = Property.objects.all()
        
        # Filter by type
        property_type = self.request.query_params.get('type', None)
        if property_type:
            queryset = queryset.filter(type=property_type)

        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by location
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        radius = self.request.query_params.get('radius', None)
        if all([latitude, longitude, radius]):
            # Add location-based filtering logic here
            pass

        return queryset

    @action(detail=False, methods=['get'])
    def auctions(self):
        auctions = self.get_queryset().filter(is_auction=True)
        serializer = self.get_serializer(auctions, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            data['created_by'] =  request.user.id
            
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            properties = serializer.save()
            properties.refresh_from_db()
            serializer = self.get_serializer(properties)

            headers = self.get_success_headers(serializer.data)
            return Response({"detail": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(e)
            return Response(
                {"detail": f"Something went wrong while creating property"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        property_id = request.data.get('property_id')
        images = request.data.get('images', [])
        
        property = get_object_or_404(Property, id=property_id)
        created_images = []

        for image_data in images:
            image_data['property'] = property.id
            serializer = self.get_serializer(data=image_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_images.append(serializer.data)

        return Response(created_images, status=status.HTTP_201_CREATED)

class AmentiesViewSet(viewsets.ModelViewSet):
    queryset = Amenties.objects.all()
    serializer_class = AmentiesSerializer
    # permission_classes = [IsAuthenticated]

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def place_bid(self, request, pk=None):
        auction = self.get_object()
        bid_amount = request.data.get('bid_amount')

        if not bid_amount:
            return Response(
                {'error': 'Bid amount is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if auction.current_bid and bid_amount <= auction.current_bid:
            return Response(
                {'error': 'Bid must be higher than current bid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if bid_amount < auction.starting_bid:
            return Response(
                {'error': 'Bid must be higher than starting bid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        auction.current_bid = bid_amount
        auction.save()
        return Response(self.get_serializer(auction).data)

