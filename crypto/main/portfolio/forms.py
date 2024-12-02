from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import CoinList, Portfolio, PortfolioCoin


class CryptoCurrencyForm(forms.ModelForm):
    class Meta:
        model = CoinList
        fields = ['name']


class PortfolioForm(forms.ModelForm):
    coins = forms.ModelMultipleChoiceField(
        queryset=CoinList.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )

    class Meta:
        model = Portfolio
        fields = ['coins']


class CustomUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label='Номер Телефона', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email', 'password1', 'password2',)


class CustomAuthentication(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class PortfolioCoinForm(forms.Form):
    coin = forms.ModelMultipleChoiceField(
        queryset=CoinList.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),  # Интеграция select2
        required=True
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        required=True
    )
