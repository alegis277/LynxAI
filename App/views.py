from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# User type flags
MEDICS = 'medics'
PATIENTS = 'patients'
LABS = 'labs'
BOOKING = 'booking'


@login_required
def index(request):

	userType = list(request.user.groups.values_list('name',flat=True))
	userType = -1 if len(userType)==0 else userType[0]

	if userType == MEDICS:
		return render(request, 'medics.html')
	elif userType == PATIENTS:
		return render(request, 'patients.html')
	elif userType == LABS:
		return render(request, 'labs.html')
	elif userType == BOOKING:
		return render(request, 'booking.html')

	return render(request, 'unknown.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/accounts/login')