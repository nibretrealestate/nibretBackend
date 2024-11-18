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

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all() 
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Automatically create a wishlist for the user if it doesn't exist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return Response(WishListSerializer(wishlist).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_items(self, request):
        # Get the user's wishlist
        wishlist = self.get_queryset().first()  # Get the user's wishlist

        if not wishlist:
            return Response({"error": "Wishlist does not exist."}, status=status.HTTP_404_NOT_FOUND)

        properties = request.data.get('properties', [])
        auctions = request.data.get('auctions', [])

        # Add properties to the wishlist
        if properties:
            for property_id in properties:
                try:
                    property_instance = Property.objects.get(id=property_id)
                    wishlist.property.add(property_instance)
                except Property.DoesNotExist:
                    return Response({"error": f"Property with id {property_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Add auctions to the wishlist
        if auctions:
            for auction_id in auctions:
                try:
                    auction_instance = Auction.objects.get(id=auction_id)
                    wishlist.auctions.add(auction_instance)
                except Auction.DoesNotExist:
                    return Response({"error": f"Auction with id {auction_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(WishListSerializer(wishlist).data, status=status.HTTP_200_OK)
    
class RequestedTourViewSet(viewsets.ModelViewSet):
    queryset = RequestedTour.objects.all() 
    serializer_class = TourSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        request.data['user'] = request.user.department

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        tour = serializer.save()

        tour.refresh_from_db()
        serializer = self.get_serializer(receiving_note)

        headers = self.get_success_headers(serializer.data)
        return Response({"detail": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)