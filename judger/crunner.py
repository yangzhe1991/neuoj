#!/usr/bin/python
import shlex,subprocess,os,time
import memcache
import MySQLdb

global mc

def run(source,lang,indata,outdata,timelimit,memlimit):
	#print source
	os.setuid(1536)
	os.chdir('/home/judge/')
	if lang=='JAVA':
		timelimit*=3
	cmd={}
	fname={}
	fname['GCC']='Main.c'
	fname['G++']='Main.cpp'
	fname['JAVA']='Main.java'
	f=file('run/'+fname[lang],'w')
	f.write(source)
	f.close()
	fd2=file('run/data.in','w')
	fd2.write(indata)
	fd2.close()
	fd3=file('run/data.out','w')
	fd3.write(outdata)
	fd3.close()
	os.system('judger '+str(timelimit)+' '+str(memlimit)+' '+lang)
	ff=file('run/ans','r')
	res=ff.readlines()
	os.system('rm -rf run/*')
	return res
	





def submit(c,runid,result):
	if mc.get('results')!=None and len(mc.get('results'))>0:
		mcs=mc.get('results')
	else:
		mcs=[]
	mcs.append((c,runid,result))
	mc.set('results',mcs)


if __name__=='__main__':
	mc=memcache.Client(['127.0.0.1:11211'])
	while True:
		conn=MySQLdb.connect(host='localhost',user='root',passwd='yangzhe1991',db='neuoj')
		cursor=conn.cursor()

		if mc.get('pendings')!=None and len(mc.get('pendings'))>0:
			temp=mc.get('pendings')
			runid,c,source,lang,datas,timelimit,memlimit=temp.pop(0)
			mc.set('pendings',temp)
			print c,runid
			result=('AC',0,0)
			PE=False
			for data in datas:
				re=run(source,lang,data[0],data[1],timelimit,memlimit)
				if re[0]=='CE':
					result=('CE',re[1])
					break
				elif re[0]=='RE':
					result=re
					break
				elif re[0]=='WA':
					result=re
					break
				elif re[0]=='TLE':
					result=re
					break
				elif re[0]=='MLE':
					result=re
					break
				elif re[0]=='PE':
					PE=True
			print re
			if result[0]!='AC':
				submit(c,runid,result)
			elif PE:
				submit(c,runid,('PE',re[1],re[2]))
			else:
				submit(c,runid,re)
		conn.commit()
		cursor.close()
		conn.close()
