from django.db import models
from django.utils.crypto import get_random_string

# Brugere u/ log in information
class User(models.Model):
	scVarChar = models.CharField(max_length=60, default=get_random_string(60), unique=True)
	username = models.CharField(max_length=60, unique=True)
	userEmail = models.CharField(max_length=60, unique=True)
	password = models.CharField(max_length=120)

	def __str__(self):
		return self.username


# Arrangement
class Event(models.Model):
	place = models.CharField(max_length=160)
	nameOfEve = models.CharField(max_length=80)
	descOfEve = models.CharField(max_length=240)
	startDate = models.DateField()
	endDate = models.DateField()
	participants = models.ManyToManyField(User, through='UserEvent')

	def __str__(self):
		return self.nameOfEve


# ManyMany-Relation Table/Model
class UserEvent(models.Model):
	userKey = models.ForeignKey(User, on_delete=models.CASCADE)
	eventKey = models.ForeignKey(Event, on_delete=models.CASCADE)

