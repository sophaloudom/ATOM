from django.contrib import admin
from .models import Product, Watch, Notification, Departure, ServiceAlert, AlertPreference
for model in [Product, Watch, Notification, Departure, ServiceAlert, AlertPreference]: admin.site.register(model)
