from django.contrib import admin
from django.urls import include, path
from .views import StockListView, StockDetailView

urlpatterns = [
    path('', StockListView.as_view()),
    path('stock/<slug:slug>/', StockDetailView.as_view(), name='stock-detail'),
]