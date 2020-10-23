from django.contrib import admin

from app.models import Restaurant, City, Category, Options


class RestaurantsInline(admin.TabularInline):
    model = Restaurant.cities.through
    extra = 0


class RestaurantsCategoryInline(admin.TabularInline):
    model = Restaurant.categories.through
    extra = 0


class RestaurantsOptionInline(admin.TabularInline):
    model = Restaurant.options.through
    extra = 0


class CityAdmin(admin.ModelAdmin):
    inlines = [RestaurantsInline]


class CategoryAdmin(admin.ModelAdmin):
    inlines = [RestaurantsCategoryInline]


class OptionsAdmin(admin.ModelAdmin):
    inlines = [RestaurantsOptionInline]


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'coordinates']
    list_display_links = ['name']
    list_filter = ['cities']
    search_fields = ['name', 'address']


admin.site.register(Options, OptionsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(City, CityAdmin)
