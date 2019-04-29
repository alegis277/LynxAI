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

	userType = list(request.user.groups.values_list('name',flat=True))[0]

	if userType == MEDICS:
		return render(request, 'medics.html')
	elif userType == PATIENTS:
		return render(request, 'patients.html')
	elif userType == LABS:
		return render(request, 'labs.html')
	elif userType == BOOKING:
		return render(request, 'booking.html')

	return HttpResponse("No user type has been set - Contact admin")

@login_required
def logout_user(request):
	logout(request)
	return redirect('/accounts/login')