# coding=utf-8

from django.template import *
from django.http import *
from django.core.context_processors import *
from django.shortcuts import render_to_response
from django.core.cache import *
from neuoj.contest.models import *
from neuoj.oj.models import *
import time

def getheader(request,con):
	context={}
	if con.isPublic!=2:
		if 'login' in request.session:
			context['login']=request.session['login']
			u=ContestUser.objects.filter(contest=con,username=request.session['login'].username)
			if len(u)==0:
				uu=ContestUser(contest=con,username=request.session['login'].username,password=request.session['login'].password)
				uu.save()
				context['contestlogin']=uu
			else:
				context['contestlogin']=u[0]
		if con.isPublic==1:
			if 'passedcontest' not in request.session or con.id not in request.session['passedcontest']:
				context['needpassword']=True
	else:
		if 'contestlogin' in request.session and request.session['contestlogin'].contest==con:
			context['contestlogin']=request.session['contestlogin']	
	context['time']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	return context

def contestlogin(request,num):
	num=int(num)
	c=Contest.objects.filter(id=num)
	if len(c)==0:
		raise Http404
	c=c[0]
	if request.method!='POST':
		raise Http404
	if 'username' in request.POST and 'password' in request.POST:
		u=ContestUser.objects.filter(username=request.POST['username'],contest=c)
		if len(u)==0:
			return HttpResponse('username/password error')
		u=u[0]
		if u.password!=request.POST['password']:
			return HttpResponse('username/password error')
		request.session['contestlogin']=u
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	raise Http404
	
def passwd(request,num):
	num=int(num)
	c=Contest.objects.filter(id=num)
	if len(c)==0:
		raise Http404
	c=c[0]
	if request.method!='POST':
		raise Http404
	if 'password' in request.POST and request.POST['password']==c.password:
		if 'passedcontest' in request.session:
			request.session['passedcontest'].append(c.id)
		else:
			request.session['passedcontest']=[c.id]
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	return HttpResponse('password error')

def home(request,num):
	num=int(num)
	c=Contest.objects.filter(id=num)
	if len(c)==0:
		raise Http404
	c=c[0]
	context=getheader(request,c)
	cp=ContestProblem.objects.filter(contest=c)	
	return render_to_response('conhome.html',dict(context,**{'contest':c,'problems':cp}))

