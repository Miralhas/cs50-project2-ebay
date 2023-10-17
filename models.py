from django.contrib.auth.models import AbstractUser
from django.db import models


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    img_url = models.URLField()
    total_bidings = models.IntegerField(default=0)
    auction_status = models.BooleanField(default=True)
    auction_winner = models.CharField(max_length=32, default=None)


    def __str__(self):
        return f"{self.title}"


class User(AbstractUser):
    listings = models.ManyToManyField(AuctionListing, blank=True, related_name="owner")
    
    def __str__(self):
        return f"{self.username}"
    

class Bid(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="first_bid")
    bid_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    new_bid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Auction: {self.auction_listing} | New Bid: {self.new_bid} | By: {self.bid_user}"
    
# Class