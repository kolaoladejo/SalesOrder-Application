from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import OrderForm, CreateUserForm
from .models import *
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from django.contrib.auth.models import Group
# Create your views here.

@unauthenticated_user
def registerPage(request):
    # if request.user.is_authenticated:
    #    return redirect('home')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            #password = form.cleaned_data.get('password1')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(user=user)
            messages.success(request, 'Account is created for ' + username)
            # user = authenticate(username=username, password=password)
            # login(request, user)
            return redirect('login')
        
    context = {'form':form}
    return render(request, 'register.html', context)
    
    
    
@unauthenticated_user
def loginPage(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    # else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
               login(request, user)
               return redirect('home')
            else:
                messages.info(request, 'Username or password is incorrect')
        context = {}
        return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
#@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    #total_customers = customers.count()
    forders = orders.order_by('-date_created')[:5]
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders,'customers':customers,
    'total_orders':total_orders,'delivered':delivered,
    'pending':pending,'forders':forders}

    return render(request, 'dashboard.html', context)

@login_required (login_url='login')
#@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,
    'pending':pending}

    return render(request, 'user.html', context)


@login_required (login_url='login')
#@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    context = {}
    return render(request, 'account_settings.html', context)

@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'products.html', {'products':products})
@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context= {'customer':customer,'orders':orders,'order_count':order_count,'myFilter':myFilter}
    return render(request, 'customer.html', context)
@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset':formset}
    return render(request, 'order_form.html', context)
@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request, 'update.html', context)
@login_required (login_url='login')
#@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item':order} 
    return render(request, 'delete.html', context)
