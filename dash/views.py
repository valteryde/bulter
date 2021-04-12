
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, HttpResponse
import calendar
from datetime import datetime
from pytz import timezone
from .models import User, Event, UserEvent, get_random_string_60
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
#import requests

# using the Fernet module
from cryptography.fernet import Fernet

# getting key
key = Fernet.generate_key()
f = Fernet(key)
RULE = (2,get_random_string(2))


def v_encrypt(s):

	"""
	rules:
		the 2. 3. and 5. char is 5, q and t.
	"""

	msg = ''
	for i in range(len(s)):
		if i == 0:
			msg += s[i]
		else:
			if i % RULE[0] == 0:
				msg += RULE[1] + s[i]
			else:
				msg += s[i]

	msg += '('+str(len(s))+')'
	return f.encrypt(msg.encode()).decode()


def v_decrypt_n_verify(s):

	"""
	verify with rules from the encryption
	"""

	s = f.decrypt(s.encode()).decode()
	clear = True

	msg = ''
	offset = 0

	start = s.index('(')
	numb = int(s[start+1: s.index(')')])
	s = s[:start]

	try:
		for j in range(len(s)): # måske kan man gøre len(s), 1 for at starte der...

			if j > 0:

				i = j + offset

				if s[i] != '':

					if i % RULE[0] == 0:

						if s[i:i+len(RULE[1])] != RULE[1]:
							clear = False
						else:
							offset += len(RULE[1])
							msg += s[i+len(RULE[1])]
					else:
						msg += s[i]
			else:
				msg += s[0]

	except IndexError:
		pass

	if clear and numb == len(msg):
		return msg
	else:
		return False


def check_for_rerouting(request):

	if request.COOKIES.get('rerouting') != '':

		rerouting_type = request.COOKIES.get('rerouting')

		if rerouting_type == 'invite':
			response = HttpResponseRedirect('/invite/tunnel')
		else:
			response = HttpResponseRedirect('/')

		response.set_cookie('rerouting', '')
		return (True, response)
	else:
		return (False, None)


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

		userList = User.objects.filter(userEmail=request.GET['email'])

		if len(userList) != 1:
			#[ERROR] No user found
			return HttpResponseRedirect('/')
		else:
			user = userList[0]

		if check_password(request.GET['password'], user.password):
			response = HttpResponseRedirect('../dash')
			response.set_cookie('userCode', user.scVarChar, 60*60*4) #ca 4 timer
			response.set_cookie('email', user.userEmail, 60*60*4)
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
			resp = HttpResponseRedirect('/')
			resp.set_cookie('email', user.userEmail, 60*60*4)
			resp.set_cookie('userCode', user.scVarChar, 60*60*4)
			return resp
		except Exception as e:
			print(str(e))
			return HttpResponse('[ERROR] 500 Something went wrong <a href="/">go back</a>')

	if len(User.objects.filter(scVarChar=request.GET['hk'], userEmail=request.GET['email'])) != 1:
		return HttpResponse('[ERROR] access denied')
	#else:

	if request.GET['type'] == 'create':
		return createEvent(request)

	elif request.GET['type'] == 'delete':
		return deleteEvent(request)

	elif request.GET['type'] == 'removeuser':
		return removeUser(request)

	elif request.GET['type'] == 'share':
		return createShareLink()

	return HttpResponse('[ERROR] Request matched 0 types')


def createShareLink():

	shareKey = get_random_string_60()
	response = HttpResponse(shareKey)
	response.set_cookie('shareKey',v_encrypt(shareKey), 60*60*0.5)
	return response
	#return HttpResponse(v_encrypt(shareKey))


def createEvent(request):

	response = HttpResponse('[SUCCESS]')

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


	if request.COOKIES.get('shareKey') == '' or not request.COOKIES.get('shareKey'):

		event = Event.objects.create(
			place=place,
			nameOfEve=name,
			descOfEve=desc,
			startDate="-".join(start),
			endDate="-".join(end)
		)
	else:

		try: #this could be a VERY bad fix. But hey it works...
			shKey = v_decrypt_n_verify(request.COOKIES.get('shareKey'))

			if not shKey:
				return HttpResponse('[ERROR] Wrong share code')

			event = Event.objects.create(
				shareKey = shKey,
				place=place,
				nameOfEve=name,
				descOfEve=desc,
				startDate="-".join(start),
				endDate="-".join(end)
			)

		except Exception:

			event = Event.objects.create(
				place=place,
				nameOfEve=name,
				descOfEve=desc,
				startDate="-".join(start),
				endDate="-".join(end)
			)

		response.set_cookie('shareKey', '')

	UserEvent.objects.create(
		eventKey=event,
		userKey=user
	)

	if len(request.GET['ptp']) > 0:
		ptp = request.GET['ptp'].split('-')
		for p in ptp:
			UserEvent.objects.create(
				eventKey=event,
				userKey=User.objects.filter(userEmail=p)[0]
			)

	return response


def deleteEvent(request):

	e = Event.objects.filter(id=request.GET['eveID'])
	if len(e) != 1:
		return HttpResponse('[ERROR] NO EVENT MATCHED')
	ue = UserEvent.objects.filter(eventKey=e[0], userKey=User.objects.get(userEmail=request.GET['email']))
	if len(ue) <= 0:
		return HttpResponse('[ERROR] access denied for event')

	e.delete()
	return HttpResponse('[SUCCESS]')


def removeUser(request):

	e = Event.objects.filter(id=request.GET['eveID'])
	if len(e) != 1:
		return HttpResponse('[ERROR] NO EVENT MATCHED')
	ue = UserEvent.objects.filter(eventKey=e[0], userKey=User.objects.get(userEmail=request.GET['email']))
	if len(ue) <= 0:
		return HttpResponse('[ERROR] access denied for event')

	ue.delete()
	return HttpResponse('[SUCCESS]')


def authenticateUser(request):
	try:
		if User.objects.filter(userEmail=request.COOKIES.get('email'))[0].scVarChar == request.COOKIES.get('userCode'):
			return True
		return False
	except Exception as e:
		print(str(e))


def index(request):

	r = check_for_rerouting(request)
	if r[0]:
		return r[1]

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
	user = User.objects.get(userEmail=request.COOKIES.get('email'))
	events = Event.objects.filter(userevent__userKey=user.id)

	ptp = []
	for i in events:
		l = ''
		for j in UserEvent.objects.filter(eventKey=i.id).order_by('userKey__id'):
			if j.userKey.userEmail != user.userEmail:
				l += str(j.userKey.username) + '-'
		ptp.append(l)

	print(l)
	events = list(zip(events, ptp))

	otherusers = User.objects.exclude(id=user.id)

	context = {'hk':user.scVarChar, 'lastDay':range(1,lastDay+1), 'today':int(today[-1]), 'user':user.username, 'events':events, 'last':lastDay, 'friends':otherusers, 'email':user.userEmail, 'usershort':user.username.split(' ')[0]}
	return render(request, 'dash/index.html', context)


# NOTER
# "ikke disponipel"
# for andre kan man se at den person har en aftale
# lidt ligsom "in call" på teams så man kan se at den person ikke
# er der på det tidspunkt.
