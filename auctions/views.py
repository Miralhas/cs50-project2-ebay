from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from .models import AuctionListing, User, Bid, Comment, Watchlist, Categories
from django.shortcuts import render
from django.urls import reverse



def index(request):
    return render(request, "auctions/index.html", context={
        "listings": AuctionListing.objects.all()
    })


def new_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    elif request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = float(request.POST["starting_bid"])
        image_url = request.POST["img_url"]
        category = request.POST["category"]
        if title and description and starting_bid and image_url and category:
            listing = AuctionListing.objects.create(
                title=title,
                description=description,
                starting_bid=starting_bid,
                img_url=image_url,
            )
            listing.save()
            category = Categories.objects.create(category_name=category.title(), category_listing=listing)
            category.save()
            user = User.objects.get(username=request.user)
            user.listings.add(listing)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html", context={
                "user": request.user,
                "message": "Error! Preencha todos os campos com os valores válidos!",
            })

    elif request.method == "GET":
        return render(
            request, "auctions/new_listing.html", context={"user": request.user}
        )


def listing_page(request, listing_pk):
    listing = AuctionListing.objects.get(pk=listing_pk)
    comment = listing.listing_comment.all()
        
    if not listing.auction_status:
        template = "auctions/closed_layout.html"
    else:
        template = "auctions/layout.html"
    if request.method == "POST" and request.user.is_authenticated:
        bid_user = request.user
        new_bid = float(request.POST["new_bid"])
        auction = AuctionListing.objects.get(pk=listing_pk)
        first_bid = float(AuctionListing.objects.get(pk=listing_pk).starting_bid)
        
        if new_bid > first_bid:
            bid = Bid(auction_listing=auction, bid_user=bid_user, new_bid=new_bid)
            listing.total_bidings += 1
            listing.starting_bid = new_bid
            bid.save(), listing.save()
            return HttpResponseRedirect(reverse("listing_page", args=(int(listing_pk),)))

        else:
            return render(request, "auctions/listing_page.html", context={
                "listing": listing,
                "message": "ERROR! NEW BID MUST BE HIGHER THAN ACTUAL BID!",
                "template": template
            })
        
    else:
        return render(request, "auctions/listing_page.html", context={
            "listing": listing,
            "owner": listing.owner.first() == request.user,
            "template": template,
            "comments": comment,
        })
    
def finish_auction(request, listing_pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    
    elif request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_pk)
        winner = AuctionListing.objects.get(pk=listing_pk).first_bid.last().bid_user
        listing.auction_status = False
        listing.auction_winner = winner.username
        listing.save()
        return HttpResponseRedirect(reverse("listing_page", args=(int(listing_pk),)))
    else:
        return HttpResponseRedirect(reverse("index"))
    
def comment(request, listing_pk):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_pk)
        comment = request.POST["comment"]
        author = request.user
        comment = Comment.objects.create(text=comment, user_comment=author)
        comment.listing_comment.set([listing])
        comment.save()
        return HttpResponseRedirect(reverse("listing_page", args=(int(listing_pk),)))
    else:
        return HttpResponseRedirect(reverse("index"))

def watchlist(request, listing_pk):
    if request.method == "POST":
        user = request.user
        auc = AuctionListing.objects.get(pk=listing_pk)
        watchlist = Watchlist.objects.create(auction_listing=auc, user_watchlist=user)
        watchlist.save()
        return HttpResponseRedirect(reverse("listing_page", args=(int(listing_pk),)))
    else:
        return HttpResponseRedirect(reverse("index"))
    
def watchlist_page(request):
    user = request.user
    if user.is_authenticated:
        user = User.objects.get(username=user)
        watchlist = user.user_watchlist.all().values("auction_listing").distinct()
        listings = []
        for listing in watchlist:
            x = AuctionListing.objects.get(pk=listing["auction_listing"])
            listings.append(x)
        print(listings)
        # return HttpResponseRedirect(reverse("index"))  
        return render(request, "auctions/watchlist_page.html", context={
            "listings": listings
    })
    else:
        return HttpResponseRedirect(reverse("index"))
    
def categories(request):
    all_categories = Categories.objects.all()
    categories_array = []
    for ctg in all_categories:
        if ctg.category_name in categories_array:
            pass
        else:
            categories_array.append(ctg.category_name)
    x = []
    for ctg in categories_array:
        x.append(Categories.objects.filter(category_name=ctg).values().first())
        
    return render(request, "auctions/categories.html", context={
        "categories": all_categories,
        "teste": x
    })

def category_page(request, title):
    title_x = title
    categories_array = AuctionListing.objects.all()

    return render(request, "auctions/category_page.html", context={
        "title": title_x,
        "categories": categories_array,
    })

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )

    elif request.method == "GET":
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", context={
                    "message": "Passwords must match."
                }
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
