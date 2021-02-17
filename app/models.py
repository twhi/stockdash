from django.db import models
from django.utils.text import slugify


class Stock(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=256)
    current_value = models.FloatField()
    historical_values = models.JSONField(default=list)

    slug = models.SlugField(null=True, unique=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.symbol)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stock-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.symbol} - {self.name}'


class Owned(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares_owned = models.FloatField()
    value_purchased_at = models.FloatField()
    platform = models.CharField(max_length=64)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Owned'

    def __str__(self):
        return f'{self.stock.symbol} - {self.stock.name}'

    @property
    def owned_value(self):
        """
        Calcualates the value of the current stock owned
        """
        return round(self.stock.current_value*self.shares_owned, 2)

    @property
    def value_change(self):
        """
        Calculates the % value change since purchasing
        """
        return round(100*(self.stock.current_value - self.value_purchased_at) / self.value_purchased_at, 2)
