from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
# ADD 'login' and 'logout' TO THIS IMPORT LINE:
from django.contrib.auth import login, logout 
from .forms import CustomerSignUpForm, BusinessSignUpForm
from .models import OrderItem, SnackBox, SnackOrder, Business

def main_menu(request):
    all_businesses = Business.objects.all()
    user_business = None
    if request.user.is_authenticated:
        try:
            user_business = Business.objects.get(owner=request.user)
        except Business.DoesNotExist:
            user_business = None
            
    return render(request, 'delivery/main.html', {
        'all_businesses': all_businesses,
        'business': user_business
    })

@login_required
def driver_portal(request):
    # Fixed: Use a safer way to get the business
    user_business = getattr(request.user, 'business', None) 
    available = SnackOrder.objects.filter(business=user_business, status='READY', driver__isnull=True)
    mine = SnackOrder.objects.filter(business=user_business, status='ON_THE_WAY', driver=request.user)
    
    return render(request, 'delivery/portal.html', {
        'orders': available, 
        'my_orders': mine,
        'business': user_business
    })

# ... (claim_order and complete_order look fine) ...

def place_order(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    
    # CRITICAL FIX: You need to define inventory before using it!
    inventory = SnackBox.objects.filter(business=business)
    
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name': f"{request.user.first_name} {request.user.last_name}",
        }
    
    if request.method == 'POST':
        customer_name = request.POST.get('name')
        address = request.POST.get('address')
        code = request.POST.get('code')
        
        order = SnackOrder.objects.create(
            business=business,
            customer_name=customer_name,
            address=address,
            code=code,
            status='PENDING'
        )
        
        for snack in inventory:
            quantity = request.POST.get(f'snack_{snack.id}')
            if quantity and int(quantity) > 0:
                OrderItem.objects.create(
                    order=order,
                    SnackBox=snack,
                    quantity=int(quantity)
                )
        return redirect(f'/track/?order_id={order.display_id}')

    return render(request, 'delivery/order_form.html', {
        'inventory': inventory, 
        'business': business
    })

# ... (track_order looks fine) ...
def track_order(request):
    order = None
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            # This looks for the unique 8-character ID (e.g., AB12CD34)
            order = SnackOrder.objects.get(display_id=order_id)
        except SnackOrder.DoesNotExist:
            order = "NOT_FOUND"
            
    return render(request, 'delivery/track.html', {'order': order})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()
            # This 'login' now works because of the import at the top
            login(request, user) 
            return redirect('Home')
    else:
        form = CustomerSignUpForm()
    return render(request, 'delivery/customer_register.html', {'form': form})

@login_required
def claim_order(request, order_id):
    # This ensures the driver is picking up an order for the RIGHT business
    order = get_object_or_404(SnackOrder, id=order_id, business=request.user.business)
    order.driver = request.user
    order.status = 'ON_THE_WAY'
    order.save()
    return redirect('driver_portal')

@login_required
def complete_order(request, order_id):
    order = get_object_or_404(SnackOrder, id=order_id, business=request.user.business)
    # Security check: only the driver who claimed it can complete it
    if order.driver == request.user:
        note = request.POST.get('driver_note')
        # This matches the 4-digit security code you created earlier
        if order.code == note:
            order.status = 'DELIVERED'
            order.save()
    return redirect('driver_portal')