from sys import exit,setrecursionlimit
import json
import os
from typing import Iterable
READING_NLINE = None
rfile = None
__dir__ = os.path.dirname(__file__)
def readline(n,__cdescr__):
	with open(rfile) as f:
		for i,l in enumerate(f):
			if i-1 == n:
				return l
	print("LineError")
	print("\tInfo:")
	print(f"\t Can't access line {n} because there isn't enough lines in {rfile}.")
	print("\tLooking for line:",n)
	print("DEBUG : ",__cdescr__)
	exit(1)

def find(ls,test_func):
	for i in ls:
		if test_func(i):
			return i
		elif type(i) in (tuple,list,set):
			r = find(i,test_func)
			if r!=None:
				return r

def lrfind(ls: list,test_func) -> int:
	for n,i in enumerate(ls[::-1]):
		if test_func(i):
			return len(ls)-n-1

def fstartwith(iterator,sub_iterator):
	l = len(sub_iterator)
	for n,i in enumerate(iterator):
		if i[:l] == sub_iterator:
			return n
	return False

## From stack exchange (by 301_Moved_Permanently)
A_UPPERCASE = ord('A')
ALPHABET_SIZE = 26
def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number - 1, ALPHABET_SIZE)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""

    return ''.join(
            chr(A_UPPERCASE + part)
            for part in _decompose(number)
    )[::-1]
## end

namegen_id = 1

def genName():
	global namegen_id
	r = "ox"+base_10_to_alphabet(namegen_id)
	namegen_id += 1
	return r

def ensureStringList(ls: list[str]) -> list[str]:
	r = [""]*len(ls)
	for i in range(len(ls)):
		if ls[i] in (""," "):
			continue
		if ls[i][-1] == " ":
			r[i] = ls[i][:-1]
		elif ls[i][0] == " ":
			r[i] = ls[i][1:]
		else:
			r[i] = ls[i]
	while "" in r:
		r.remove("")
	return r

def intelligent_join(_join: str, ls: Iterable[str]) -> str:
	indbq = False
	insgq = False
	r = ls[0]
	if ls[0][0] == '"':
		indbq = True
	elif ls[0][0] == "'":
		insgq = True
	for i in ls[1:]:
		if insgq:
			r += i
			if i[0] == "'":
				insgq = False
		elif indbq:
			r += i
			if i[0] == '"':
				indbq = False
		else:
			if i[0] == '"':
				indbq = True
			elif i[0] == "'":
				insgq = True
			r += _join + i
	return r

def RETdebug(descr,value,_sep=" "):
	print(descr,value)
	return str(descr) + _sep + str(value)

"""
Unreferenced objects naming (UON):
For example:
RTPL0 is the first return tuple
RTPL1 is the second return tuple

RTPL
	Return TuPLe.
	Type : FixTuple

UUFT
	Union Used For Template.
	Type : union

TOU
	Type Of Union.
	Type : {{x}}
	The syntax of this one is a bit weird:
	TOU{{x}}
	The compiler sticks the type to the UON.
	If {{x}} is a pointer, it adds _ptr at the end of the name
	For example:
	char* -> TOUchar_ptr




"""

def buildActualConfiguration(name):
	global config
	config = None

	def push_config(dico: dict):
		global config
		if config == None:
			config = dico
		else:
			for i in dico:
				config[i] = dico[i]

	for i in json.load(open("config.json")):
		if i["name"] == "default":
			if config == None:
				config = i["data"]
			else:
				for j in i["data"]:
					if not j in config.keys():
						config[j] = i["data"][j]
		elif i["name"] == name:
			config = i["data"]
	if config == None:
		print("ConfigError:")
		print("\tInfo:")
		print("\t\tNo default configuration !")
		print("\tHelp:")
		print("\t\tUse this command: leaf config reset")
		exit(1)



"""    OLD CONFIG PARSER

		if "arch" in params.keys():
			if i["arch"] == params["arch"]:
				if "os" in params.keys():
					if i["os"] == params["os"]:
						push_config(i["data"])
					elif i["os"] == "*" and config == None:
						push_config(i["data"])
				else:
					if i["os"] == "*":
						push_config(i["data"])
			elif i["arch"] == "*" and config == None:
				if "os" in params.keys():
					if i["os"] == params["os"]:
						push_config(i["data"])
					elif i["os"] == "*" and config == None:
						push_config(i["data"])
				else:
					if i["os"] == "*":
						push_config(i["data"])
		elif "os" in params.keys():
			if i["os"] == params["os"] and params["arch"] == "*":
				push_config(i["data"])
			elif i["os"] == "*" and config == None and params["arch"] == "*":
				push_config(i["data"])
		else:
			if i["arch"] == "*" and i["os"] == "*":
				push_config(i["data"])


"""