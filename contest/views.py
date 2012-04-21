# coding=utf-8
#
# Author: Philo Yang "yangzhe1991"
#

from django.template import *
from django.http import *
from django.core.context_processors import *
from django.shortcuts import render_to_response
from django.core.cache import *
from django.db.models import F
from neuoj.contest.models import *
from neuoj.oj.models import *
import time,datetime,memcache
from operator import itemgetter, attrgetter

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

		ds=Data.objects.filter(problem=p.probid)
		datas=[]
		for d in ds:
			datas.append((d.din,d.dout))
		put=(s.id,True,s.source,s.lang,datas,p.probid.timelimit,p.probid.memorylimit)
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
		
		ds=Data.objects.filter(problem=p.probid)
		datas=[]
		for d in ds:
			datas.append((d.din,d.dout))
		put=(s.id,True,s.source,s.lang,datas,p.probid.timelimit,p.probid.memorylimit)
		mc=memcache.Client(['127.0.0.1:11211'])
		if mc.get('pendings')==None:
			mc.set('pendings',[put])
		else:
			temp=mc.get('pendings')
			temp.append(put)
			mc.set('pendings',temp)

		return HttpResponseRedirect('/contest/%d/status/'%cid)
	return render_to_response('consubmit.html',context)

def status(request,cid):
	mc=memcache.Client(['127.0.0.1:11211'])
	if mc.get('results')!=None and len(mc.get('results'))>0:
		ss=mc.get('results')
		mc.delete('results')
		for s in ss:
			if s[0]:
				submit=ContestSubmition.objects.get(id=s[1])
			else:
				submit=Submition.objects.get(id=s[1])
			submit.result=s[2][0]
			if submit.result=='CE':
				submit.detail=s[2][1]
				submit.time=submit.memory=0
			else:
				submit.time=s[2][1]
				submit.memory=s[2][2]
			if submit.result=='AC':
				if not s[0] and	len(Submition.objects.filter(user=submit.user,problem=submit.problem,result='AC'))==0:
					#raise Http404
					submit.user.AC+=1
					submit.user.save()
				submit.problem.AC+=1
			elif submit.result=='WA':
				submit.problem.WA+=1
			elif submit.result=='TLE':
				submit.problem.TLE+=1
			elif submit.result=='MLE':
				submit.problem.MLE+=1
			elif submit.result=='RE':
				submit.problem.RE+=1
			elif submit.result=='CE':
				submit.problem.CE+=1
			elif submit.result=='PE':
				submit.problem.PE+=1
			submit.problem.save()
			submit.save()

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
	cus=ContestUser.objects.filter(contest=c)
	users={}	
	cps=ContestProblem.objects.filter(contest=c).order_by('id')
	csss=ContestSubmition.objects.all()
	l=[]
	pdict={}
	ps=[]
	for i,p in enumerate(cps):
		l.append({'problem':0,'result':''})
		pdict[p]=i
		ps.append(chr(i+ord('A')))

	for cu in cus:
		users[cu]=[0,0,l]#(prob,time)
		css=csss.filter(user=cu).order_by('id')
		for cs in css:
			if cs.result=='Pending':
				continue
			p=cs.problem
			if users[cs.user][2][pdict[p]]['result']=='AC':
				continue
			if cs.result=='AC':
				users[cs.user][2][pdict[p]]['result']='AC'
				users[cs.user][1]+=(cs.create-cs.user.contest.start).seconds/60-users[cs.user][2][pdict[p]]['problem']*20
				users[cs.user][2][pdict[p]]['problem']=(cs.create-cs.user.contest.start).seconds/60
				users[cs.user][0]+=1
			else:
				users[cs.user][2][pdict[p]]['result']=cs.result
				users[cs.user][2][pdict[p]]['problem']-=1

	us=sorted(users.items(),key=itemgetter(1))
	us=sorted(us,key=itemgetter(0),reverse=True)
	return render_to_response('conrank.html',{'contest':c,'users':us,'problems':ps})



def source(request,cid,sid):
	cid=int(cid)
	c=Contest.objects.get(id=cid)
	context=getheader(request,c)
	sid=int(sid)
	s=ContestSubmition.objects.filter(id=sid)
	if not 'contestlogin' in context:
		error="please login first"
		return HttpResponse(error)
	if len(s)==0 or s[0].user.username!=context['contestlogin'].username:
		error="you are not the owner"
		return HttpResponse(error)
	s=s[0]
	return render_to_response('viewcode.html',dict(context,**{'submit':s}))

def background(request,cid):
	cid=int(cid)
	c=Contest.objects.get(id=cid)
	
		

	
