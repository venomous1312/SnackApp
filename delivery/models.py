from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Business(models.Model):
    name = models.CharField(max_length=100)
    # The "Owner" of this business (Admin/Manager)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business') 
    slug = models.SlugField(unique=True) # e.g., "varun-snacks"

    def __str__(self):
        return self.name

class SnackBox(models.Model):
    # This ensures a snack belongs only to one business
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventory')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"[{self.business.name}] {self.name} ({self.stock_quantity} left)"

class SnackOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending (Packing)'),
        ('READY', 'Ready for Pickup'),
        ('ON_THE_WAY', 'Claimed by driver'),
        ('DELIVERED', 'Delivered'),
    ]

    # Every order is now tied to a specific business
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='orders')
    
    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    code = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    display_id = models.CharField(max_length=20, editable=False, null=True)

    # Links the order to the driver
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')

    def __str__(self):
        return f"{self.display_id} - {self.customer_name} ({self.business.name})"

    def get_delivery_date(self):
        order_time = self.created_at.astimezone(timezone.get_current_timezone())
        cutoff = order_time.replace(hour=14, minute=0, second=0, microsecond=0)
        if order_time < cutoff:
            return "Delivers Today (after 5:00pm)"
        else: 
            return "Delivers Tomorrow (after 5:00pm)"   

    @property
    def total_price(self):
        items = self.items.all()
        # Ensure we use the correct attribute name 'SnackBox' from the OrderItem model
        total = sum([item.SnackBox.price * item.quantity for item in items])
        return f"${total:.2f}"
    
    def save(self, *args, **kwargs):
        if not self.display_id:
            date_str = timezone.now().strftime('%y%m%d')
            # Now we count orders for THIS business only today
            today_count = SnackOrder.objects.filter(
                business=self.business,
                created_at__date=timezone.now().date()
            ).count() + 1
            self.display_id = f"{date_str}-{today_count:03d}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(SnackOrder, related_name='items', on_delete=models.CASCADE)
    SnackBox = models.ForeignKey(SnackBox, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.SnackBox.name}"