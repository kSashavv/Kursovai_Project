from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import CustomUserForm, CustomAuthentication, PortfolioForm
from .models import CoinList, Portfolio


# def home(request):
#     cryptos = CoinList.objects.all()
#     if request.method == 'POST':
#         form = CryptoCurrencyForm(request.POST)
#         currency_id = request.POST.get('name')
#         price = Api_Coin_Gekko.coin_price(currency_id)
#         if form.is_valid():
#             form.save()
#             print(price)
#             return render(request, 'home.html', {'form': form, 'cryptos': cryptos, 'price': price})
#     else:
#         form = CryptoCurrencyForm()
#
#         return render(request, 'home.html', {'form': form, 'cryptos': cryptos})


def home(request):
    if request.user.is_authenticated:
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
    else:
        return redirect('regis')

    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            # portfolio_save = form.save(commit=False)  # Временное сохранение объекта
            # portfolio_save.user = request.user  # Присваиваем текущего пользователя
            # portfolio_save.save()  # Сохраняем объект в базе данных
            coins = form.cleaned_data['coins']
            for coin in coins:
                portfolio.coins.add(coin)
            # portfolio_data = Portfolio.objects.all(user_id=request.user)
            # print(portfolio_data.coins)
            return redirect('home')
            # return render(request, 'home.html', {'form': form})
        else:
            return render(request, 'home.html', {'form': form, 'error': 'Что-то не так'})
    else:
        form = PortfolioForm()
        return render(request, 'home.html', {'form': form})


def search_coins(request):
    query = request.GET.get('q', '')
    coins = CoinList.objects.filter(name__icontains=query)[:10]  # Ограничиваем количество результатов
    results = [{'id': coin.id, 'text': coin.name} for coin in coins]
    return JsonResponse({'results': results})


def UserCreation(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user_save = form.save()
            # user = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password')
            # aunt = authenticate(username=user, password=password)
            # login(request, aunt)
            login(request, user_save)
            return redirect('home')
        else:
            return render(request, 'UserCreationForm.html', {'form': form})
    else:
        form = CustomUserForm()
        return render(request, 'UserCreationForm.html', {'form': form})


def Authenticate(request):
    if request.method == 'POST':
        form = CustomAuthentication(request.POST, data=request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            aunt = authenticate(username=user, password=password)
            login(request, aunt)
            return redirect('home')
        else:
            print('#####################')
            print('Error')
            return render(request, 'AuthenticationForm.html', {'form': form})
    else:
        form = CustomAuthentication()
        return render(request, 'AuthenticationForm.html', {'form': form})


# def Authenticate(request):
#     if request.method == 'POST':
#         form = CustomAuthentication(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 print('#####################')
#                 print('Error: Invalid username or password')
#         else:
#             print('#####################')
#             print('Error: Form is not valid')
#     else:
#         form = CustomAuthentication()
#     return render(request, 'AuthenticationForm.html', {'form': form})


def _logout(request):
    logout(request)
    return redirect('home')


@login_required
def portfolio(request):
    portfolio = Portfolio.objects.get(user=request.user)
    coins = portfolio.coins.all()
    print(coins)
    return render(request, 'portfolio.html', {'coins': coins})
