from models import Store, Category, MenuItem, Order, OptionPrice, ChefChoice
from django.contrib import admin

class StoreAdmin(admin.ModelAdmin):
    pass

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    ordering = ('name',)

class OptionPriceAdmin(admin.ModelAdmin):
    pass

class MenuItemAdmin(admin.ModelAdmin):
    list_filter = ('category', 'active')
    ordering = ('category',) 
    search_fields = ('name', 'description')

class ChefChoiceAdmin(admin.ModelAdmin):
    list_display = ('item', 'start_date', 'end_date')

class OrderAdmin(admin.ModelAdmin):
    pass

admin.site.register(Store, StoreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OptionPrice, OptionPriceAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(ChefChoice, ChefChoiceAdmin)
admin.site.register(Order, OrderAdmin)

