from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import psycopg2
import simplejson as json
from django.contrib.auth.models import User

# User type flags
MEDICS = 'medics'
PATIENTS = 'patients'
LABS = 'labs'
BOOKING = 'booking'


@login_required
def index(request):

	dbConnect = psycopg2.connect(database="djfdlbhx", user="djfdlbhx", password="Pm_v8zZfV-l5ahcv5AZWmNX9rnKd7zds", host = "isilo.db.elephantsql.com", port = "5432")
	cursor=dbConnect.cursor()

	userType = list(request.user.groups.values_list('name',flat=True))
	userType = -1 if len(userType)==0 else userType[0]

	if userType == MEDICS:
		dbConnect.commit()
		dbConnect.close()
		labs = list(User.objects.filter(groups__name='labs'))

		labNames = [labActual.first_name for labActual in labs]
		labIds = [labActual.id for labActual in labs]
		return render(request, 'medics.html', {'name':request.user.first_name+" "+request.user.last_name, 'id_doc' : str(request.user.id), 'labs':zip(labIds, labNames)})
	elif userType == PATIENTS:
		dbConnect.commit()
		dbConnect.close()
		return render(request, 'patients.html')
	elif userType == LABS:
		dbConnect.commit()
		dbConnect.close()
		return render(request, 'labs.html')



	elif userType == BOOKING:
		id_user = str(request.user.id)

		sql="select id_user_doctor from booking_relations where id_user_booking=%s"
		cursor.execute(sql,[id_user])
		relations = cursor.fetchall()



		sql="select first_name,last_name,id from auth_user where id = "+str(relations[0][0])
		for relation in relations:
			sql+=" or id = "+str(relation[0])

		cursor.execute(sql)
		doctors_related = cursor.fetchall()


		doctors_related_final = []
		for doctor in doctors_related:
			doctors_related_final.append([[doctor[0] + " "+ doctor[1]],[doctor[2]]])


		dbConnect.commit()
		dbConnect.close()
		return render(request, 'booking.html', {'name':request.user.first_name+" "+request.user.last_name, 'doctors_related':doctors_related_final})

	dbConnect.commit()
	dbConnect.close()
	return render(request, 'unknown.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/accounts/login')



@login_required
def ajax_checkUser(request):

	id_check = str(request.POST['id_check'])


	dbConnect = psycopg2.connect(database="djfdlbhx", user="djfdlbhx", password="Pm_v8zZfV-l5ahcv5AZWmNX9rnKd7zds", host = "isilo.db.elephantsql.com", port = "5432")
	cursor=dbConnect.cursor()
	sql="select first_name, last_name from auth_user where id=%s"
	cursor.execute(sql,[id_check])
	name = cursor.fetchall()
	dbConnect.commit()
	dbConnect.close()


	data = {}
	if len(name)>0:
		data['patient_name'] = name[0][0] + " "+ name[0][1]
	else:
		data['patient_name'] = "Not found"

	return HttpResponse(json.dumps(data))

@login_required
def ajax_makeAppointment(request):

	doc_id = str(request.POST['doc_id'])
	patient_id = str(request.POST['patient_id'])
	complaint = str(request.POST['complaint'])
	date = str(request.POST['date'])

	dbConnect = psycopg2.connect(database="djfdlbhx", user="djfdlbhx", password="Pm_v8zZfV-l5ahcv5AZWmNX9rnKd7zds", host = "isilo.db.elephantsql.com", port = "5432")
	cursor=dbConnect.cursor()
	sql="insert into appointments (id_user, complaint, start_time, end_time, id_doctor) values (%s, %s, %s, %s, %s)"
	cursor.execute(sql,[patient_id, complaint, date, date, doc_id])
	dbConnect.commit()
	dbConnect.close()

	return HttpResponse("")


@login_required
def ajax_getCalendar(request):

	doc_id = str(request.POST['doc_id'])


	dbConnect = psycopg2.connect(database="djfdlbhx", user="djfdlbhx", password="Pm_v8zZfV-l5ahcv5AZWmNX9rnKd7zds", host = "isilo.db.elephantsql.com", port = "5432")
	cursor=dbConnect.cursor()
	sql="SELECT (id_user, start_time) from appointments where id_doctor=%s"
	cursor.execute(sql,[doc_id])
	iduser_date = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in iduser_date:

		string_base = data_database[0]
		string_base = string_base.strip('(').strip(')').split(',')

		iduser = string_base[0]
		date = string_base[1].strip('"')

		sql="select first_name, last_name from auth_user where id=%s"
		cursor.execute(sql,[iduser])
		name = cursor.fetchall()
		patient_name = name[0][0] + " "+ name[0][1]

		
		dataToAppend = {'title': patient_name, 'start': date, 'end': date,'id':iduser, 'imageurl':"/static/profile/"+str(iduser)+".jpg"}
		data['source'].append(dataToAppend)

	dbConnect.commit()
	dbConnect.close()

	return HttpResponse(json.dumps(data))


@login_required
def ajax_getPatientData(request):
	return HttpResponse("")




@login_required
def ajax_askWatson(request):
	return HttpResponse("")




@login_required
def ajax_endAppointment(request):
	return HttpResponse("")




@login_required
def ajax_saveUserData(request):
	return HttpResponse("")




@login_required
def ajax_bookLab(request):
	return HttpResponse("")


@login_required
def ajax_watsonDiseaseData(request):
	return HttpResponse("")


