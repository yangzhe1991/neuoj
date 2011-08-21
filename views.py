# coding=utf-8
from django.template import *
from django.http import *
from django.core.context_processors import *
from django.shortcuts import render_to_response
from django.core.cache import *
from neuoj.oj.models import *
from neuoj.contest.models import *

import time,memcache

def admin(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	
	return render_to_response('adminbase.html')
	
def addproblem(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	
	if request.method!='POST':
		return render_to_response('addproblem.html')
	if 'title' in request.POST:
		t1=request.POST['title']
	else:
		raise Http404
	if 'text' in request.POST:
		t2=request.POST['text']
	else:
		raise Http404
	if 'samplein' in request.POST:
		t3=request.POST['samplein']
	else:
		raise Http404
	if 'sampleout' in request.POST:
		t4=request.POST['sampleout']
	else:
		raise Http404
	if 'hint' in request.POST:
		t5=request.POST['hint']
	else:
		t5=None
	if 'source' in request.POST:
		t6=request.POST['source']
	else:
		t6=None
	if 'time' in request.POST:
		t7=request.POST['time']
	else:
		raise Http404
	if 'memory' in request.POST:
		t8=request.POST['memory']
	else:
		raise Http404
	if 'input' in request.POST:
		t9=request.POST['input']
	else:
		raise Http404
	if 'output' in request.POST:
		t10=request.POST['output']
	else:
		raise Http404

	p=Problem(title=t1,text=t2,samplein=t3,sampleout=t4,hint=t5,source=t6,timelimit=int(t7),memorylimit=int(t8),indescribe=t9,outdescribe=t10)
	if len(Problem.objects.all())==0:
		p.id=1000
	p.save()
	return HttpResponseRedirect('/admin/problems/')
	
	
def problems(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	
	p=Problem.objects.order_by('-id')
	return render_to_response('adminproblems.html',{'problems':p})

def editproblem(request,num):
	num=int(num)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	p=Problem.objects.filter(id=num)
	if len(p)==0:
		raise Http404
	if request.method=='GET':
		if 'visible' in request.GET:
			if request.GET['visible']=='true':
				p.update(visible=True)
			else:
				p.update(visible=False)
			return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
		return render_to_response('admineditproblem.html',{'problem':p[0]})
	if 'title' in request.POST:
		t1=request.POST['title']
	else:
		raise Http404
	if 'text' in request.POST:
		t2=request.POST['text']
	else:
		raise Http404
	if 'samplein' in request.POST:
		t3=request.POST['samplein']
	else:
		raise Http404
	if 'sampleout' in request.POST:
		t4=request.POST['sampleout']
	else:
		raise Http404
	if 'hint' in request.POST:
		t5=request.POST['hint']
	else:
		t5=None
	if 'source' in request.POST:
		t6=request.POST['source']
	else:
		t6=None
	if 'time' in request.POST:
		t7=request.POST['time']
	else:
		raise Http404
	if 'memory' in request.POST:
		t8=request.POST['memory']
	else:
		raise Http404
	if 'input' in request.POST:
		t9=request.POST['input']
	else:
		raise Http404
	if 'output' in request.POST:
		t10=request.POST['output']
	else:
		raise Http404
	p.update(title=t1,text=t2,samplein=t3,sampleout=t4,hint=t5,source=t6,timelimit=int(t7),memorylimit=int(t8),indescribe=t9,outdescribe=t10)
	return HttpResponseRedirect('/admin/problems/')

def problem(request,num):
	num=int(num)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	p=Problem.objects.filter(id=num)
	if len(p)==0:
		raise Http404
	p=p[0]
	return render_to_response('adminproblem.html',{'num':num,'problem':p})	

def datas(request,pid):
	pid=int(pid)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	p=Problem.objects.filter(id=pid)
	if len(p)==0:
		raise Http404
	p=p[0]
	d=Data.objects.filter(problem=p)
	return render_to_response('admindatas.html',{'datas':d,'problem':p})	

def data(request,did):
	did=int(did)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	d=Data.objects.filter(id=did)
	if len(d)==0:
		raise Http404
	d=d[0]
	return render_to_response('admindata.html',{'data':d})	

def editdata(request,did):
	did=int(did)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	d=Data.objects.filter(id=did)
	if len(d)==0:
		raise Http404
	if request.method!='POST' or 'din' not in request.POST or 'dout' not in request.POST:
		return render_to_response('admineditdata.html',{'data':d[0]})	
	d.update(din=request.POST['din'],dout=request.POST['dout'])
	return HttpResponseRedirect('/admin/problem/'+str(d[0].problem.id)+'/data')

def adddata(request,pid):
	pid=int(pid)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	p=Problem.objects.filter(id=pid)
	if len(p)==0:
		raise Http404
	p=p[0]
	if request.method!='POST' or 'din' not in request.POST or 'dout' not in request.POST:
		return render_to_response('adddata.html')	
	d=Data(problem=p,din=request.POST['din'],dout=request.POST['dout'])
	d.save()
	return HttpResponseRedirect('/admin/problem/'+str(pid)+'/data')

def deletedata(request,did):
	did=int(did)
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	d=Data.objects.filter(id=did)
	if len(d)==0:
		raise Http404
	pid=d[0].problem.id
	d.delete()
	return HttpResponseRedirect('/admin/problem/'+str(pid)+'/data')

def contests(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	c=Contest.objects.order_by('-start','-end')
	return render_to_response('admincontests.html',{'contests':c})

def addcontest(request):
	if not 'login' in request.session:
		raise Http404
	if request.method!='POST':
		t=time.localtime()
		return	render_to_response('addcontest.html',{'year':t[0],'mon':t[1],'day':t[2],'hour':t[3],'min':t[4]})
	if 'title' in request.POST:
		tt=request.POST['title']
	else:
		raise Http404
	if 'year' in request.POST:
		y=int(request.POST['year'])
	else:
		raise Http404
	if 'day' in request.POST:
		d=int(request.POST['day'])
	else:
		raise Http404
	if 'month' in request.POST:
		m=int(request.POST['month'])
	else:
		raise Http404
	if 'hour' in request.POST:
		h=int(request.POST['hour'])
	else:
		raise Http404
	if 'minutes' in request.POST:
		mi=int(request.POST['minutes'])
	else:
		raise Http404
	if 'duringhour' in request.POST:
		dh=int(request.POST['duringhour'])
	else:
		raise Http404
	if 'duringminutes' in request.POST:
		dm=int(request.POST['duringminutes'])
	else:
		raise Http404
	if 'type' in request.POST:
		t=int(request.POST['type'])
	else:
		raise Http404
	if 'password' in request.POST:
		p=request.POST['password']
	else:
		raise Http404
	dd=datetime.timedelta(hours=dh,minutes=dm)
	start=datetime.datetime(y,m,d,h,mi)
	end=start+dd
	admin=request.session['login']
	c=Contest(title=tt,admin=admin,start=start,end=end,isPublic=t,password=p)
	c.save()
	if admin.isManager:
		return HttpResponseRedirect('/admin/contest/'+str(c.id))
	else:
		return HttpResponseRedirect('/contest/'+str(c.id))

def editcontest(request,num):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	cid=int(num)
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	if request.method!='POST':
		c=c[0]
		t=c.end-c.start
		return render_to_response('admineditcontest.html',{'contest':c,'hour':t.seconds/3600,'min':t.seconds%3600/60})

	if 'title' in request.POST:
		tt=request.POST['title']
	else:
		raise Http404
	if 'year' in request.POST:
		y=int(request.POST['year'])
	else:
		raise Http404
	if 'day' in request.POST:
		d=int(request.POST['day'])
	else:
		raise Http404
	if 'month' in request.POST:
		m=int(request.POST['month'])
	else:
		raise Http404
	if 'hour' in request.POST:
		h=int(request.POST['hour'])
	else:
		raise Http404
	if 'minutes' in request.POST:
		mi=int(request.POST['minutes'])
	else:
		raise Http404
	if 'duringhour' in request.POST:
		dh=int(request.POST['duringhour'])
	else:
		raise Http404
	if 'duringminutes' in request.POST:
		dm=int(request.POST['duringminutes'])
	else:
		raise Http404
	if 'type' in request.POST:
		t=int(request.POST['type'])
	else:
		raise Http404
	if 'password' in request.POST:
		p=request.POST['password']
	else:
		raise Http404
	dd=datetime.timedelta(hours=dh,minutes=dm)
	start=datetime.datetime(y,m,d,h,mi)
	end=start+dd
	admin=request.session['login']
	c.update(title=tt,admin=admin,start=start,end=end,isPublic=t,password=p)
	if admin.isManager:
		return HttpResponseRedirect('/admin/contest/'+str(c[0].id))
	else:
		return HttpResponseRedirect('/contest/'+str(c[0].id))

def contest(request,cid):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	cid=int(cid)
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	c=c[0]
	cp=ContestProblem.objects.filter(contest=c)
	return render_to_response('admincontest.html',{'contest':c,'problems':cp})

def addcontestproblem(request,cid):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	cid=int(cid)
	c=Contest.objects.filter(id=cid)
	if len(c)==0:
		raise Http404
	c=c[0]
	if request.method!='POST':
		return render_to_response('addcontestproblem.html')
	if 'pid' not in request.POST:
		raise Http404
	pid=int(request.POST['pid'])
	p=Problem.objects.filter(id=pid)
	if len(p)==0:
		raise Http404
	p=p[0]
	cp=ContestProblem(contest=c,probid=p)
	cp.save()
	return HttpResponseRedirect('/admin/contest/%d/'% cid)



def submitions(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	return render_to_response('adminsubmitions.html')

def rejudge(request):
	if not 'login' in request.session:
		raise Http404
	if not request.session['login'].isManager:
		raise Http404
	if 'pid' in request.GET and request.GET['pid']!='':
		pid=int(request.GET['pid'])
		p=Problem.objects.filter(id=pid)
		if len(p)==0:
			raise Http404
		p=p[0]
		cp=ContestProblem.objects.filter(probid=p)
		s2=[]
		if len(cp)>0:
			for cpp in cp:
				s2+=ContestSubmition.objects.filter(problem=cpp)
		s1=Submition.objects.filter(problem=p)
	elif 'runid' in request.GET and request.GET['runid']!='':
		runid=int(request.GET['runid'])
		s=Submition.objects.filter(id=runid)
		if len(s)==0:
			raise Http404
		p=s[0].problem
		s1=s
		s2=[]
	elif 'crunid' in request.GET and request.GET['crunid']!='':
		id=int(request.GET['crunid'])
		cs=ContestSubmition.objects.filter(id=id)
		if len(cs)==0:
			raise Http404
		p=cs[0].problem.probid
		s1=[]
		s2=cs
	else:
		raise Http404

	ds=Data.objects.filter(problem=p)
	datas=[]
	for d in ds:
		datas.append((d.din,d.dout))
	for s in s1:
		put=(s.id,False,s.source,s.lang,datas,p.timelimit,p.memorylimit)
		mc=memcache.Client(['127.0.0.1:11211'])
		if mc.get('pendings')==None:
			mc.set('pendings',[put])
		else:
			temp=mc.get('pendings')
			temp.append(put)
			mc.set('pendings',temp)
	for s in s2:
		put=(s.id,True,s.source,s.lang,datas,p.timelimit,p.memorylimit)
		mc=memcache.Client(['127.0.0.1:11211'])
		if mc.get('pendings')==None:
			mc.set('pendings',[put])
		else:
			temp=mc.get('pendings')
			temp.append(put)
			mc.set('pendings',temp)

	return HttpResponseRedirect('/admin/')
