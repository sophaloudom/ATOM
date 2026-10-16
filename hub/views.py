from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django import forms

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit: user.save()
        return user

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product, Watch, Notification, Departure, ServiceAlert, AlertPreference
from .services import weather

def dashboard(request):
    city = request.GET.get('city', request.session.get('city', 'auckland'))
    if city not in ('auckland', 'wellington'): city = 'auckland'
    request.session['city'] = city
    products = Product.objects.all().order_by('name')
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    if query: products = products.filter(name__icontains=query)
    if category: products = products.filter(category=category)
    section = request.GET.get('view', 'overview')
    watched = set(Watch.objects.filter(user=request.user).values_list('product_id', flat=True)) if request.user.is_authenticated else set()
    if section == 'watchlist': products = products.filter(pk__in=watched)
    if request.GET.get('sale'): products = products.filter(price__lt=F('regular_price'))
    notifications = Notification.objects.filter(user=request.user)[:20] if request.user.is_authenticated else []
    return render(request, 'hub/dashboard.html', {'products': products[:60], 'categories': Product.objects.values_list('category',flat=True).distinct().order_by('category'), 'preference': AlertPreference.objects.filter(user=request.user).first() if request.user.is_authenticated else None, 'watched': watched, 'notifications': notifications, 'city': city, 'city_name': city.title(), 'weather': weather(city), 'departures': Departure.objects.filter(city=city).order_by('minutes'), 'alerts': ServiceAlert.objects.filter(active=True, city=city), 'section': section, 'query': query, 'category': category, 'sale_count': Product.objects.filter(price__lt=F('regular_price')).count(), 'watch_count': len(watched)})

def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(); AlertPreference.objects.create(user=user,city=request.session.get('city','auckland')); login(request,user); return redirect('dashboard')
    return render(request,'hub/auth.html',{'form':form,'signup':True})

@login_required
@require_POST
def watch(request, pk):
    product = get_object_or_404(Product,pk=pk)
    obj, created = Watch.objects.get_or_create(user=request.user, product=product)
    if not created: obj.delete()
    elif product.discount: Notification.objects.create(user=request.user,title=f'{product.name} is currently {product.discount}% off at {product.store}.')
    messages.success(request, 'Added to your watchlist. We’ll notify you of price drops.' if created else 'Removed from your watchlist.')
    return redirect('dashboard')

@login_required
@require_POST
def read_notifications(request):
    Notification.objects.filter(user=request.user,read=False).update(read=True)
    return redirect('/?view=notifications')

@login_required
@require_POST
def preferences(request):
    city = request.POST.get('city', 'auckland')
    if city not in ('auckland', 'wellington'): city = 'auckland'
    AlertPreference.objects.update_or_create(user=request.user, defaults={'city':city,'weather':'weather' in request.POST,'transport':'transport' in request.POST})
    messages.success(request,'Alert preferences saved. New local notices will appear here and in your email queue.')
    return redirect('/?view=notifications')

# A health request checks database connectivity without contacting external feeds.
def health(request):
    from django.db import connection
    from django.http import JsonResponse
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
