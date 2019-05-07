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

	path('ajax_getPatientData/', views.ajax_getPatientData, name='ajax_getPatientData'),
	path('ajax_askWatson/', views.ajax_askWatson, name='ajax_askWatson'),
	path('ajax_endAppointment/', views.ajax_endAppointment, name='ajax_endAppointment'),
	path('ajax_saveUserData/', views.ajax_saveUserData, name='ajax_saveUserData'),
	path('ajax_bookLab/', views.ajax_bookLab, name='ajax_bookLab'),
	path('ajax_watsonDiseaseData/', views.ajax_watsonDiseaseData, name='ajax_watsonDiseaseData'),

	path('ajax_getCalendarLab/', views.ajax_getCalendarLab, name='ajax_getCalendarLab'),
	path('ajax_getExamInfo/', views.ajax_getExamInfo, name='ajax_getExamInfo'),


]
