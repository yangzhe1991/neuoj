from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.cache import cache_page
import neuoj.oj.views
import neuoj.contest.views

urlpatterns = patterns('neuoj.oj.views',
		# Examples:
		url(r'^$', 'index'),
		url(r'^problems/$','problems'),
		url(r'^problems/(\d+)/$','problemlist'),
		url(r'^problem/(\d+)/$','problem'),
		url(r'^problem/(\d+)/submit/$','submit'),
		url(r'^problem/(\d+)/upload/$','upload'),
		url(r'^problem/(\d+)/bbs/$','bbs'),
		url(r'^viewcode/(\d+)/$','source'),
		url(r'^bbs/$','posts'),
		url(r'^bbs/(\d+)/$','post'),
		url(r'^bbs/(\d+)/reply$','reply'),
		url(r'^rank/$','rank'),
		url(r'^contest/$','contest'),
		url(r'^login/$','login'),
		url(r'^logout/$','logout'),
		url(r'^contest/(\d+)/.*login/$','login'),
		
		)

urlpatterns+=patterns('neuoj.contest.views',
		url(r'^contest/(\d+)/$','home'),
		url(r'^contest/(\d+)/([A-Z])/$','problem'),
		url(r'^contest/(\d+)/([A-Z])/submit/$','submit'),
		url(r'^contest/(\d+)/([A-Z])/upload/$','upload'),
		url(r'^contest/(\d+)/status/$','status'),
		url(r'^contest/(\d+)/.*passwd/$','passwd'),

		)

urlpatterns+=patterns('neuoj.views',
		url(r'^admin/$','admin'),
		url(r'^admin/problems/$','problems'),
		url(r'^admin/contest/$','contests'),
		url(r'^admin/contest/add$','addcontest'),
		url(r'^admin/contest/(\d+)/$','contest'),
		url(r'^admin/contest/(\d+)/edit/$','editcontest'),
		url(r'^admin/contest/(\d+)/addproblem/$','addcontestproblem'),
		url(r'^admin/datas/$','datas'),
		url(r'^admin/submitions/$','submitions'),
		url(r'^admin/addproblem/$','addproblem'),
		url(r'^admin/problem/(\d+)/edit/$','editproblem'),
		url(r'^admin/problem/(\d+)/$','problem'),
		url(r'^admin/problem/(\d+)/data/$','datas'),
		url(r'^admin/data/(\d+)/$','data'),
		url(r'^admin/data/(\d+)/edit/$','editdata'),
		url(r'^admin/data/(\d+)/edit/delete/$','deletedata'),
		url(r'^admin/problem/(\d+)/data/add/$','adddata'),

		)

#need cache
urlpatterns+=patterns('',
		url(r'^status/$',cache_page(1)(neuoj.oj.views.status)),
		url(r'^contest/(\d+)/ranklist/$',cache_page(5)(neuoj.contest.views.rank)),
		)
