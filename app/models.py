from django.db import models


class City(models.Model):
    """Модель, описывающая город"""
    name = models.CharField(max_length=35)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return f'{self.name}, {self.pk}'


class Category(models.Model):
    """Модель, описывающая категорию ресторана
    (например, 'быстро и не дорого' или 'приятно провести время')"""
    name = models.CharField(max_length=35)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} {self.pk}'


class Options(models.Model):
    """Модель, описывающая дополнительные опции ресторана
    (например, 'веранда' или 'дог-френдли')"""
    name = models.CharField(max_length=35)
    emoji = models.CharField(max_length=5)

    class Meta:
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'

    def __str__(self):
        return f'{self.pk}: {self.emoji} {self.name}'


class Restaurant(models.Model):
    """Модель, описывающая ресторан"""
    name = models.CharField(max_length=55)
    short_description = models.CharField(max_length=350)
    address = models.TextField()
    full_description = models.TextField()
    cities = models.ManyToManyField(City)
    categories = models.ManyToManyField(Category)
    google_map_link = models.CharField(max_length=250)
    options = models.ManyToManyField(Options, blank=True)
    coordinates = models.CharField(max_length=150, blank=True, null=True)
    

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'

    def __str__(self):
        return f'{self.name}'
