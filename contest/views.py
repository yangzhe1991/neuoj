# coding=utf-8

from django.template import *
from django.http import *
from django.core.context_processors import *
from django.shortcuts import render_to_response
from django.core.cache import *
from django.db.models import F
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
	context['contest']=con
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
	if 'contestlogin' not in context:
		return render_to_response('conhome.html')
	ps=[]
	submits=ContestSubmition.objects.filter(user=context['contestlogin'])
	for i,p in enumerate(cp):
		temp={}
		temp['title']=p.probid.title
		for s in submits.filter(problem=p):
			if s.result=='AC':
				temp['solved']=True
				break
		temp['AC']=p.AC
		temp['submit']=p.submit
		temp['num']=chr(ord('A')+i)	
		temp['id']=i+1
		ps.append(temp)
	return render_to_response('conhome.html',dict(context,**{'contest':c,'problems':ps}))

def problem(request,cid,pid):
	cid=int(cid)
	pid=ord(pid)-ord('A')
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	c=c[0]
	context=getheader(request,c)
	cp=ContestProblem.objects.filter(contest=c)	
	if 'contestlogin' not in context:
		return render_to_response('conhome.html')
	cp=ContestProblem.objects.filter(contest=c)
	if len(cp)<pid+1:
		raise Http404
	cp=cp[pid]
	return render_to_response('conproblem.html',dict(context,**{'problem':cp}))	


def submit(request,cid,pid):
	cid=int(cid)
	pid=ord(pid)-ord('A')
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	c=c[0]
	context=getheader(request,c)
	cp=ContestProblem.objects.filter(contest=c)	
	if 'contestlogin' not in context:
		return render_to_response('conhome.html')
	cp=ContestProblem.objects.filter(contest=c)
	if len(cp)<pid+1:
		raise Http404
	p=cp[pid]

	if request.method=='POST':
		p.submit=F('submit')+1
		p.save()
		s=ContestSubmition(user=context['contestlogin'],problem=p,source=request.POST['source'],lang=request.POST['lang'],sourcelong=len(request.POST['source']))
		s.save()

		ds=Data.objects.filter(problem=p[0])
		datas=[]
		for d in ds:
			datas.append((d.din,d.dout))
		put=(s.id,False,s.source,s.lang,datas,p[0].timelimit,p[0].memorylimit)
		mc=memcache.Client(['127.0.0.1:11211'])
		if mc.get('pendings')==None:
			mc.set('pendings',[put])
		else:
			temp=mc.get('pendings')
			temp.append(put)
			mc.set('pendings',temp)

		
		return HttpResponseRedirect('/contest/%d/status/'% cid)
	return render_to_response('consubmit.html',context)

def upload(request,cid,pid):
	cid=int(cid)
	pid=ord(pid)-ord('A')
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	c=c[0]
	context=getheader(request,c)
	cp=ContestProblem.objects.filter(contest=c)	
	if 'contestlogin' not in context:
		return render_to_response('conhome.html')
	cp=ContestProblem.objects.filter(contest=c)
	if len(cp)<pid+1:
		raise Http404
	p=cp[pid]

	if request.method=='POST':
		fd=request.FILES['file']
		if fd.name.find('.cpp')>=0:
			la='G++'
		elif fd.name.find('.c')>=0:
			la='GCC'
		elif fd.name.find('.java')>=0:
			la='JAVA'
		else:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
		p.submit=F('submit')+1
		p.save()
		sour=fd.read()
		s=ContestSubmition(user=context['contestlogin'],problem=p,source=sour,lang=la,sourcelong=len(sour))
		s.save()
		return HttpResponseRedirect('/contest/%d/status/'%cid)
	return render_to_response('consubmit.html',context)

def status(request,cid):
	cid=int(cid)
	c=Contest.objects.get(id=cid)
	context=getheader(request,c)
	if 'contestlogin' not in context:
		return render_to_response('conhome.html')
	s=ContestSubmition.objects.filter(user=context['contestlogin']).order_by('-id')
	return render_to_response('constatus.html',dict(context,**{'status':s}))

def rank(request,cid):
	cid=int(cid)
	c=Contest.objects.get(id=cid)
	cp=ContestProblem.objects.filter(contest=c)
	pid={}
	for i,p in enumerate(cp):
		pass
	cs=ContestSubmition.objects.filter(contest=c)	


