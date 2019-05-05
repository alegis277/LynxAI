from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import psycopg2
import simplejson as json
from django.contrib.auth.models import User

import numpy as np
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, ConceptsOptions
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions

# User type flags
MEDICS = 'medics'
PATIENTS = 'patients'
LABS = 'labs'
BOOKING = 'booking'

dbConnect = psycopg2.connect(database="djfdlbhx", user="djfdlbhx", password="Pm_v8zZfV-l5ahcv5AZWmNX9rnKd7zds", host = "isilo.db.elephantsql.com", port = "5432")

@login_required
def index(request):

	
	cursor=dbConnect.cursor()

	userType = list(request.user.groups.values_list('name',flat=True))
	userType = -1 if len(userType)==0 else userType[0]

	if userType == MEDICS:
		dbConnect.commit()
		cursor.close()
		labs = list(User.objects.filter(groups__name='labs'))

		labNames = [labActual.first_name for labActual in labs]
		labIds = [labActual.id for labActual in labs]
		return render(request, 'medics.html', {'name':request.user.first_name+" "+request.user.last_name, 'id_doc' : str(request.user.id), 'labs':zip(labIds, labNames)})
	elif userType == PATIENTS:
		dbConnect.commit()
		cursor.close()
		return render(request, 'patients.html')
	elif userType == LABS:
		dbConnect.commit()
		cursor.close()
		return render(request, 'labs.html')



	elif userType == BOOKING:
		id_user = str(request.user.id)

		sql="SELECT id_user_doctor from booking_relations where id_user_booking=%s"
		cursor.execute(sql,[id_user])
		relations = cursor.fetchall()



		sql="SELECT first_name,last_name,id from auth_user where id = "+str(relations[0][0])
		for relation in relations:
			sql+=" or id = "+str(relation[0])

		cursor.execute(sql)
		doctors_related = cursor.fetchall()


		doctors_related_final = []
		for doctor in doctors_related:
			doctors_related_final.append([[doctor[0] + " "+ doctor[1]],[doctor[2]]])


		dbConnect.commit()
		cursor.close()
		return render(request, 'booking.html', {'name':request.user.first_name+" "+request.user.last_name, 'doctors_related':doctors_related_final})

	dbConnect.commit()
	cursor.close()
	return render(request, 'unknown.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/accounts/login')



@login_required
def ajax_checkUser(request):

	id_check = str(request.POST['id_check'])


	
	cursor=dbConnect.cursor()
	sql="SELECT first_name, last_name from auth_user where id=%s"
	cursor.execute(sql,[id_check])
	name = cursor.fetchall()
	dbConnect.commit()
	cursor.close()


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

	
	cursor=dbConnect.cursor()
	sql="INSERT into appointments (id_user, complaint, start_time, end_time, id_doctor) values (%s, %s, %s, %s, %s)"
	cursor.execute(sql,[patient_id, complaint, date, date, doc_id])
	dbConnect.commit()
	cursor.close()

	return HttpResponse("")


@login_required
def ajax_getCalendar(request):

	doc_id = str(request.POST['doc_id'])


	
	cursor=dbConnect.cursor()
	sql="SELECT (id_user, start_time, id_appointment) from appointments where id_doctor=%s"
	cursor.execute(sql,[doc_id])
	iduser_date = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in iduser_date:

		string_base = data_database[0]
		string_base = string_base.strip('(').strip(')').split(',')

		iduser = string_base[0]
		date = string_base[1].strip('"')
		idappointment = string_base[2]

		sql="SELECT first_name, last_name from auth_user where id=%s"
		cursor.execute(sql,[iduser])
		name = cursor.fetchall()
		patient_name = name[0][0] + " "+ name[0][1]

		
		dataToAppend = {'title': patient_name, 'start': date, 'end': date,'id':iduser, 'imageurl':"/static/profile/"+str(iduser)+".jpg", 'id_appointment':idappointment}
		data['source'].append(dataToAppend)

	dbConnect.commit()
	cursor.close()

	return HttpResponse(json.dumps(data))


@login_required
def ajax_getPatientData(request):

	patient_id = str(request.POST['patient_id'])
	appointment_id = str(request.POST['appointment_id'])




	
	cursor=dbConnect.cursor()

	sql="SELECT first_name from auth_user where id=%s"
	cursor.execute(sql,[patient_id])
	name = cursor.fetchall()
	patient_name = name[0][0]


	sql="SELECT (complaint, symptoms, diagnosis) from appointments where id_appointment=%s"
	cursor.execute(sql,[appointment_id])
	complaint_symptoms_diagnosis = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in complaint_symptoms_diagnosis:

		string_base = data_database[0]
		string_base = string_base.strip('(').strip(')').split(',')

		complaint = string_base[0].strip('"')
		symptoms = string_base[1].strip('"')
		diagnosis = string_base[2].strip('"')


	sql="SELECT (age, height, weight, surgery, current_illness, family_diseases, medication, allergies, sexual_history, gender) from hci where id_user=%s"
	cursor.execute(sql,[patient_id])
	all_data_HCI = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in all_data_HCI:

		string_base = data_database[0]
		string_base = string_base.strip('(').strip(')').split(',')

		age = string_base[0].strip('"')
		height = string_base[1].strip('"')
		weight = string_base[2].strip('"')
		surgeries = string_base[3].strip('"')
		diseases = string_base[4].strip('"')
		family_diseases = string_base[5].strip('"')
		medication = string_base[6].strip('"')
		allergies = string_base[7].strip('"')
		sexual_diseases = string_base[8].strip('"')
		gender = string_base[9].strip('"')


	data = {}

	data['name'] = patient_name

	data['complaint'] = complaint
	data['symptoms'] = symptoms
	data['diagnosis'] = diagnosis

	data['age'] = age
	data['height'] = height
	data['weight'] = weight
	data['gender'] = gender
	data['surgeries'] = surgeries
	data['diseases'] = diseases
	data['family_diseases'] = family_diseases
	data['medication'] = medication
	data['allergies'] = allergies
	data['sexual_diseases'] = sexual_diseases
	

	dbConnect.commit()
	cursor.close()


	return HttpResponse(json.dumps(data))




