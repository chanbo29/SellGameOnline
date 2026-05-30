import random
import string
import json
import csv
# import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth
from django.http import HttpResponse
from .forms import GameForm, RegisterForm
from .models import Game, Wishlist, Cart, Purchase
from django.contrib.auth.decorators import login_required, user_passes_test

#Admin dashboard (optional)
def login_view(request):

    if request.user.is_authenticated:
        return redirect('game_list')

    error = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('game_list')

        error = 'Invalid username or password'

    return render(request, 'games/login.html', {
        'error': error
    })


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    purchases = Purchase.objects.all().order_by('-purchased_at')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        purchases = purchases.filter(
            purchased_at__date__range=[start_date, end_date]
        )

    total_games = Game.objects.count()
    total_orders = purchases.count()
    total_sales = purchases.aggregate(total=Sum('price'))['total'] or 0
    total_users = User.objects.count()

    monthly_revenue = (
        Purchase.objects
        .annotate(month=TruncMonth('purchased_at'))
        .values('month')
        .annotate(total=Sum('price'))
        .order_by('month')
    )

    chart_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    chart_data = [float(item['total']) for item in monthly_revenue]

    best_selling_games = (
        Purchase.objects
        .values('game__title')
        .annotate(total_sold=Count('id'), revenue=Sum('price'))
        .order_by('-total_sold')[:5]
    )

    return render(request, 'games/admin_dashboard.html', {
        'purchases': purchases,
        'total_games': total_games,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_users': total_users,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'best_selling_games': best_selling_games,
    })
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    users = User.objects.annotate(
        total_spent=Sum('purchase__price'),
        total_orders=Count('purchase')
    ).order_by('-total_spent')

    return render(request, 'games/admin_users.html', {
        'users': users
    })
@login_required
@user_passes_test(lambda u: u.is_staff)
def export_purchases_excel(request):
    purchases = Purchase.objects.all().order_by('-purchased_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchases_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Game', 'Price', 'Date'])

    for p in purchases:
        writer.writerow([
            p.user.username,
            p.game.title,
            p.price,
            p.purchased_at
        ])

    return response
def home(request):

    games = Game.objects.all()

    return render(request,'home.html',{
        'games': games
    })
def user_login(request):

    # Already logged in
    if request.user.is_authenticated:
        return redirect('game_list')

    error = ''

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('game_list')

        else:

            error = 'Invalid username or password'

    return render(request, 'games/login.html', {
        'error': error
    })
def user_logout(request):

    logout(request)

    return redirect('/login/')
def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # AFTER REGISTER GO LOGIN PAGE
        return redirect('/login/')

    return render(request, 'games/register.html')
def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(
                form.cleaned_data['password']
            )

            user.save()

            login(request, user)

            return redirect('/')

    else:
        form = RegisterForm()

    return render(request,
                  'games/register.html',
                  {'form': form})

