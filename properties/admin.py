from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Property)
admin.site.register(Location)
admin.site.register(Image)
admin.site.register(Amenties)
admin.site.register(Loaners)
admin.site.register(LoanerProperty)
admin.site.register(Wishlist)