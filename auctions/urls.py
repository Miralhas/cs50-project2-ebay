from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist_page, name="watchlist_page"),
    path("categories", views.categories, name="categories"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("categories/<str:title>", views.category_page, name="category_page"),
    path("listings/<int:listing_pk>", views.listing_page, name="listing_page"),
    path("listings/<int:listing_pk>/finish", views.finish_auction, name="finish_auction"),
    path("listings/<int:listing_pk>/comment", views.comment, name="comment"),
    path("listings/<int:listing_pk>/watchlist", views.watchlist, name="watchlist"),
]