@login_required
def ajax_saveUserData(request):

	
	cursor=dbConnect.cursor()

	patient_id = str(request.POST['patient_id'])
	appointment_id = str(request.POST['appointment_id'])

	name = str(request.POST['name'])

	diagnosis = str(request.POST['diagnosis'])
	symptom = str(request.POST['symptom'])

	age = str(request.POST['age'])
	height = str(request.POST['height'])
	weight = str(request.POST['weight'])
	surgeries = str(request.POST['surgeries'])
	diseases = str(request.POST['diseases'])
	family_diseases = str(request.POST['family_diseases'])
	medication = str(request.POST['medication'])
	allergies = str(request.POST['allergies'])
	sexual_diseases = str(request.POST['sexual_diseases'])
	gender = str(request.POST['gender'])
	
	
	sql="UPDATE auth_user set first_name=%s where id=%s;"
	cursor.execute(sql,[name, patient_id])


	sql="UPDATE appointments set diagnosis=%s, symptoms=%s where id_appointment=%s;"
	cursor.execute(sql,[diagnosis, symptom, appointment_id])


	sql="UPDATE hci set age=%s, height=%s, weight=%s, surgery=%s, current_illness=%s, family_diseases=%s, medication=%s, allergies=%s, sexual_history=%s, gender=%s where id_user=%s;"
	cursor.execute(sql,[age, height, weight, surgeries, diseases, family_diseases, medication, allergies, sexual_diseases, gender, patient_id])


	dbConnect.commit()
	cursor.close()

	return HttpResponse("")




@login_required
def ajax_bookLab(request):

	patient_id = str(request.POST['patient_id'])
	lab_id = str(request.POST['lab_id'])
	exam_req = str(request.POST['exam_req'])
	date_lab = str(request.POST['date_lab'])

	
	cursor=dbConnect.cursor()
	sql="INSERT into exams (id_user, id_lab_user, start_time, end_time, requirements) values (%s, %s, %s, %s, %s)"
	cursor.execute(sql,[patient_id, lab_id, date_lab, date_lab, exam_req])
	dbConnect.commit()
	cursor.close()

	return HttpResponse("")



### WATSON RELATED VIEWS ###

@login_required
def ajax_endAppointment(request):

	diagnosis = str(request.POST['diagnosis'])
	symptoms = str(request.POST['symptoms'])
	appointment_id = str(request.POST['appointment_id'])
	
	
	cursor=dbConnect.cursor()
	sql="UPDATE appointments set diagnosis=%s,symptoms=%s where id_appointment=%s;"
	cursor.execute(sql,[diagnosis, symptoms, appointment_id])
	dbConnect.commit()
	cursor.close()

	trainWatson(symptoms, diagnosis)

	return HttpResponse("")




@login_required
def ajax_askWatson(request):

	symptoms = str(request.POST['symptoms'])

	watsonDiagnosis = askWatsonDiagnosis(symptoms)
	
	data = {}

	data['illness1'] = watsonDiagnosis[0][0]
	data['percentage1'] = str(watsonDiagnosis[0][1])+" %"

	data['illness2'] = watsonDiagnosis[1][0]
	data['percentage2'] = str(watsonDiagnosis[1][1])+" %"

	data['illness3'] = watsonDiagnosis[2][0]
	data['percentage3'] = str(watsonDiagnosis[2][1])+" %"

	data['illness4'] = watsonDiagnosis[3][0]
	data['percentage4'] = str(watsonDiagnosis[3][1])+" %"

	data['illness5'] = watsonDiagnosis[4][0]
	data['percentage5'] = str(watsonDiagnosis[4][1])+" %"

	return HttpResponse(json.dumps(data))




@login_required
def ajax_watsonDiseaseData(request):

	illness = str(request.POST['illnessName'])

	data = {}
	data['diseaseData'] = askIllnessDefinition(illness)
	
	return HttpResponse(json.dumps(data))





### WATSON FUNCTIONS ###


def trainWatson(symptoms, diagnosis):

	pass

def askIllnessDefinition(diseaseName):

	return "Disease definition for "+diseaseName

def askWatsonDiagnosis(symptoms):


	return [['Illness 1', 100],['Illness 2', 90.3],['Illness 3', 56.5],['Illness 4', 10.4],['Illness 5', 5.1]] #From largest to smallest probability



