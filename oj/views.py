# coding=utf-8
from django.template import *
from django.http import *
from django.core.context_processors import *
from django.shortcuts import render_to_response
from django.core.cache import *
from neuoj.oj.models import *
from neuoj.contest.models import *
from datetime import *

def getheader(request):
	notice=Notice(text='通知测试')
	notice.save()
	context={'notice':notice}
	if 'login' in request.session:
		context['login']=request.session['login']
	context['time']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	return context

def index(request):	
	news=News.objects.order_by('-time')
	u=User.objects.all()
	if len(u)==0:
		u=User(username='admin',password='19910521',nickname='god',email='s',isManager=True,isBoy=True,website='',school='NEU',AC=0,submit=0)
		u.save()
	context=getheader(request)
	l=len(news)
	if l>5:
		news=news[0:4]
	return render_to_response('ojindex.html',dict(context,**{'news':news}))		

def problems(request):
	return HttpResponseRedirect('/problems/1/')

def problemlist(request,vol):
	context=getheader(request)
	#p=Problem(title='测试',text='ads',samplein='所撕碎',sampleout='asd',timelimit=1000,memorylimit=64)
	#p.save()
	vol=int(vol)
	probs=Problem.objects.order_by('id')
	if (vol-1)*100+1>len(probs):
		return render_to_response('ojproblems.html',dict(context,**{'error':True}))
	return render_to_response('ojproblems.html',dict(context,**{'problems':probs[(vol-1)*100:vol*100-1]}))


def problem(request,num):
	context=getheader(request)
	num=int(num)
	p=Problem.objects.filter(id=num)
	if len(p)==0:
		raise Http404
	p=p[0]
	if p.visible:
		return render_to_response('ojproblem.html',dict(context,**{'num':num,'problem':p}))	
	else:
		raise Http404

def status(request):
	context=getheader(request)
	s=Submition.objects.order_by('-create')
	p=1
	if 'user' in request.GET and request.GET['user']!='':
		s=s.filter(user=request.GET['user'])
	if 'problem' in request.GET and request.GET['problem']!='':
		s=s.filter(problem=int(request.GET['problem']))
	if 'result' in request.GET and request.GET['result']!='':
		s=s.filter(result=request.GET['result'])
	if 'runid' in request.GET and request.GET['runid']!='':
		s=s.filter(id=int(request.GET['runid']))
	if 'lang' in request.GET and request.GET['lang']!='':
		s=s.filter(lang=request.GET['lang'])
	if 'page' in request.GET and request.GET['page']!='':
		p=int(request.GET['page'])
		if p<2:
			p=1
	s=s[(p-1)*20:p*20]
	#s=s[0:1]
	path=request.get_full_path()
	i=path.find('page')
	if i>=0:
		path=path[0:i-1]
	if path.find('?')<0:
		path+='?'
	ne=path+'&page='+str(p+1)
	pre=path+'&page='+str(p-1)
	return render_to_response('ojstatus.html',dict(context,**{'status':s,'next':ne,'pre':pre}))
	
def submit(request,problem):
	context=getheader(request)
	if not 'login' in request.session:
		error="please login first"
		return render_to_response('ojsubmit.html',dict(context,**{'error':error}))
	p=int(problem)
	p=Problem.objects.filter(id=p)
	if len(p)==0:
		raise Http404
	if p[0].visible==False:
		raise Http404
	if request.method=='POST':
		if not 'login' in request.session:
			error="please login first"
			return render_to_response('ojsubmit.html',dict(context,**{'error':error}))
		s=Submition(user=request.session['login'],problem=p[0],source=request.POST['source'],lang=request.POST['lang'],sourcelong=len(request.POST['source']))
		s.save()
		p.update(submit=p[0].submit+1)
		u=User.objects.filter(username=request.session['login'].username)
		u.update(submit=u[0].submit+1)
		request.session['login']=u[0]

		rrr=run(s.source,s.lang,p[0].samplein,
				p[0].sampleout,p[0].timelimit,p[0].memorylimit)
		rr,rrrr=rrr
		
		return HttpResponseRedirect('/status/')
	return render_to_response('ojsubmit.html',context)

