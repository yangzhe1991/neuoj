from django.db import models
from neuoj.oj.models import *

class Contest(models.Model):
	title=models.CharField(max_length=50)
	admin=models.ForeignKey('oj.User')
	start=models.DateTimeField()
	end=models.DateTimeField()
	notice=models.TextField(null=True,blank=True)
	isPublic=models.IntegerField()#0 for public 1 for private 2 for password
	password=models.CharField(max_length=100,null=True,blank=True)

class ContestUser(models.Model):
	username=models.CharField(max_length=20)
	password=models.CharField(max_length=64)
	nickname=models.CharField(max_length=100,blank=True,null=True)
	contest=models.ForeignKey('Contest')
	string=models.CharField(max_length=200,null=True)

class ContestProblem(models.Model):
	contest=models.ForeignKey('Contest')
	probid=models.ForeignKey('oj.Problem')
	AC=models.IntegerField(default=0)
	CE=models.IntegerField(default=0)
	WA=models.IntegerField(default=0)
	PE=models.IntegerField(default=0)
	RE=models.IntegerField(default=0)
	TLE=models.IntegerField(default=0)
	MLE=models.IntegerField(default=0)
	submit=models.IntegerField(default=0)

class ContestSubmition(models.Model):
	user=models.ForeignKey('ContestUser')
	problem=models.ForeignKey('ContestProblem')
	source=models.TextField()
	result=models.TextField(default='Pending')
	time=models.IntegerField(null=True)
	memory=models.IntegerField(null=True)
	create=models.DateTimeField(auto_now_add=True)
	lang=models.CharField(max_length=10)
	detail=models.TextField(null=True,blank=True)
	sourcelong=models.IntegerField()

