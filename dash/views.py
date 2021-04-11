
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, HttpResponse
import calendar
from datetime import datetime
from pytz import timezone
from .models import User, Event, UserEvent
from django.http import HttpResponseRedirect
#import requests


# NOT IN USE AT THE MOMENT... TERRIBLE API.
WHEATERKEY = '9e929957-5758-40c2-b007-365aef6fd0ac'
def getWheaterInformation ():

	#start_time = time.time()
	r = requests.get("https://dmigw.govcloud.dk/v2/metObs/collections/observation/items?limit=20&stationId=06074&api-key={}".format(WHEATERKEY))
	if r.status_code == 200:
		pack = r.json()['features']
		temp = pack[9]['properties']['parameterId']
	#print("--- {} seconds ---".format(time.time() - start_time))

def manageRequest(request):

	#check if sc is real
	if request.GET['type'] == 'in':
		userList = User.objects.filter(username=request.GET['username'])

		if len(userList) <= 0:
			#[ERROR] No user found
			return HttpResponseRedirect('/')
		else:
			user = userList[0]

		if check_password(request.GET['password'], user.password):
			response = HttpResponseRedirect('../dash')
			response.set_cookie('userCode', user.scVarChar, 60*60*4) #ca 4 timer
			response.set_cookie('username', user.username, 60*60*4)
			return response
		else:
			return HttpResponseRedirect('/')
			#return HttpResponse('[ERROR] 500 Something went wrong <a href="/">go back</a>')


	if request.GET['type'] == 'up':

		try:
			user = User.objects.create(
				username = request.GET['username'],
				userEmail=request.GET['email'],
				password = make_password(request.GET['password'], salt=None, hasher='default'),
			)
			return HttpResponseRedirect('../')
		except Exception as e:
			print(str(e))
			return HttpResponse('[ERROR] 500 Something went wrong <a href="/">go back</a>')


		#make_password(password, salt=None, hasher='default')

	if len(User.objects.filter(scVarChar=request.GET['hk'], username=request.GET['user'])) != 1:
		return HttpResponse('[ERROR] access denied')
	#else:

	if request.GET['type'] == 'create':
		return createEvent(request)

	elif request.GET['type'] == 'delete':
		return deleteEvent(request)

	elif request.GET['type'] == 'removeuser':
		return removeUser(request)

	return 'none'


def createEvent(request):

	"""
	need to know:
		start
		end
		desc
		place
		name
		with whom? (skal der være en confirm? neeeej, men de andre kan vælge at melde sig fra)
	"""
	user = User.objects.filter(scVarChar=request.GET['hk'])[0]

	start = list(request.GET['start'].split('-'))
	end = list(request.GET['end'].split('-'))
	start.reverse()
	end.reverse()
	name = request.GET['name']
	desc = request.GET['desc']
	place = request.GET['place']

	if len(name) == 0:
		name = 'Aftale af ' + user.username
	if len(desc) == 0:
		desc = 'En aftale';
	if len(place) == 0:
		place = 'Verden';

	event = Event.objects.create(
		place=place,
		nameOfEve=name,
		descOfEve=desc,
		startDate="-".join(start),
		endDate="-".join(end)
	)

	UserEvent.objects.create(
		eventKey=event,
		userKey=user
	)

	if len(request.GET['ptp']) > 0:
		ptp = request.GET['ptp'].split('-')
		for p in ptp:
			UserEvent.objects.create(
				eventKey=event,
				userKey=User.objects.filter(username=p)[0]
			)

	return HttpResponse('[SUCCESS]')


def deleteEvent(request):

	e = Event.objects.filter(id=request.GET['eveID'])
	if len(e) != 1:
		return HttpResponse('[ERROR] NO EVENT MATCHED')
	ue = UserEvent.objects.filter(eventKey=e[0], userKey=User.objects.get(username=request.GET['user']))
	if len(ue) <= 0:
		return HttpResponse('[ERROR] access denied for event')

	e.delete()
	return HttpResponse('[SUCCESS]')


def removeUser(request):

	e = Event.objects.filter(id=request.GET['eveID'])
	if len(e) != 1:
		return HttpResponse('[ERROR] NO EVENT MATCHED')
	ue = UserEvent.objects.filter(eventKey=e[0], userKey=User.objects.get(username=request.GET['user']))
	if len(ue) <= 0:
		return HttpResponse('[ERROR] access denied for event')

	ue.delete()
	return HttpResponse('[SUCCESS]')


def authenticateUser(request):
	try:
		if User.objects.filter(username=request.COOKIES.get('username'))[0].scVarChar == request.COOKIES.get('userCode'):
			return True
		return False
	except Exception as e:
		print(str(e))


def index(request):

	if not authenticateUser(request):
		return HttpResponseRedirect('/sign')

	#getWheaterInformation()

	# få kaldender
	cal = calendar.Calendar()
	fm = "%Y-%m-%d"
	utc = datetime.now(timezone('UTC'))
	local = utc.astimezone(timezone('Europe/Copenhagen'))
	dt = local.strftime(fm)
	dt = str(dt).split('-')

	l = []
	for day in cal.itermonthdays(int(dt[0]), int(dt[1])):
		l.append(day)
	lastDay = max(l)
	today = dt

	# pull data from db.
	user = User.objects.get(username=request.COOKIES.get('username'))
	events = Event.objects.filter(userevent__userKey=user.id)

	ptp = []
	for i in events:
		l = ''
		for j in UserEvent.objects.filter(eventKey=i.id).order_by('userKey__id'):
			if j.userKey.username != user.username:
				l += str(j.userKey.username) + '-'
		ptp.append(l)

	events = list(zip(events, ptp))

	otherusers = User.objects.exclude(id=user.id)

	context = {'hk':user.scVarChar, 'lastDay':range(1,lastDay+1), 'today':int(today[-1]), 'user':user.username, 'events':events, 'last':lastDay, 'friends':otherusers}
	return render(request, 'dash/index.html', context)


# NOTER
# "ikke disponipel"
# for andre kan man se at den person har en aftale
# lidt ligsom "in call" på teams så man kan se at den person ikke
# er der på det tidspunkt.
