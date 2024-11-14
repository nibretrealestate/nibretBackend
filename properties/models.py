import uuid
from django.db import models

from authentication.models import UserAccount
    
class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255) 
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='property')
    price = models.FloatField()
    discount = models.FloatField(null=True, blank=True, default=0)
    sold_out = models.BooleanField(default=False)
    is_store = models.BooleanField(default=False)
    type = models.CharField(max_length=255, null=True, blank=True)
    move_in_date = models.DateTimeField(null=True, blank=True)
    is_auction = models.BooleanField(default=False)
    created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='saved_properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    is_cover = models.BooleanField(default=False)
    image_url = models.CharField(max_length=255)
    blur_hash = models.CharField(max_length=255, default="blurHash")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return f"Image for {self.property.name}"

class Amenties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    bedroom = models.IntegerField()
    bathroom = models.IntegerField()
    area = models.FloatField()
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='amenties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Amenities for {self.property.name}"

class Auction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    starting_bid = models.FloatField()
    current_bid = models.FloatField(null=True, blank=True)
    min_bid_increment = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='auction')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Auction for {self.property.name}"

    class Meta:
        verbose_name_plural = "Auctions"


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True) 
    user =  models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='wishlist')
    properties = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='properties')
    auctions = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='auctions') 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Reviews(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True) 
    user =  models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='reviews')
    properties = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()