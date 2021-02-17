from django.shortcuts import render
from .models import Stock, Owned
from django.views.generic import ListView, DetailView
from django.db.models import Sum, F


class StockListView(ListView):
    template_name = 'index.html'
    context_object_name = 'owned_stock'
    model = Owned

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # calculate total portfolio value
        context['total_current'] = Owned.objects.all().aggregate(
            total=Sum(F('stock__current_value')*F('shares_owned'))
        )

        # calculate total purchase value
        context['total_purchased'] = Owned.objects.all().aggregate(
            total=Sum(F('value_purchased_at')*F('shares_owned'))
        )

        # calculate % change in portfolio value
        context['total_change'] = 100*(context['total_current']['total'] - context['total_purchased']['total']) / context['total_purchased']['total']

        return context

class StockDetailView(DetailView):
    model = Stock
    template_name = 'detail.html'
    context_object_name = 'stock'