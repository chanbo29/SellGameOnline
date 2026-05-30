from django.urls import path
from django.shortcuts import redirect
from . import views
from django.conf import settings
from django.conf.urls.static import static
def home_redirect(request):
    return redirect('login')

urlpatterns = [
    #Admin dashboard (optional)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export-purchases/', views.export_purchases_excel, name='export_purchases_excel'),
    # FIRST PAGE
    path('', views.game_list, name='game_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('add/', views.add_game, name='add_game'),
    # HOME PAGE
    path('games/', views.game_list, name='game_list'),

    # GAME CRUD
    path('update/<int:id>/', views.edit_game, name='edit_game'),
    path('delete/<int:id>/', views.delete_game, name='delete_game'),
    # BUY-HISTORY
    path('buy/<int:game_id>/', views.buy_game, name='buy_game'),
    path('history/', views.purchase_history, name='purchase_history'),
    # PAYMENT
    path('pay-success/', views.pay_success, name='pay_success'),
    #LIBRARY
    path('library/', views.library, name='library'),
    path('library/delete/<int:game_id>/', views.delete_library_game, name='delete_library_game'),
    # PAYMENT_COMPLETED
    path('complete-payment/', views.complete_payment, name='complete_payment'),
    #REDEEM
    path('show-redeem-code/', views.show_redeem_code, name='show_redeem_code'),
    #DOWNLOAD
    path('download/<int:game_id>/', views.download_game, name='download_game'),
    #ADMIN
    path("admin-sales/", views.admin_sales, name="admin_sales"),
    path('admin-users/', views.admin_users, name='admin_users'),

    #ABOUT US
    path("about/", views.about_view, name="about_view"),

    # CART
    path("cart/", views.cart, name="cart"),
    path("add-cart/<int:game_id>/", views.add_cart, name="add_cart"),
    path("remove-cart/<int:game_id>/", views.remove_cart, name="remove_cart"),
    path('cart/add/<int:game_id>/', views.add_cart, name='add_cart'),
    path('buy/<int:game_id>/', views.buy_game, name='buy_game'),
    #PLAY GAME
    path('play/<int:game_id>/', views.play_game, name='play_game'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )