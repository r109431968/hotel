from django.contrib import admin
from django.urls import path, include
from hotelApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotelApp.urls')),
]
