from models import StoreCategory, Store, Category, MenuItem, Order 
from django.contrib import admin

class StoreCategoryAdmin(admin.ModelAdmin):
    pass

class StoreAdmin(admin.ModelAdmin):
    pass

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    ordering = ('store',)

class MenuItemAdmin(admin.ModelAdmin):
    list_filter = ('category', 'active')
    ordering = ('category',) 
    search_fields = ('name', 'description')

class OrderAdmin(admin.ModelAdmin):
    pass

admin.site.register(StoreCategory, StoreCategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order, OrderAdmin)

