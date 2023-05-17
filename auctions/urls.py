from django.urls import path
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import search_view

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("auctions/<int:bidid>", views.listingpage, name="listingpage"),
    path("watchlist/<str:username>", views.watchlistpage, name = "watchlistpage"),
    path("added", views.addwatchlist, name = "addwatchlist"),
    path("delete", views.deletewatchlist, name = "deletewatchlist"),
    path("bidlist", views.bid, name="bid"),
    path("comments", views.allcomments, name="allcomments"),
    path("win_ner", views.win_ner, name="win_ner"),
    path("winnings", views.winnings, name="winnings"),
    path("cat_list", views.cat_list, name="cat_list"),
    path("categories/<str:category_name>", views.cat, name="cat"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("send_email", views.send_email, name="send_email"),
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('search/', search_view, name='search'),
    
]

