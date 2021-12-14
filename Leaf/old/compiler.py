"""

Spliting and grouping encode bytes:
	\x01 : seperate lines in "{" group;
	\x02 : conserve older split and let regex do some work over a join
		[regroup_line(ln) <- lf_parser.py]


"""

RECURSION_LIMIT = 4095




import argparse
from sys import exit
from sys import argv as sys__argv__
from copy import copy
import context
import lf_parser as lfp
import glb
import platform
import tempfile
from argparse import ArgumentParser

__code__ = ""

glb.rfile = "./ex/test.lf"


def beautify_c_output(s):
	r=""
	for i in s.split(";"):
		if not (i.replace(" ","").replace("\t","") in ("","\n")):
			r+=i+";"
	s=""
	for i in r.split("\n"):
		if len(i)==0:
			continue
		if i[0] == ";":
			s += i[1:]+"\n"
		else:
			s += i+"\n"
	return s

def readable_C(s):
	r=""
	tabs = 0
	spl = [""]
	for i in s:
		if i == ";":
			spl.append("")
		elif i in "{}":
			spl.append(i)
			spl.append("")
		else:
			spl[-1] += i
	for n,i in enumerate(spl):
		if i == "{":
			tabs += 1
			r+="\t"*tabs+i+'\n'
		elif i == "}":
			tabs -= 1
			r+="\t"*tabs+i+";\n"
		else:
			if n!=len(spl)-1 and spl[n+1] == "{":
				r+="\t"*tabs+i
			else:
				r+="\t"*tabs+i+";\n"
	return r


def main(argc : int, argv : ArgumentParser):
	global __code_dir__, __code_name__, __code_encoding__
	#if glb.rfile == None:
	#	print("Error ! : No input file or command.")
	#	exit(1)
	if glb.rfile:
		__code_dir__ = glb.os.path.dirname(glb.rfile)
		__code_name__ = glb.rfile.rsplit(".",1)[0]
	arch,os = platform.architecture()
	glb.buildActualConfiguration(name=argv.cf)
	lfp.names[glb.config["MAIN_NAME"]] = glb.config["C_MAIN_NAME"]
	with open(glb.rfile) as e:
		__code_encoding__ = e.encoding
		lfp.lf_compile_to_C(e)
	
						
if __name__ == "__main__":
	#glb.setrecursionlimit(RECURSION_LIMIT)

	# Setup argparse
	argp = argparse.ArgumentParser(
		description="Leaf compiler (using gcc)."
	)
	argp.add_argument("input_file",type=str, help="The input file to process.")
	argp.add_argument("-cf",type=str, nargs=1,help="The input file to process.")
	argp.add_argument("-toC", action="store_true",help="The input file to process.")
	argp.set_defaults(cf=("name","default"))
	# Build code
	argv = argp.parse_args(sys__argv__[1:])
	print(argv.__repr__())
	main(2,argv)

	# Write C output
	f = open(__code_dir__+"/"+glb.genName()+".c",'w', encoding=__code_encoding__)
	if argv.toC:
		f.write(readable_C(beautify_c_output(lfp.__code__)))
	else:
		f.write(beautify_c_output(lfp.__code__))
	file_path = f.name
	f.close()
	if not argv.toC:
		warp = glb.os.popen("gcc "+file_path+" -o "+__code_name__+glb.config["EXECUTABLE_EXTENSION"])
		print(warp.read())
		print(glb.os.listdir(__code_dir__))
		# glb.os.remove(file_path) # Keeping this to see the final code.