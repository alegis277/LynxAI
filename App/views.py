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

from datetime import date, datetime

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
		return render(request, 'labs.html', {'name':request.user.first_name+" "+request.user.last_name, 'id_lab' : str(request.user.id)})



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

	return HttpResponse(json.dumps(data, default=json_serial))

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
	sql="SELECT id_user, start_time, id_appointment from appointments where id_doctor=%s"
	cursor.execute(sql,[doc_id])
	iduser_date = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in iduser_date:

		string_base = data_database

		iduser = string_base[0]
		date = string_base[1]
		idappointment = string_base[2]

		sql="SELECT first_name, last_name from auth_user where id=%s"
		cursor.execute(sql,[iduser])
		name = cursor.fetchall()
		patient_name = name[0][0] + " "+ name[0][1]


		dataToAppend = {'title': patient_name, 'start': date, 'end': date,'id':iduser, 'imageurl':"/static/profile/"+str(iduser)+".jpg", 'id_appointment':idappointment}
		data['source'].append(dataToAppend)

	dbConnect.commit()
	cursor.close()

	return HttpResponse(json.dumps(data, default=json_serial))


@login_required
def ajax_getPatientData(request):

	patient_id = str(request.POST['patient_id'])
	appointment_id = str(request.POST['appointment_id'])





	cursor=dbConnect.cursor()

	sql="SELECT first_name from auth_user where id=%s"
	cursor.execute(sql,[patient_id])
	name = cursor.fetchall()
	patient_name = name[0][0]


	sql="SELECT complaint, symptoms, diagnosis from appointments where id_appointment=%s"
	cursor.execute(sql,[appointment_id])
	complaint_symptoms_diagnosis = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in complaint_symptoms_diagnosis:

		string_base = data_database

		complaint = string_base[0]
		symptoms = string_base[1]
		diagnosis = string_base[2]


	sql="SELECT age, height, weight, surgery, current_illness, family_diseases, medication, allergies, sexual_history, gender from hci where id_user=%s"
	cursor.execute(sql,[patient_id])
	all_data_HCI = cursor.fetchall()

	data = {}
	data['source'] = []

	for data_database in all_data_HCI:

		string_base = data_database

		age = string_base[0]
		height = string_base[1]
		weight = string_base[2]
		surgeries = string_base[3]
		diseases = string_base[4]
		family_diseases = string_base[5]
		medication = string_base[6]
		allergies = string_base[7]
		sexual_diseases = string_base[8]
		gender = string_base[9]


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


	return HttpResponse(json.dumps(data, default=json_serial))




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
	cursor.execute(sql,(age, height, weight, surgeries, diseases, family_diseases, medication, allergies, sexual_diseases, gender, patient_id,))


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

	data['illness5'] = watsonDiagnosis[0][0]
	data['percentage5'] = "%.2f %%"%(watsonDiagnosis[0][1])

	data['illness4'] = watsonDiagnosis[1][0]
	data['percentage4'] = "%.2f %%"%(watsonDiagnosis[1][1])

	data['illness3'] = watsonDiagnosis[2][0]
	data['percentage3'] = "%.2f %%"%(watsonDiagnosis[2][1])

	data['illness2'] = watsonDiagnosis[3][0]
	data['percentage2'] = "%.2f %%"%(watsonDiagnosis[3][1])

	data['illness1'] = watsonDiagnosis[4][0]
	data['percentage1'] = "%.2f %%"%(watsonDiagnosis[4][1])

	return HttpResponse(json.dumps(data, default=json_serial))




@login_required
def ajax_watsonDiseaseData(request):

	illness = str(request.POST['illnessName'])

	data = {}
	data['diseaseData'] = askIllnessDefinition(illness)

	return HttpResponse(json.dumps(data, default=json_serial))

@login_required
def ajax_getCalendarLab(request):

	lab_id = str(request.user.id)



	cursor=dbConnect.cursor()
	sql="SELECT id_user, id_exam, start_time from exams where id_lab_user = %s"
	cursor.execute(sql,[lab_id])
	ids = cursor.fetchall()

	data = {}
	data['source'] = []

	for inf in ids:
		sql2 = "SELECT first_name, last_name from auth_user where id = %s"
		cursor.execute(sql2, [inf[0]])
		idu = cursor.fetchall()

		patient_name = idu[0][0] + " "+ idu[0][1]


		dataToAppend = {'title': patient_name, 'start': inf[2], 'end': inf[2],'id':inf[0], 'imageurl':"/static/profile/"+str(inf[0])+".jpg", 'id_exam':inf[1]}
		data['source'].append(dataToAppend)

	dbConnect.commit()
	cursor.close()

	return HttpResponse(json.dumps(data, default=json_serial))




### WATSON FUNCTIONS ###


def trainWatson(symptoms, diagnosis):

	pass