def upload(request,num):
	context=getheader(request)
	if not 'login' in request.session:
		error="please login first"
		return render_to_response('oj.html',dict(context,**{'error':error}))
	p=int(num)
	p=Problem.objects.filter(id=p)
	if len(p)==0:
		raise Http404
	if p[0].visible==False:
		raise Http404
	if request.method=='POST':
		if not 'login' in request.session:
			error="please login first"
			return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
		if not 'file' in request.FILES:
			error="error filename"
			return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
		fd=request.FILES['file']
		if fd.name.find('.cpp')>=0:
			la='G++'
		elif fd.name.find('.c')>=0:
			la='GCC'
		elif fd.name.find('.java')>=0:
			la='JAVA'
		else:
			error="error filename"
			return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

		sour=fd.read()
		s=Submition(user=request.session['login'],problem=p[0],source=sour,lang=la,sourcelong=len(sour))
		s.save()
		p.update(submit=p[0].submit+1)
		u=User.objects.filter(username=request.session['login'].username)
		u.update(submit=u[0].submit+1)
		request.session['login']=u[0]
		return HttpResponseRedirect('/status/')
	return render_to_response('ojsubmit.html',context)

def source(request,num):
	context=getheader(request)
	sid=int(num)
	s=Submition.objects.filter(id=sid)
	if not 'login' in request.session:
		error="please login first"
		return render_to_response('ojsource.html',dict(context,**{'error':error}))
	if len(s)==0 or s[0].user.username!=request.session['login'].username:
		error="you are not the owner"
		return render_to_response('ojsource.html',dict(context,**{'error':error}))
	s=s[0]
	return render_to_response('ojsource.html',dict(context,**{'submit':s}))
	

def bbs(request,num):
	context=getheader(request)
	pid=int(num)
	p=Problem.objects.filter(id=pid)
	if len(p)==0:
		raise Http404
	if p[0].visible==False:
		raise Http404
	p=p[0]
	if request.method=='POST':
		if not 'login' in request.session:
			error="please login first"
			return render_to_response('ojbbs.html',dict(context,**{'error':error}))
		if not 'text' in request.POST:
			raise Http404
		post=BBS(problem=p,user=request.session['login'],text=request.POST['text'])
		post.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	posts=BBS.objects.filter(problem=pid).order_by('-id')
	l=[]
	for post in posts:
		re=Reply.objects.filter(bbs=post.id).order_by('id')
		l.append((post,re))
	return render_to_response('ojbbs.html',dict(context,**{'postsandreply':l}))

def reply(request,bid):
	if request.method!='POST':
		raise Http404
	if not 'login' in request.session:
		raise Http404
	b=BBS.objects.filter(id=bid)
	if len(b)==0:
		raise Http404
	r=Reply(bbs=b[0],user=request.session['login'],text=request.POST['text'])
	r.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def posts(request):
	context=getheader(request)
	if request.method=='POST':
		if not 'login' in request.session:
			error="please login first"
			return render_to_response('ojbbs.html',dict(context,**{'error':error}))
		if not 'text' in request.POST:
			raise Http404
		post=BBS(user=request.session['login'],text=request.POST['text'])
		post.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	posts=BBS.objects.order_by('-id')
	l=[]
	for post in posts:
		re=Reply.objects.filter(bbs=post.id).order_by('id')
		l.append((post,re))
	return render_to_response('ojbbs.html',dict(context,**{'postsandreply':l}))

	
def login(request):
	if request.method!='POST':
		raise Http404
	if 'username' in request.POST and 'password' in request.POST:
		u=User.objects.filter(username=request.POST['username'])
		if len(u)==0:
			return HttpResponse('username/password error')
		u=u[0]
		if u.password!=request.POST['password']:
			return HttpResponse('username/password error')
		request.session['login']=u
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	raise Http404

def logout(request):
	if 'login' in request.session:
		del request.session['login']
	return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def rank(request):
	context=getheader(request)
	r=1
	if 'rankstart' in request.GET and request.GET['rankstart']!='':
		r=int(request.GET['rankstart'])
	u=User.objects.order_by('-AC','submit')
	u=u[r-1:r+49]
	out=[]
	for user in u:
		ratio=0
		if user.submit>0:
			ratio=float(user.AC)/user.submit;
		out.append([r,user.username,user.nickname,user.school,user.AC,user.submit,ratio])
		r+=1
	n=len(out)+r
	return render_to_response('ojrank.html',dict(context,**{'users':out,'next':n}))

def contest(request):
	context=getheader(request)
	c=Contest.objects.order_by('-start','-end')

	return render_to_response('ojcontests.html',dict(context,**{'contests':c}))
