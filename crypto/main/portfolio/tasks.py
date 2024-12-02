from .models import Portfolio, PortfolioHistory
from .views import get_portfolio_value


def record_portfolio_value():
    for portfolio in Portfolio.objects.all():
        total_value, _ = get_portfolio_value(portfolio)
        PortfolioHistory.objects.create(portfolio=portfolio, total_value=total_value)