def askIllnessDefinition(diseaseName):

	cursor1=dbConnect.cursor()
	sql= "SELECT * from watson"

	cursor1.execute(sql)
	watson_symptoms = cursor1.fetchall()

	Diseases = []

	#in_sympotoms = ['"fatigue"','"tired"','"feeling unwell"','"mkadas"']
	in_sympotoms=PalabrasClave
	for row_s in PalabrasClave:
		for row in watson_symptoms:
			if row[1] == row_s:
				Diseases.append(row[2])

	num_of_diseases = []
	num_of_symptoms = []

	for row_s in Diseases:
		num = 0;
		for row in watson_symptoms:
			if row[2] == row_s:
				num += 1
		num_of_symptoms.append(num)
		num2 = 0;
		for row in Diseases:
			if row == row_s:
				num2 += 1
		num_of_diseases.append(num2)
	n = 0
	data_out = []
	for row_s in Diseases:

		x = True
		for i in range(n):
			if Diseases[n] == Diseases[i]:
				x = False

		if x == True:
			data_out.append([row_s,(num_of_diseases[n]/num_of_symptoms[n])*100])
		n += 1

	for i in data_out:
		for j in data_out:
			if j[1] > i[1]:
				max_percent = j[0]  # enfermedad con la mayor probabilidad

	Extra_symptoms2 = []
	#for z in data_out:
	for z in Real_Data_Out:
		Extra_symptoms = []
		for row in watson_symptoms:

			x = True
			for row_s in in_sympotoms:
				if row_s == row[1]:
					x = False
			if x == True and row[2] == z[0]:
				Extra_symptoms.append(row[1])
		Extra_symptoms2.append(Extra_symptoms)
	i=0
	while i<5:
		if Real_Data_Out[i][0]== diseaseName:
			#print (Real_Data_Out[i][0])
			#print (Extra_symptoms2[i])
			return ('Be cautious if the patient shows one of the following symptoms: <br> <br> <br>',Extra_symptoms2[i])
		i=i+1
	#print('Estar pendiente de:',Extra_symptoms2[0])
	#print('Estar pendiente de:',Extra_symptoms2[1])

	dbConnect.commit()
	cursor1.close()

def askWatsonDiagnosis(symptoms):

	global Real_Data_Out
	global PalabrasClave
	informacion=[]
	natural_language_understanding = NaturalLanguageUnderstandingV1(
		version='2018-11-16',
		iam_apikey='Pam5AQPn6A9Zd1R0h01vnbwPxvvNaThARMJozSGqGYxp',
		url='https://gateway.watsonplatform.net/natural-language-understanding/api')

	natural_language_understanding.set_detailed_response(True)
	#response = natural_language_understanding.analyze(
	#   text=Texto,
	#    features=Features(concepts=ConceptsOptions(limit=nume))).get_result()
	response = natural_language_understanding.analyze(
		text=symptoms,
		features=Features(keywords=KeywordsOptions(sentiment=True,emotion=True,limit=5))).get_result()
	#print(json.dumps(response,indent=2))
	#print(json.dumps(response['concepts'][4]['text']))
	i=0
	PalabrasClave=[]
	#PaginasInformacion=[]
	while i<5:
		PalabrasClave.append(json.dumps(response['keywords'][i]['text']))
	#    PaginasInformacion.append(json.dumps(response['concepts'][i]['dbpedia_resource']))
		i=i+1

	i=0
	while i<5:
		PalabrasClave[i]=PalabrasClave[i].replace('"','')
		i=i+1
	#print (PalabrasClave)

	cursor1=dbConnect.cursor()
	sql= "SELECT * from watson"

	cursor1.execute(sql)
	watson_symptoms = cursor1.fetchall()

	Diseases = []

	#in_sympotoms = ['"fatigue"','"tired"','"feeling unwell"','"mkadas"']

	for row_s in PalabrasClave:
		for row in watson_symptoms:
			if row[1] == row_s:
				Diseases.append(row[2])

	num_of_diseases = []
	num_of_symptoms = []

	for row_s in Diseases:
		num = 0;
		for row in watson_symptoms:
			if row[2] == row_s:
				num += 1
		num_of_symptoms.append(num)
		num2 = 0;
		for row in Diseases:
			if row == row_s:
				num2 += 1
		num_of_diseases.append(num2)
	n = 0
	data_out = []
	for row_s in Diseases:

		x = True
		for i in range(n):
			if Diseases[n] == Diseases[i]:
				x = False

		if x == True:
			data_out.append([row_s,(num_of_diseases[n]/num_of_symptoms[n])*100])
		n += 1

	for i in data_out:
		#print("la probabilidad de tener",i[0],"es de un",i[1],"%")
		informacion.append(i[0])
		informacion.append(i[1])

	for i in data_out:
		for j in data_out:
			if j[1] > i[1]:
				max_percent = j[0]  # enfermedad con la mayor probabilidad

	data = []
	for i in data_out:
		data.append(i[1])
	# print("la probabilidad de tener",i[0],"es de un",i[1],"%")
	organiced_data = sorted(data)

	Real_Data_Out = []  # dator ordenados de enfermedad y probabilidad
	for i in organiced_data:
		for j in data_out:
			if i == j[1]:
				Real_Data_Out.append(j)

	dbConnect.commit()
	cursor1.close()
	#print(Real_Data_Out)
	#print(PalabrasClave)
	return Real_Data_Out

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
