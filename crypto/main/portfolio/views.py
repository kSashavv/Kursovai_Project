from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserForm, CustomAuthentication, PortfolioCoinForm
from .models import CoinList, Portfolio, PortfolioCoin, Coin
import requests
from django.core.cache import cache
from .Api_Coin_Gekko import coin_price
from decimal import Decimal
from .models import PortfolioHistory
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone


def get_portfolio_value(portfolio):
    base_url = 'https://api.coingecko.com/api/v3/simple/price'
    symbols = [coin.coin.symbol for coin in PortfolioCoin.objects.filter(portfolio=portfolio)]
    query_params = {
        'ids': ','.join(symbols),
        'vs_currencies': 'usd'
    }
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        prices = response.json()
        total_value = 0
        detailed_values = []
        for coin in PortfolioCoin.objects.filter(portfolio=portfolio):
            coin_price = prices.get(coin.coin.symbol, {}).get('usd', 0)
            coin_value = coin.amount * coin_price
            total_value += coin_value
            detailed_values.append({
                'coin': coin.coin.name,
                'symbol': coin.coin.symbol,
                'amount': coin.amount,
                'price': coin_price,
                'value': coin_value
            })
        return total_value, detailed_values
    else:
        return 0, []


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    portfolio, created = Portfolio.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PortfolioCoinForm(request.POST)
        if form.is_valid():
            coins = form.cleaned_data['coin']  # Получаем список выбранных монет
            amount = form.cleaned_data['amount']

            for coin in coins:  # Перебираем монеты и сохраняем их по одной
                PortfolioCoin.objects.update_or_create(
                    portfolio=portfolio,
                    coin=coin,
                    defaults={'amount': amount}
                )
            return redirect('profile')  # Перенаправление в личный кабинет

        else:
            return render(request, 'home.html', {'form': form, 'error': 'Invalid input'})

    else:
        form = PortfolioCoinForm()

    return render(request, 'home.html', {'form': form})


def update_portfolio_history(portfolio, total_value):
    PortfolioHistory.objects.create(
        portfolio=portfolio,
        total_value=total_value,
        timestamp=timezone.now()
    )


