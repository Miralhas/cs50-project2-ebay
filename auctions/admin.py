from django.contrib import admin
from .models import AuctionListing, User, Bid

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("bidings", )

admin.site.register(AuctionListing)
admin.site.register(User)
admin.site.register(Bid)
