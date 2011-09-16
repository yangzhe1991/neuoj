from django.db import models

class User(models.Model):
	username=models.CharField(max_length=50,primary_key=True)
	password=models.CharField(max_length=100)
	nickname=models.CharField(max_length=50,null=True,blank=True)
	email=models.EmailField(null=True,blank=True)
	isManager=models.BooleanField(default=False)
	birthday=models.DateField(blank=True,null=True)
	isBoy=models.NullBooleanField()
	website=models.URLField(blank=True,null=True)
	school=models.CharField(max_length=20,null=True,blank=True)
	create=models.DateTimeField(auto_now_add=True)
	AC=models.IntegerField(default=0)
	submit=models.IntegerField(default=0)

class Problem(models.Model):
	title=models.CharField(max_length=40)
	text=models.TextField()
	indescribe=models.TextField()
	outdescribe=models.TextField()
	samplein=models.TextField()
	sampleout=models.TextField()
	source=models.TextField(null=True,blank=True)
	hint=models.TextField(null=True,blank=True)
	create=models.DateTimeField(auto_now_add=True)
	iswater=models.BooleanField(default=False)
	timelimit=models.IntegerField()
	memorylimit=models.IntegerField()
	AC=models.IntegerField(default=0)
	CE=models.IntegerField(default=0)
	WA=models.IntegerField(default=0)
	PE=models.IntegerField(default=0)
	RE=models.IntegerField(default=0)
	TLE=models.IntegerField(default=0)
	MLE=models.IntegerField(default=0)
	submit=models.IntegerField(default=0)
	visible=models.BooleanField(default=False)

class Data(models.Model):
	problem=models.ForeignKey('Problem')
	din=models.TextField()
	dout=models.TextField()

class Submition(models.Model):
	user=models.ForeignKey('User')
	problem=models.ForeignKey('Problem')
	source=models.TextField()
	result=models.TextField(default='Pending')
	time=models.IntegerField(null=True)
	memory=models.IntegerField(null=True)
	create=models.DateTimeField(auto_now_add=True)
	lang=models.CharField(max_length=10)
	detail=models.TextField(null=True,blank=True)
	sourcelong=models.IntegerField()

class BBS(models.Model):
	problem=models.ForeignKey('Problem',null=True)
	user=models.ForeignKey('User')
	time=models.DateTimeField(auto_now_add=True)
	text=models.TextField()

class Reply(models.Model):
	bbs=models.ForeignKey('BBS')
	user=models.ForeignKey('User')
	time=models.DateTimeField(auto_now_add=True)
	text=models.TextField()

class Logininfo(models.Model):
	username=models.CharField(max_length=50)
	password=models.CharField(max_length=50)
	ip=models.IPAddressField()
	time=models.DateTimeField(auto_now_add=True)

class News(models.Model):
	title=models.CharField(max_length=20)
	text=models.TextField()
	time=models.DateTimeField(auto_now_add=True)

class Notice(models.Model):
	text=models.CharField(max_length=50)
	time=models.DateTimeField(auto_now_add=True)
