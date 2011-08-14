#!/usr/bin/python
import shlex,subprocess,os,time

def run(source,lang,indata,outdata,timelimit,memlimit):
	#print source
	os.chdir('/home/godfather/judge/')
	if lang=='JAVA':
		timelimit*=3
	cmd={}
	fname={}
	fname['GCC']='Main.c'
	fname['G++']='Main.cpp'
	fname['JAVA']='Main.java'
	f=file(fname[lang],'w')
	f.write(source)
	f.close()
	cmd['GCC']='gcc -o Main Main.c'
	cmd['G++']='g++ Main.cpp -o Main'
	cmd['JAVA']='javac Main.java'
	fd1=file('out.txt','w')
	fd2=file('err.txt','w')
	#print cmd[lang]
	p=subprocess.Popen(shlex.split(cmd[lang]),stdout=fd1,stderr=fd2)
	p.wait()
	fd1.close()
	fd2.close()
	if p.returncode!=0:
		e=file('err.txt','r')
		return ('CE',e.read())
	cmd['GCC']='./Main'
	cmd['G++']='./Main'
	cmd['JAVA']='java Main'
	returncode=0
	fd0=file('in.txt','w')
	fd0.write(indata)
	fd0.close()
	fd0=file('in.txt','r')
	fd1=file('out.txt','w')
	fd2=file('err.txt','w')
	start=time.time()
	p=subprocess.Popen(shlex.split(cmd[lang]),stdin=fd0,stdout=fd1,stderr=fd2)
	mm=0
	while True:
		s=file('/proc/'+str(p.pid)+'/status','r').read()
		if p.poll()!=None:
			fd0.close()
			fd1.close()
			fd2.close()
			fd1=file('out.txt','r')
			fd2=file('err.txt','r')
			if p.poll()!=0:
				return ('RE',fd2.read(),p.poll())
			out=fd1.read()
			if out==outdata:
				return ('AC',tt,mm)
			else:
				out=out.replace('\n','')
				outdata=outdata.replace('\n','')
				if out==outdata:
					return ('PE')
				return ('WA',outdata,out)
		tt=time.time()-start
		if tt>timelimit:
			#os.kill(p.pid,9)
			p.kill()
			return ('TLE',tt)
		#print s
		if s.find('RSS')<0:
			continue
		s=s[s.find('RSS')+6:]
		s=s[:s.find('kB')-1]
		mm=int(s)
		if mm>memlimit:
			#os.kill(pid,9)
			p.kill()
			return ('MLE',mm)


if __name__=='__main__':
	ff=file('source.c','r')
	s=ff.read()
	lang='GCC'
	timelimit=1.0
	memlimit=64000
	fin=file('input.txt','r')
	sin=fin.read()
	fout=file('output.txt','r')
	sout=fout.read()
	print run(s,lang,sin,sout,timelimit,memlimit)
