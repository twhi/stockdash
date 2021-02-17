from django.core.management.base import BaseCommand, CommandError

from app.platforms import EToro, Trading212, Finnhub
from app.models import Stock, Owned


class Command(BaseCommand):
    help = 'WIP: Scrapes data from platforms with live positions'

    def handle(self, *args, **options):
        
        positions = dict()

        e = EToro(headless=True)
        login_success = e.login()
        if login_success:
            positions['eToro'] = e.get_owned()

        t = Trading212(headless=True)
        login_success = t.login()
        if login_success:
            positions['Trading 212'] = t.get_owned()
        
        Owned.objects.all().delete()
        
        for platform, data in positions.items():
            for position in data:
                try:
                    print(f'fetching stock {position["symbol"]}')
                    s = Stock.objects.get(symbol=position['symbol'])
                except Stock.DoesNotExist:
                    print(f"stock {position['symbol']} does not exist! Creating one...")
                    f = Finnhub(position['symbol'])
                    s = Stock.objects.create(
                        symbol = position['symbol'],
                        name = f.stock_name,
                        current_value = f.current_value,
                        historical_values = f.last_year
                    )
                finally:
                    print('linking owned stock to DB')
                    o = Owned.objects.create(
                        stock=s, 
                        shares_owned=position['shares_owned'],
                        value_purchased_at=position['value_purchased_at'],
                        platform=platform
                    )