@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('regis')  # Редирект, если пользователь не авторизован

    portfolio = Portfolio.objects.filter(user=request.user).first()

    if not portfolio:
        return HttpResponseBadRequest("Портфель не найден")

    # Используем правильный способ получения связанных объектов
    portfolio_coins = PortfolioCoin.objects.filter(portfolio=portfolio)

    # Получаем цену для каждой монеты
    for portfolio_coin in portfolio_coins:
        coin_id = portfolio_coin.coin.currency_id  # Уникальный идентификатор монеты
        try:
            # Получаем цену с помощью функции coin_price_cached
            price_data = coin_price_cached(coin_id)
            if not price_data:  # Если данные пустые, пропускаем
                print(f"Не удалось получить данные для {coin_id}. Пропускаем...")
                continue

            price = Decimal(price_data.get(coin_id, {}).get('usd', 0))  # Преобразуем в Decimal

            # Обновляем цену в модели PortfolioCoin
            portfolio_coin.price = price
            portfolio_coin.save()

            # Добавляем атрибут `total_value` для удобства
            portfolio_coin.total_value = portfolio_coin.amount * portfolio_coin.price
        except Exception as e:
            print(f"Ошибка получения цены для {coin_id}: {e}")

    # Расчет общей стоимости портфеля
    total_value = sum(
        portfolio_coin.total_value for portfolio_coin in portfolio_coins if portfolio_coin.price
    )

    # Обновляем историю портфеля
    update_portfolio_history(portfolio, total_value)

    # Обработка POST-запроса
    if request.method == 'POST':
        coin_id = request.POST.get('coin_id')
        amount = Decimal(request.POST.get('amount'))
        action = request.POST.get('action')

        try:
            portfolio_coin = portfolio_coins.get(coin__id=coin_id)
        except PortfolioCoin.DoesNotExist:
            return HttpResponseBadRequest("Монета не найдена в портфеле")

        if action == 'update':
            portfolio_coin.amount = amount
            portfolio_coin.save()
        elif action == 'sell':
            if portfolio_coin.amount < amount:
                return HttpResponseBadRequest("Недостаточно монет для продажи")
            elif portfolio_coin.amount == amount:
                portfolio_coin.delete()
            else:
                portfolio_coin.amount -= amount
                portfolio_coin.save()

        return redirect('profile')

    context = {
        'portfolio': portfolio,
        'portfolio_coins': portfolio_coins,
        'total_value': total_value,
    }

    history = PortfolioHistory.objects.filter(portfolio=portfolio).order_by('timestamp')
    history_data = {
        'timestamps': [entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') for entry in history],
        'values': [float(entry.total_value) for entry in history]
    }
    context['history_data'] = json.dumps(history_data, cls=DjangoJSONEncoder)

    pie_data = {
        'labels': [coin.coin.name for coin in portfolio_coins],
        'values': [float(coin.total_value) for coin in portfolio_coins if coin.total_value]
    }
    context['pie_data'] = json.dumps(pie_data)

    return render(request, 'profile.html', context)

    # if not request.user.is_authenticated:
    #     return redirect('regis')  # Редирект, если пользователь не авторизован
    #
    # portfolio = Portfolio.objects.filter(user=request.user).first()
    #
    # if not portfolio:
    #     return HttpResponseBadRequest("Портфель не найден")
    #
    # # Используем правильный способ получения связанных объектов
    # portfolio_coins = PortfolioCoin.objects.filter(portfolio=portfolio)
    #
    # # Получаем цену для каждой монеты
    # for portfolio_coin in portfolio_coins:
    #     coin_id = portfolio_coin.coin.currency_id  # Уникальный идентификатор монеты
    #     try:
    #         # Получаем цену с помощью функции coin_price_cached
    #         price_data = coin_price_cached(coin_id)
    #         if not price_data:  # Если данные пустые, пропускаем
    #             print(f"Не удалось получить данные для {coin_id}. Пропускаем...")
    #             continue
    #
    #         price = Decimal(price_data.get(coin_id, {}).get('usd', 0))  # Преобразуем в Decimal
    #
    #         # Обновляем цену в модели PortfolioCoin
    #         portfolio_coin.price = price
    #         portfolio_coin.save()
    #
    #         # Добавляем атрибут `total_value` для удобства
    #         portfolio_coin.total_value = portfolio_coin.amount * portfolio_coin.price
    #     except Exception as e:
    #         print(f"Ошибка получения цены для {coin_id}: {e}")
    #
    # # Расчет общей стоимости портфеля
    # total_value = sum(
    #     portfolio_coin.total_value for portfolio_coin in portfolio_coins if portfolio_coin.price
    # )
    #
    # # Обработка POST-запроса
    # if request.method == 'POST':
    #     coin_id = request.POST.get('coin_id')
    #     amount = Decimal(request.POST.get('amount'))
    #     action = request.POST.get('action')
    #
    #     try:
    #         portfolio_coin = portfolio_coins.get(coin__id=coin_id)
    #     except PortfolioCoin.DoesNotExist:
    #         return HttpResponseBadRequest("Монета не найдена в портфеле")
    #
    #     if action == 'update':
    #         portfolio_coin.amount = amount
    #         portfolio_coin.save()
    #     elif action == 'sell':
    #         if portfolio_coin.amount < amount:
    #             return HttpResponseBadRequest("Недостаточно монет для продажи")
    #         elif portfolio_coin.amount == amount:
    #             portfolio_coin.delete()
    #         else:
    #             portfolio_coin.amount -= amount
    #             portfolio_coin.save()
    #
    #     return redirect('profile')
    #
    # context = {
    #     'portfolio': portfolio,
    #     'portfolio_coins': portfolio_coins,
    #     'total_value': total_value,
    # }
    #
    # history = PortfolioHistory.objects.filter(portfolio=portfolio).order_by('timestamp')
    # history_data = {
    #     'timestamps': [entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') for entry in history],
    #     'values': [float(entry.total_value) for entry in history]
    # }
    # context['history_data'] = json.dumps(history_data, cls=DjangoJSONEncoder)
    #
    # pie_data = {
    #     'labels': [coin.coin.name for coin in portfolio_coins],
    #     'values': [float(coin.total_value) for coin in portfolio_coins if coin.total_value]
    # }
    # context['pie_data'] = json.dumps(pie_data)
    #
    # return render(request, 'profile.html', context)


@require_POST
@login_required
def update_coin(request):
    coin_id = request.POST.get('coin_id')
    new_amount = request.POST.get('new_amount')

    portfolio = get_object_or_404(Portfolio, user=request.user)
    try:
        portfolio_coin = PortfolioCoin.objects.get(portfolio=portfolio, coin__id=coin_id)
        portfolio_coin.amount = Decimal(new_amount)
        portfolio_coin.save()
    except PortfolioCoin.DoesNotExist:
        return JsonResponse({'error': 'Актив не найден'}, status=400)

    return redirect('profile')


@require_POST
@login_required
def sell_coin(request):
    coin_id = request.POST.get('coin_id')

    portfolio = get_object_or_404(Portfolio, user=request.user)
    try:
        portfolio_coin = PortfolioCoin.objects.get(portfolio=portfolio, coin__id=coin_id)
        portfolio_coin.delete()  # Удаляем актив из портфеля
    except PortfolioCoin.DoesNotExist:
        return JsonResponse({'error': 'Актив не найден'}, status=400)

    return redirect('profile')


def coin_price_cached(currency_id):
    cache_key = f"coin_price_{currency_id}"
    price_data = cache.get(cache_key)  # Получаем данные из кэша

    if price_data is None:  # Если данных нет, запрашиваем через API
        price_data = coin_price(currency_id)  # Функция возвращает полный словарь
        if price_data:  # Если словарь не пустой
            cache.set(cache_key, price_data, timeout=300)  # Кэшируем полный словарь на 5 минут
        else:
            print(f"Не удалось получить данные для {currency_id}, кэширование пропущено.")
            return {}

    return price_data  # Возвращаем словарь или пустой объект


def search_coins(request):
    query = request.GET.get('q', '')  # Получаем текст из запроса
    coins = CoinList.objects.filter(name__icontains=query)[:10]  # Ограничиваем результаты
    results = [{'id': coin.id, 'text': coin.name} for coin in coins]  # Формат JSON
    return JsonResponse({'results': results})


def UserCreation(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user_save = form.save()
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


def _logout(request):
    logout(request)
    return redirect('home')


@login_required
def portfolio(request):
    portfolio = Portfolio.objects.get(user=request.user)
    coins = portfolio.coins.all()
    print(coins)
    return render(request, 'portfolio.html', {'coins': coins})


def manage_coin(request):
    if request.method == 'POST':
        coin_id = request.POST.get('coin_id')
        amount = Decimal(request.POST.get('amount'))
        action = request.POST.get('action')

        portfolio = Portfolio.objects.filter(user=request.user).first()

        if not portfolio:
            return HttpResponseBadRequest("Портфель не найден")

        try:
            portfolio_coin = PortfolioCoin.objects.get(portfolio=portfolio, coin__id=coin_id)
        except PortfolioCoin.DoesNotExist:
            return HttpResponseBadRequest("Монета не найдена в портфеле")

        if action == 'update':
            portfolio_coin.amount = amount
            portfolio_coin.save()
        elif action == 'sell':
            if portfolio_coin.amount < amount:
                return HttpResponseBadRequest("Недостаточно монет для продажи")
            elif portfolio_coin.amount == amount:
                portfolio_coin.delete()
            else:
                portfolio_coin.amount -= amount
                portfolio_coin.save()

        return redirect('profile')

    return HttpResponseBadRequest("Неверный метод запроса")


def get_portfolio_history(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Пользователь не авторизован"}, status=401)

    portfolio = Portfolio.objects.filter(user=request.user).first()

    if not portfolio:
        return JsonResponse({"error": "Портфель не найден"}, status=404)

    history = PortfolioHistory.objects.filter(portfolio=portfolio).order_by('timestamp')
    history_data = {
        'timestamps': [entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') for entry in history],
        'values': [float(entry.total_value) for entry in history]
    }
    print(history_data)

    return JsonResponse(history_data)

def get_bitcoin_price_history(request):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '60',  # Получаем данные за последние 60 дней
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    data = response.json()

    prices = data['prices']
    timestamps = [price[0] for price in prices]
    values = [price[1] for price in prices]

    history_data = {
        'timestamps': timestamps,
        'values': values
    }

    return JsonResponse(history_data)
