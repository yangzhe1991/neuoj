#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <time.h>
#include <stdarg.h>
#include <ctype.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/signal.h>
#include <sys/stat.h>
#include <unistd.h>

#include "okcalls.h"
#include <string>
#include <fstream>
#include <iostream>
using namespace std;

int timel;
int meml;
string lang;

int get_file_size(const char * filename) {
        struct stat f_stat;

        if (stat(filename, &f_stat) == -1) {
                return 0;
        }

        return (int) f_stat.st_size;
}

void init_para(char ** argv)
{
	timel=atoi(argv[1]);
	meml=atoi(argv[2]);
	lang=string(argv[3]);
}
bool compile()
{
	const char * CP_C[] = { "gcc", "Main.c", "-o", "Main", "-O2","-Wall", "-lm",
		"--static", "-std=c99", "-DONLINE_JUDGE", NULL };
	const char * CP_X[] = { "g++", "Main.cc", "-o", "Main", "-O2", "-Wall",
		"-lm", "--static", "-DONLINE_JUDGE", NULL };
	const char * CP_J[] = { "javac", "-J-Xms32m", "-J-Xmx256m", "Main.java",
		NULL };
    pid_t pid = fork();
	if(pid==0)
	{
	freopen("ce.txt", "w", stdout);
	if(lang=="GCC")execvp(CP_C[0], (char * const *) CP_C);
	else if(lang=="G++")execvp(CP_X[0], (char * const *) CP_X);
	else execvp(CP_J[0], (char * const *) CP_J);
	exit(0);
	}
	else
	{
		int status=0;
        waitpid(pid, &status, 0);
        status=get_file_size("ce.txt");
		return status;
	}
	
}

void run()
{
	pid_t pid=fork();	
	if(pid==0)//runner
	{
        freopen("data.in", "r", stdin);
        freopen("user.out", "w", stdout);
        freopen("error.out", "w", stderr);
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
		if(lang!="JAVA")
            execl("./Main", "./Main", NULL);
		else 
                execl("/usr/bin/java", "/usr/bin/java", java_p1, java_p2,
                                "-Djava.security.manager",
                                "-Djava.security.policy=./java.policy", "Main", NULL);

	exit(0);	
	}
	else//watcher
	{
        int status, sig, exitcode;
        struct user_regs_struct reg;
        struct rusage ruse;
		while(1)
		{
			
            wait4(pidApp, &status, 0, &ruse);
            if (WIFEXITED(status))
                break;
			if(get_file_size("error.out"))
			{
				ofstream fout("ans");
				fout<<"CE"<<endl;
				exit(0);
			}
            exitcode = WEXITSTATUS(status);
		}
	}

}

int main(int argc ,char ** argv)
{
	init_para(argv);
	if(!compile())//CE
	{
		ofstream fout("ans");
		freopen("ce.txt","r",stdin);
		string s;
		fout<<"CE"<<endl;
		while(getline(cin,s)>0)
		{
			fout<<s;
		}
		fout<<endl;
	}
	run();
	
	return 0;
}
