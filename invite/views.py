
from django.shortcuts import render, HttpResponse
from dash.models import Event, UserEvent, User
from django.http import HttpResponseRedirect


def mergeTunnel(request):

    #print('throug tunnel')

    if User.objects.filter(userEmail=request.COOKIES.get('email'))[0].scVarChar != request.COOKIES.get('userCode'):
        return HttpResponse('[ERROR]')

    user = User.objects.get(userEmail=request.COOKIES.get('email'))
    invited_event = Event.objects.filter(shareKey=request.COOKIES.get('shareCodeNew'))
    if len(invited_event) != 1:
        return HttpResponse('[ERROR] False link')
    invited_event = invited_event[0]

    UserEvent.objects.create(
		eventKey=invited_event,
		userKey=user,
	)

    response = HttpResponseRedirect('/')
    response.set_cookie('shareCodeNew', '')
    return response


def reroute(request, share):

    """
    http://localhost:8000/invite/link/5lXY20ICKMYCugEMNjZjIozpy0uYuwZVF7WmkVUvaZuhgu3Xajh40aCX77uo
    """

    response = HttpResponseRedirect('/sign/up')

    """
    what does it do?

        sets cookies

        (would you send it to someone with a profile? no...)

        user is new
            creates a login
            creates a connecter model

        reroutes to dash
    """

    response.set_cookie('rerouting', 'invite')
    response.set_cookie('shareCodeNew', share)

    return response