def login_page(request):

    if request.user.is_authenticated:
        return redirect('game_list')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('game_list')   # Steam-style redirect

        return render(request, 'games/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'games/login.html')
def logout_view(request):

    logout(request)

    return redirect('/login/')

# បង្ហាញបញ្ជីហ្គេមទាំងអស់ (ទំព័រដើម)=
#@login_required(login_url='/login/')
def game_list(request):
    games = Game.objects.all()

    purchased_game_ids = []

    if request.user.is_authenticated:
        purchased_game_ids = list(
            Purchase.objects.filter(user=request.user)
            .values_list('game_id', flat=True)
        )

    return render(request, 'games/game_list.html', {
        'games': games,
        'purchased_game_ids': purchased_game_ids
    })
# ថែមហ្គេមថ្មី
@login_required(login_url='/login/')
@login_required
def add_game(request):

    if not request.user.is_staff:
        return redirect('/')

    form = GameForm(request.POST or None,
                    request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('/')

    return render(request,
                  'games/game_form.html',
                  {'form': form})

@login_required(login_url='/login/')
def buy_game(request, game_id):

    game = get_object_or_404(Game, id=game_id)

    already_bought = Purchase.objects.filter(
        user=request.user,
        game=game
    ).exists()

    if already_bought:
        return redirect('library')

    return render(request, 'games/pay_money.html', {
        'game': game,
        'game_title': game.title,
        'amount': game.final_price()
    })
@login_required
def purchase_history(request):
    purchases = Purchase.objects.filter(
        user=request.user
    ).order_by('-purchased_at')
    return render(request, 'games/history.html', {
        'purchases': purchases
    })
@login_required
def admin_sales(request):
    if not request.user.is_staff:
        return redirect("/")
    sales = Purchase.objects.all().order_by("-purchased_at")
    total_sales = sum(s.price for s in sales)
    return render(request, "admin_sales.html", {
        "sales": sales,
        "total_sales": total_sales
    })
@login_required
def add_wishlist(request, game_id):
    game = Game.objects.get(id=game_id)
    Wishlist.objects.get_or_create(
        user=request.user,
        game=game
    )
    return redirect('wishlist')
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).order_by('-added_date')

    return render(request, 'games/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def remove_wishlist(request, game_id):
    Wishlist.objects.filter(
        user=request.user,
        game_id=game_id
    ).delete()

    return redirect('wishlist')

@login_required
def add_cart(request, game_id):

    game = Game.objects.get(id=game_id)

    Cart.objects.get_or_create(
        user=request.user,
        game=game
    )

    return redirect('cart')


@login_required
def cart(request):

    cart_items = Cart.objects.filter(
        user=request.user
    ).order_by('-added_date')

    total = 0

    for item in cart_items:
        total += item.game.final_price()

    return render(request, 'games/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def remove_cart(request, game_id):

    Cart.objects.filter(
        user=request.user,
        game_id=game_id
    ).delete()

    return redirect('cart')

@login_required
def add_game(request):
    if not request.user.is_staff:
        return redirect('/')

    form = GameForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('/')

    return render(request, 'games/add_game.html', {
        'form': form
    })
# កែប្រែព័ត៌មានហ្គេម
@login_required(login_url='/login/')
def edit_game(request, id):
    if not request.user.is_staff:
        return redirect('/')
    game = get_object_or_404(Game, id=id)
    if request.method == 'POST':
        form = GameForm(
            request.POST,
            request.FILES,
            instance=game
        )
        if form.is_valid():
            form.save()
            return redirect('game_list')
        else:
            print(form.errors)
    else:
        form = GameForm(instance=game)
    return render(request, 'games/update_game.html', {
        'form': form,
        'game': game
    })
# លុបហ្គេម
@login_required
def delete_game(request, id):

    if not request.user.is_staff:
        return redirect('/')

    game = get_object_or_404(Game, id=id)

    game.delete()

    return redirect('/')
@login_required
def buy_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request,
                  'games/pay_money.html',
                  {
                      'game': game,
                      'game_title': game.title,
                      'amount': game.final_price()
                  })
@login_required
def delete_library_game(request, game_id):
    if request.method == "POST":
        purchase = get_object_or_404(
            Purchase,
            user=request.user,
            game_id=game_id
        )
        purchase.delete()

    return redirect('/library/')
# បន្ថែមបន្ទាត់នេះនៅខាងក្រោមគេក្នុងឯកសារ views.py របស់អ្នក
@login_required(login_url='/login/')
def pay_success(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, id=game_id)

        redeem_code = generate_redeem_code()

        request.session['redeem_code'] = redeem_code
        request.session['game_id'] = game.id

        return render(request, 'games/pay_success.html', {
            'game': game,
            'game_title': game.title,
            'amount': game.final_price(),
            'redeem_code': redeem_code
        })
    
    return redirect('/')
# from .models import Purchase
# COMPLETE_PAYMENT
@login_required(login_url='/login/')
def complete_payment(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        user_code = request.POST.get('redeem_code')
        session_code = request.session.get('redeem_code')

        if user_code != session_code:
            messages.error(request, 'Invalid redeem code!')
            return redirect('/buy/' + str(game_id) + '/')

        game = get_object_or_404(Game, id=game_id)

        Purchase.objects.create(
            user=request.user,
            game=game,
            price=game.final_price()
        )

#         # TELEGRAM ALERT
#         bot_token = "YOUR_BOT_TOKEN"
#         chat_id = "YOUR_CHAT_ID"

#         text = f"""
# 🎮 New Game Payment

# User: {request.user.username}
# Game: {game.title}
# Price: ${game.final_price()}
# Redeem Code: {session_code}
# Status: Paid with ABA
# """

#         requests.post(
#             f"https://api.telegram.org/bot{bot_token}/sendMessage",
#             data={
#                 "chat_id": chat_id,
#                 "text": text
#             }
#         )

        return redirect('download_game', game_id=game.id)

    return redirect('/')
#SHOW_REDEEM_CODE
@login_required(login_url='/login/')
def show_redeem_code(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, id=game_id)

        redeem_code = generate_redeem_code()

        request.session['redeem_code'] = redeem_code
        request.session['game_id'] = game.id

        return render(request, 'games/pay_success.html', {
            'game': game,
            'game_title': game.title,
            'amount': game.final_price(),
            'redeem_code': redeem_code,
            'show_redeem': True
        })

    return redirect('/')
#DOWNLOAD
@login_required(login_url='/login/')
def download_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    return render(request, 'games/download.html', {
        'game': game
    })
# LIBRARY
@login_required
def library(request):
    purchased_games = Purchase.objects.filter(user=request.user)

    return render(request, 'games/library.html', {
        'purchased_games': purchased_games
    })
@login_required(login_url='/login/')
def delete_library(request, id):
    purchase = get_object_or_404(
        Purchase,
        id=id,
        user=request.user
    )
    purchase.delete()

    return redirect('library')
# PURCHASE_HISTORY
@login_required
def purchase_history(request):

    purchases = [
        {
            "title": "Cyberpunk 2077",
            "price": 39.99,
            "date": "22 May 2026",
            "status": "Completed",
            "image": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg"
        },

        {
            "title": "Elden Ring",
            "price": 59.99,
            "date": "20 May 2026",
            "status": "Completed",
            "image": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg"
        }
    ]

    return render(request, "history.html", {
        "purchases": purchases
    })
def about_view(request):
    return render(request, "about.html")
def generate_redeem_code():
    return "WU-" + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )
@login_required(login_url='/login/')
def play_game(request, game_id):

    game = get_object_or_404(Game, id=game_id)

    return render(request, 'games/play_game.html', {
        'game': game
    })