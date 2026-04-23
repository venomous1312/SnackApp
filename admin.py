from django.contrib import admin
from .models import Business, SnackBox, SnackOrder, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(SnackOrder)
class SnackOrderAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'customer_name', 'status', 'delivery_info', 'get_total')
    inlines = [OrderItemInline]

    def delivery_info(self, obj):
        return obj.get_delivery_date()

    def get_total(self, obj):
        # DO NOT use parentheses () here because it is a @property
        return obj.total_price 
    
    get_total.short_description = 'Order Total'

admin.site.register(SnackBox)
admin.site.register(Business)
