from django.contrib import admin
from .models import Stock, Owned

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('symbol',)}


@admin.register(Owned)
class OwnedAdmin(admin.ModelAdmin):
    pass
