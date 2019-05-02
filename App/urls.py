from django.urls import path
from django.urls import include, re_path
from django.views.generic.base import RedirectView
from django.contrib import admin

favicon_view = RedirectView.as_view(url='/static/favi.ico', permanent=True)

from . import views

urlpatterns = [
	path('favicon.ico', favicon_view, name='favicon'),
	path('myIcon.ico', favicon_view, name='favicon'),
	path('', views.index, name='index'),
	path('admin/', admin.site.urls),
	path('accounts/', include('django.contrib.auth.urls')),
	path('logout_user/', views.logout_user, name='logout_user'),
	path('ajax_checkUser/', views.ajax_checkUser, name='ajax_checkUser'),
	path('ajax_makeAppointment/', views.ajax_makeAppointment, name='ajax_makeAppointment'),
	path('ajax_getCalendar/', views.ajax_getCalendar, name='ajax_getCalendar'),
]