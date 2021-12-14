from copy import error
from enum import IntEnum
from io import BufferedIOBase
from typing import Iterable, Union
import context
import re
from sys import exit
import string
import os
import classprops as classfix_consts
import psutil
process = psutil.Process(os.getpid())
def getRAMsize():
	return process.memory_info().rss

import ALUexpr
from errors import *

__code__ = ""
__code__included = [] # Just a parse, not real C code.
__dir__ = os.path.dirname(__file__)
print(__dir__)

COMPILE_INCLUDE_AND_KEEP_CODE = "py compiler.py {header} --temp {tempid} -o {tempname}{tempid}"
FIXED_FUNCTION = 0b10_10_10_10
NUL_STR = ""
def TNUL(s):
	return s if s!=None else NUL_STR
def TUNKNOWN(s):
	return s if s!=None else "<unknown>"

class LineJump:pass


_popposits = {"(":")","[":"]","{":"}"}
def split_line(s: str) -> list[object]:
	r=[""]
	insgq = False
	indbq = False
	parenth = ""
	backslash = 0
	linejump_holder = 0 # For line breaks in parenthesis
	step_left = -1
	comment_block = 0
	last = ""
	for i in s:
		if step_left > 0:
			step_left-=1
		elif step_left==0:
			quit(0)
		if i == "\t":
			last = "\t"
			continue
		if i == "\\" and (indbq or insgq):
			backslash = True
		if comment_block:
			if i == "*" and last == "/":
				comment_block += 1
			elif i == "/" and last == "*":
				comment_block -= 1
			elif i == "\n":
				r.append(LineJump)
		elif insgq:
			r[-1]+=i
			if i == "'" and not backslash:
				insgq = False
			if backslash:
				backslash = False
		elif indbq:
			r[-1]+=i
			if i == '"' and not backslash:
				indbq = False
			if backslash:
				backslash = False
		elif len(parenth)>0:
			if i in "\n;" and parenth[-1]=="{":
				r[-1]+="\x01"
				linejump_holder+=1
			elif i!="\n":
				r[-1]+=i
			if i == _popposits[parenth[-1]]:
				parenth = parenth[:-1]
				if len(parenth) == 0:
					r.extend([LineJump]*linejump_holder)
					linejump_holder = 0
			elif i in _popposits.values():
				glb.READING_LINE = r[-1]
				glb.READING_NLINE = r.count(LineJump)
				traceback("SyntaxError","Wrong closing braket !",__cdescr__="split_line")
			elif i in "([{":
				parenth += i
			elif i == "'":
				insgq = True
			elif i == '"':
				indbq = True
		elif i == "\n":
			r.append(LineJump)
			r.append("")
		elif i == ";":
			r.append("")
		elif i == "'":
			insgq = True
			r[-1] += i#r.append(i)
		elif i == '"':
			indbq = True
			r[-1] += i#r.append(i)
		elif i == "*" and last == "/":
			r[-1] = r[-1][:-1]
			comment_block += 1
		elif i in "([{":
			parenth+=i
			r[-1]+=i
		else:
			r[-1]+=i
		last = i
	return r


def split(l: str, __cdescr__="<invalid call description>") -> list[str]:
	#print(__cdescr__ + f"split({l=}): ")
	if l == "":
		return []
	# if l in "}{":
	# 	return [l]
	l = re.sub(r"^\s+","",l)
	# non-regex split (to avoid in-parentheses spliting)
	r=[""]
	insgq = False
	indbq = False
	parenth = ""
	backslash = False
	for i in l:
		if i == "\\" and (indbq or insgq):
			backslash = True
			r[-1]+=i
			continue
		if insgq:
			r[-1]+=i
			if i == "'" and not backslash:
				insgq = False
			if backslash:
				backslash = False
		elif indbq:
			r[-1]+=i
			if i == '"' and not backslash:
				indbq = False
			if backslash:
				backslash = False
		elif len(parenth)>0:
			r[-1]+=i
			if i == _popposits[parenth[-1]]:
				parenth = parenth[:-1]
				if len(parenth)==0:
					r.append("")
			elif i in "([{":
				parenth += i
			elif i == "'":
				insgq = True
			elif i == '"':
				indbq = True
		elif i == "'":
			insgq = True
			r.append("'")
		elif i == '"':
			indbq = True
			r.append('"')
		elif i in "([{":
			parenth+=i
			r.append(i)
		else:
			if re.search(r"\b.$",r[-1]+i):
				if (len(r[-1]) < 2 or r[-1][-1] in " ") and i == " ":
					continue
				r.append(i)
			elif i == ",":
				r.append(i)
				r.append("")
			else:
				r[-1]+=i
	return glb.ensureStringList(regroup_line(glb.ensureStringList(r)))

def regroup_text(txt):
	# REGROUP : CURLY BRACKETS [v]
	r = []
	for i in txt:
		if i == LineJump:
			r.append(i)
		elif i == "":
			continue
		elif i[0] == "{":
			r[-1]+=i
		else:
			r.append(i)
	return r

_template_pattern = r"[a-zA-Z_0-9]+\x02\<\x02[a-zA-Z_0-9,]+\x02\>"
def regroup_line(ln,__cdescr__="<incorrect call description>"):
	# REGROUP : TYPE TEMPLATES [x]
	# REGROUP : TYPE POINTER
	# REGROUP : TYPE/VARIABLE AND ARRAY/SCLICE [x]
	# REGROUP : AFTER = [x]
	# REGROUP : OPERATIONS [x]
	r = []
	buff = "\x02".join(ln)
	result = re.findall(_template_pattern,buff)
	if len(result) > 0:
		ln = []
		for i in result:
			matched = re.search(_template_pattern,buff)
			ln.extend(buff[:matched.pos].split("\x02"))
			ln.append(i.replace("\x02",""))
			buff = buff[matched.end():]
		ln.extend(buff.split("\x02"))
	last = None
	stick_to_last_one = False
	close_parenth = False
	for n,i in enumerate(ln):
		if len(r) > 0:
			stack_last_type = context.getTypeByName(r[-1])
		else:
			stack_last_type = None
		if i.replace(" ","")=="=":
			r.append("=")
			r.append("("+" ".join(ln[n+1:])+")")
			return r
		elif i == ",":
			if close_parenth:
				idx = glb.lrfind(r,lambda x: x==',')
				r = r[:idx+1]+[glb.intelligent_join(" ",r[idx+1:])+")"]
				r.append(",")
				r.append("(")
			else:
				r = ["("+glb.intelligent_join(" ",r)+")"]
				r.append(",")
				r.append("(")
				close_parenth = True
		elif last in glb.config["keywords"] and (i in glb.config["keywords"] or context.getAnyByName(i)):
			r[-1] += " "+i
		elif i == "*":
			if stack_last_type and i == "*":
				r[-1]+=i
			elif len(r) > 0 and r[-1][-1] == "*":
				r[-1]+=i
			elif n == 0:
				stick_to_last_one = True
				r.append(i)
			elif stick_to_last_one:
				r[-1]+=i
			else:
				r.append(i)
		elif stick_to_last_one:
			r[-1]+=i
			stick_to_last_one = False
		else:
			r.append(i)
		last = i
	if close_parenth:
		idx = glb.lrfind(r,lambda x: x == ',')
		r = r[:idx+1]+[glb.intelligent_join(" ",r[idx+1:])+")"]
	while "" in r:
		r.remove("")
	return r


class symbol:
	def __init__(self,symbol,syntaxes):
		self.symbol = symbol
		self.syntaxes = syntaxes


"""

		THIS IS FUCKED UP !!!
		USE SLY FOR THAT PLS !
		THERE STILL A LOT OF WORK TO DO !

"""
known_symbols = (
	symbol("=",["{left}%s{right}"]),
	symbol("+",["{left}%s{right}","%s{right}"]),
	symbol("-",["{left}%s{right}","%s{right}"]),
	symbol("*",["{left}%s{right}","%s{right}","{left}%s"]),
	symbol("/",["{left}%s{right}"]),
	symbol("%",["{left}%s{right}"]),
	symbol("&",["{left}%s{right}","{left}%s"]),
	symbol("|",["{left}%s{right}"]),
	symbol(">>",["{left}%s{right}"]),
	symbol("<<",["{left}%s{right}"]),
	symbol("~",["%s{right}"]),
	symbol("**",["{left}%s{right}","%s{left}","{left}%s"]),
	symbol("^",["{left}%s{right}"]),
	symbol("==",["{left}%s{right}"]),
	symbol(">",["{left}%s{right}","{left}%s"]),
	symbol("<",["{left}%s{right}","%s{right}"]),
	symbol(">=",["{left}%s{right}"]),
	symbol("<=",["{left}%s{right}"]),
	symbol("!=",["{left}%s{right}"]),
	symbol("~=",["{left}%s{right}"])
)
single_symbols = "=+-*/%&|><!^~"
def verifySymbolsShapeSyntax(ln: list[str]) -> None:
	for n,i in enumerate(ln):
		if i[0] in single_symbols:
			for j in known_symbols:
				if i==j.symbol:
					for sntx in j.syntaxes:
						if n==0 and "{left}" not in sntx and "{right}" in sntx:
							return
						elif n==(len(ln)-1) and "{right}" not in sntx and "{left}" in sntx:
							return
						elif 0<n<(len(ln)-1):
							return
					else:
						traceback("SyntaxError",f"Invalid symbol syntax for \"{j.symbol}\".",syntax="\n\t".join(j.syntaxes))
			else:
				traceback("SyntaxError", f"Unknown symbol {i}.")
	return


class PreProc:
	def __init__(self,command,data):
		self.command = command.lower()
		self.data = data
	def __repr__(self):
		return f"<PreProc {self.command=} {self.data=}>"

class ReturnStatement:
	def __init__(self,value):
		self.value = value
	def __repr__(self):
		return f"<return {self.value}>"

class BreakStatement:
	def __repr__(self):
		return "<BREAK>"
class ContinueStatement:
	def __repr__(self):
		return "<CONTINUE>"
class DeleteStatement:
	def __init__(self,ls):
		self.deletes = ls
	def __repr__(self):
		return f"<DeleteStatement {self.deletes}>"

class DefArgument:
	def __init__(self,type,name,octx,default_value=None):
		self.type = type
		self.name = name
		self.default_value = default_value
		self.octx = octx
	def getCSyntax(self) -> context.CSyntaxOutcome:
		if self.default_value:
			return context.CSyntaxOutcome(f"{self.type.getCSyntax().raw} {self.name} = {self.default_value.getCSyntax().raw}")
		else:
			return context.CSyntaxOutcome(f"{self.type.getCSyntax().raw} {self.name}")
	def __repr__(self):
		return f"<DefArgument {self.type=} {self.name=}>"

class CallArgument:
	def __init__(self,value,octx,name=None):
		self.name = name
		self.value = value
		self.octx = octx
	def __repr__(self):
		return f"<CallArgument {self.name=} {self.value=}>"

class StaticCall:
	# Call when the returned value isn't used
	def __init__(self,func: context.Func, arguments: list[CallArgument]):
		self.func = func
		self.arguments = arguments
	def __repr__(self):
		return f"<StaticCall {self.func}{self.arguments}>"

class DataCall:
	# Call when the returned value is used
	def __init__(self,func: context.Func, arguments: list[CallArgument]):
		self.func = func
		self.arguments = arguments
	def __repr__(self):
		return f"<DataCall {self.func}{self.arguments}>"

class valueGetter:
	def __init__(self,getfrom):
		self.getfrom = getfrom
	def __repr__(self):
		return f"(GET* {self.getfrom})"

class adressGetter:
	def __init__(self,getfrom):
		self.getfrom = getfrom
	def __repr__(self):
		return f"(GET& {self.getfrom})"

DECL_UNKNOWN = 0
DECL_VAR_NO_DEFAULT = 1
DECL_VAR_DEFAULT_VAL = 2
DECL_VAR_DEFAULT_INIT = 3
DECL_FUNC = 4

class Declaration:
	def __init__(self,_type,name,init=None,value=None,keywords=None,decl_type=0,octx=None):
		# Function : init value
		# Variable "int x" : 
		# Variable "int x=y": value
		# Variable "Object x(y)": init
		self.init = init
		if octx == None:
			traceback(
				"InternalError",
				f"No given \"object from context\"(octx): Declaration({_type=},{name=},{init=},{value=},{keywords=},{decl_type=},{octx=})"
			)
		self.octx = octx
		if type(_type) == str:
			self.type = context.getTypeByName(_type)
		else:
			self.type = _type
		self.name = name
		self.value = value
		if keywords == None:
			keywords = []
		self.keywords = keywords
		if decl_type == DECL_UNKNOWN:
			if init == None and value == None:
				self.decl_type = DECL_VAR_NO_DEFAULT
			elif value == None:
				self.decl_type = DECL_VAR_DEFAULT_INIT
			elif init == None:
				self.decl_type = DECL_VAR_DEFAULT_VAL
			else:
				self.decl_type = DECL_FUNC
		else:
			self.decl_type = decl_type

	def __repr__(self):
		return f"<Declaration:{self.decl_type} {self.keywords} {self.type} {self.name}{TNUL(self.init)} := {TUNKNOWN(self.value)}>"

class ExternalC:
	def __init__(self,compact_code: str) -> None:
		self.code = compact_code[1:-1].replace("\x01","\n")
	def __repr__(self) -> str:
		return "<Extern C>"

class ExternalASM:
	def __init__(self, compact_code: str) -> None:
		self.code = compact_code[1:-1].replace("\x01","\\n")
	def __repr__(self) -> str:
		return "<Extern ASM>"
	def getCExpression(self) -> str:
		buf = "".join(f'"{i}"\n' for i in self.code.splitlines())
		return f"asm({buf})"


class Template:
	def __init__(self,name,linked_to=None):
		self.name = name
		self.linked_to = linked_to
		self.ctx_thing = None# context.getAnyByName(self.linked_to.name)
	def __repr__(self):
		return f"<Template {self.name} linked_to:{self.linked_to.name}>"
	def bakeContextName(self):
		return self.linked_to.name+":"+self.name

class Operation:
	def __init__(self,left,operand,right=None):
		# If self.right is None, the operation is a single-handed operation
		self.left = left
		self.operand = operand
		self.right = right
	def getCSyntax(self) -> context.CSyntaxOutcome:
		return context.CSyntaxOutcome(self.__repr__)
	def __repr__(self):
		return f"({self.left}){self.operand}({TNUL(self.right)})"

class New:
	def __init__(self,type):
		self.type = type
	def getCSyntax(self) -> context.CSyntaxOutcome:
		return f"({self.type.getCSyntax().raw}*)malloc({context.getTypeSize(self.type)})"
	def __repr__(self):
		return f"(NEW {self.type})"

def lastIndex(ls,value):
	return len(ls) - 1 - ls[::-1].index(value)

def purgeList(ls):
	while "" in ls:
		ls.remove("")
	return len(ls)>0

def makeDefArguments(string:str,ctx_input:Union[context.ctx, None]=None):
	s = split(string[1:-1],f"makeDefArgument({string=},{ctx_input=}): ")
	r = []
	i = 0
	buf = []
	def repart():
		nonlocal buf
		if len(buf) == 0:
			traceback(
				"SyntaxError",
				"Argument declaration doesn't start with \",\".",
				"([keywords] <type> <name> [= default value], ...)",
				f"makeDefArguments({string=},{ctx_input=})"
			)
		decl = _recognizeDeclaration(buf,tuple(context.getTypeByName(i) for i in buf), "MakeDef: ")
		if not decl:
			print("WTF")
			print(buf)
			traceback("WTF Error","wtf","wtf","wtf")
		r.append(DefArgument(decl.type, decl.name, context.CTX[-1], decl.value))
		buf = []
	for i in s:
		if i==",":
			repart()
		else:
			if i == "":
				continue
			buf.append(i)
	if len(buf) > 0:
		repart()
	return r

def makeCallArguments(string, octx):
	spl = split(string[1:-1],f"makeCallArgument({string=},{octx=}): ")
	r = []
	i = 0
	for i in spl:
		if i == ",":
			continue
		b = split(i,f"makeCallArgument({string=},{octx=}): L0[{spl} => {i}]: ")
		r.append(CallArgument(parse(b,2,__cdescr__=f"makeCallArgument({string}): "),octx=octx))
	return r
		

def _recognizeDeclaration(ln: list,is_type: Union[tuple, list], __cdescr__="No call description :"):
	# !!!
	#  DON'T FORGET TO A ADD FUNCTION THAT TRANSLATE ARGUMENT STRING INTO ARGUMENT LIST
	#  AND DON'T FORGET TO RE-PARSE VALUE 
	# !!!
	if len(ln) == 1 and ln[0][0] == "(":
		spl = split(ln[0][1:-1],__cdescr__ + f"_recognizeDeclaration({ln=}, {is_type=}): ")
		return _recognizeDeclaration(spl, tuple(context.getTypeByName(i) for i in spl), __cdescr__)
	
	if len(ln) > 2 and any(i for i in is_type) and any(("(" in i and ")" in i) or "=" in i for i in ln):
		#idx = None
		char = ""
		for n,i in enumerate(ln[::-1]):
			if i[0] == "=":
				char = i[0]
				#idx = len(ln)-1-n
				break
		else:
			for n,i in enumerate(ln[::-1]):
				if i[0] == "(":
					char = i[0]
					#idx = len(ln)-1-n
					break
			else:
				# variable delcaration without value
				_type = context.getTypeByName(ln[-2])
				context.CTX << context.Var(_type, ln[-1], context.CTX.getProcessedOBJ())
				return Declaration(ln[-2],ln[-1],None,None,ln[:-2] if len(ln[:-2]) > 0 else None,DECL_VAR_NO_DEFAULT, context.CTX[-1])
		if char=="=":
			# Variable decl
			context.CTX << context.Var(is_type[-4], ln[-3], context.CTX.getProcessedOBJ())
			spl = split(ln[-1][1:-1], __cdescr__ + f"_recognizeDeclaration({ln=}, {is_type=}): VAR_DECL({char=}): ")
			return Declaration(is_type[-4],ln[-3],None,parse(spl, 2, __cdescr__=__cdescr__+f"_recoDecl({ln=},{is_type=})"),ln[:-4] if len(ln[:-4]) > 0 else None, octx=context.CTX[-1])
		elif char=="(":
			if ln[-1][0] == "{":
				# Function decl
				_type = context.getTypeByName(ln[-4])
				context.CTX << context.Func(_type,ln[-3],None,context.CTX.getProcessedOBJ())
				decl = Declaration(_type, ln[-3], None, None, ln[:-4], DECL_FUNC, context.CTX[-1])
				context.CTX = context.CTX[-1].ctx
				decl.init = makeDefArguments(ln[-2],context.CTX)
				decl.value = parsesParenth(ln[-1],static=1, __cdescr__= __cdescr__ + f"_recognizeDeclaration({ln=}, {is_type=}): FUNC_DECL: ")
				
				context.CTX = context.CTX.getParentCTX()

				ls = []
				for i in decl.init:
					ls.append(i.type)
				context.CTX[-1].atypes=ls

				return decl
			# Variable decl (the initializer type)
			return Declaration(ln[-3],ln[-2],ln[-1],None,ln[:-3] if len(ln[:-3]) > 0 else None)
	elif len(ln)==2 and issubclass(type(is_type[0]),context.BaseClass):
		context.CTX << context.Var(is_type[0], ln[1], context.CTX.getProcessedOBJ())
		return Declaration(is_type[0], ln[1], keywords=is_type[0].getKeyWords(), octx=context.CTX[-1])
	else:
		return None
def parsesParenth(parenth,static=0,__cdescr__="<invalide call description>"):
	value = []
	for i in parenth[1:-1].split("\x01"):
		buf = split(i, __cdescr__ + f"parsesParenth({parenth=},{static=}): ")
		if buf == ['']  or len(buf)==0:
			continue
		buf2 = parse(buf,static,__cdescr__=f"parsesParenth[{buf=}]({parenth=},{static=})")
		value.append(buf2)
	#while None in value:
	#	value.remove(None)
	return value

ALUSWI = {
	"+":"ADD",
	"-":"SUB",
	"*":"MUL",
	"/":"MUL",
	"%":"MOD",
	"&":"BAND",
	"|":"BOR",
	"^":"XOR",
	"~":"BNOT",
	">":"SUP",
	"<":"INF",

	"&&":"LAND",
	"||":"LOR",
	"<<":"LSHIFT",
	">>":"RSHIFT",
	"==":"EQL",
	">=":"SUPEQL",
	"<=":"INFEQL",
	"!=":"NEQL",

	"!":"NOT",
	"++":"INCR",
	"--":"DECR"
}

def parseTree(element):
	if element == None:
		return None
	elif type(element)==int:
		return context.Constant(element,context.defaults["int"])
	elif type(element)==float:
		return context.Constant(element,context.defaults["float"])
	elif type(element)==bool:
		return context.Constant(element,context.defaults["bool"])
	elif type(element)==str:
		if element[0] == '"':
			buff = context.getTypeByName("string")
			if buff:
				return context.Constant(element,buff)
			buf = context.Pointer(context.getTypeByName("char"))
			cst = context.Constant(
				element,
				buf
			)
			return cst
		elif element[0] =="'":
			return context.Constant(
				element,
				context.getTypeByName("char")
			)
		elif element == "NULL":
			return context.Constant(
				element,
				context.getTypeByName("int")
			)
		buff = context.getAnyByName(element)
		if buff:
			return buff
	elif element[0] in "+-*/|&^%":
		buff1 = parseTree(element[1])
		buff2 = parseTree(element[2])
		if type(buff1) == context.Constant and type(buff2) == context.Constant:
			return context.Constant(eval("buff1.value"+element[0]+"buff2.value"),buff1.type)
		return Operation(buff1,element[0],buff2)
	elif element[0] == "||":
		buff1 = parseTree(element[1])
		buff2 = parseTree(element[2])
		if type(buff1) == context.Constant and type(buff2) == context.Constant:
			return context.Constant(buff1.value or buff2.value,buff1.type)
		return Operation(buff1,element[0],buff2)
	elif element[0] == "!":
		buff1 = parseTree(element[1])
		if type(buff1) == context.Constant:
			return context.Constant(not buff1.value,buff1.type)
		return Operation(buff1,element[0])
	elif element[0] == "&&":
		buff1 = parseTree(element[1])
		buff2 = parseTree(element[2])
		if type(buff1) == context.Constant and type(buff2) == context.Constant:
			return context.Constant(buff1.value and buff2.value,buff1.type)
		return Operation(buff1,element[0],buff2)
	elif element[0] == "~":
		buff1 = parseTree(element[1])
		buff2 = parseTree(element[2])
		if type(buff1) == context.Constant and type(buff2) == context.Constant:
			return context.Constant(buff1.value ,buff1.type)
		return Operation(buff1,element[0],buff2)
	elif element[0] == "NEW":
		buff = parseTree(element[1])

	
def uncoverData(data):
	# Remove covering characters and keep spaces and other shits.
	# For example, this ([{{"Hello world !"}}]) gives -> Hello world !
	if data[0] in "([{":
		return uncoverData(data[1:-1])
	return data
	
		
"""
Static levels:
0 : Full static, global env.
1 : in_place, local env.
2 : used data, any env. (int a = func() ==> func() is static=2)

"""
def parse(ln:list[str],static=0,definition=False,__cdescr__="???:"):
	if type(ln) != list:
		raise TypeError("parse(list[str] ln, int static, bool definition, str __cdescr__)")
	if ln == None or ln[0] == "":
		return None
	if len(ln)==1:
		if ln[0][0] == "(":
			return parse(split(ln[0][1:-1]),static,definition, __cdescr__+f"parse({ln=},{static=},{definition=}):")
		buf = context.getAnyByName(ln[0])
		if buf:
			return buf
		else:
			parsed = ALUexpr.parser.parse(ALUexpr.lexer.tokenize(ln[0]))
			buf = parseTree(parsed)
			if buf:
				return buf
			else:
				traceback("ParserError",f"Parser got a list of one element which do not represent anything : {ln}",__cdescr__=f"parser({ln},{static})")
	
	linking_templates = []

	if ln[-1] == ";":
		warning("UselessExpression","You can remove \";\", it's useless.")
	if ln[0] == "#":
		r = PreProc(ln[1],ln[2:])
		execPreProc(r)
		return r
	elif ln[0] == "template":
		# For now it's like this : template A,B,C
		# But later you'll be able to use this syntax
		#			template A=int,B=char,C=float
		for i in ln[1::2]:
			buff = Template(i)
			linking_templates.append(buff)
	elif ln[0] == "return":
		return ReturnStatement(ln[1:])
	elif ln[0] == "break":
		return BreakStatement()
	elif ln[0] == "continue":
		return ContinueStatement()
	elif ln[0] == "*":
		return valueGetter(parse(ln[1:],__cdescr__=__cdescr__+f"parse({ln=},{static=},{definition=}):"),2)
	elif ln[0] == "&":
		return adressGetter(parse(ln[1:],__cdescr__=__cdescr__+f"parse({ln=},{static=},{definition=}):"),2)
	elif ln[0] == "extern":
		if ln[1].upper() == "C":
			return ExternalC(ln[2])
		elif ln[1].upper() == "ASM":
			return ExternalASM(ln[2])
		elif len(ln) > 1:
			traceback("ExternKeywordError",f"The language named {ln[1]} is unknown or can't be used with the extern keyword.")
		else:
			traceback("ExternKeywordError",f"The extern keyword needs a language, like C or ASM.",syntax="extern <language> {<code>}")
	elif ln[0] == "typedef":
		context.CTX << context.Class(ln[-1], context.getTypeSize(" ".join(ln[1:-1])))
	else:
		is_type = (context.getTypeByName(i) for i in ln)
		is_func = tuple(context.getFuncByName(i) for i in ln)
		decl = _recognizeDeclaration(ln,tuple(is_type),"parse: ")
		verifySymbolsShapeSyntax(ln)
		"""
		print("================================================================")
		print("RAM_size:",getRAMsize())
		print(f"{ln=}\n{is_type=}\n{is_func=}\n{decl=}\n{linking_templates=}\n{context.CTX=}")
		print(__cdescr__)
		"""
		if ln[0] == "main":
			context.CTX << context.Func(context.getTypeByName("int"),"main",makeDefArguments(ln[1],context.CTX)) # Create ctx.Func
			decl = Declaration(context.getTypeByName("int"),"main",None, None, None, DECL_FUNC,octx=context.CTX[-1]) # Create declaration
			context.CTX = context.CTX[-1].ctx # Dive into ctx.Func's context.
			decl.init = makeDefArguments(ln[1],context.CTX) # Set decl's arguments
			decl.value = parsesParenth(ln[2],1,__cdescr__ + f"parse({ln=},{static=},{definition=}): ") # Set decl's content
			context.CTX = context.CTX.getParentCTX()
			return decl
		elif is_func[0]:
			# For later : use ln[2:] for call extensions like:
			#  a(b) as c
			if static < 2:
				return StaticCall(is_func[0],makeCallArguments(ln[1],is_func[0]))
			else:
				return DataCall(is_func[0],makeCallArguments(ln[1],is_func[0]))
		elif decl:
			return decl
		else:
			parsed = ALUexpr.parser.parse(ALUexpr.lexer.tokenize(" ".join(ln)))
			return parseTree(parsed)





"""

			THIS IS THE COMPILER PART
	I WASN'T ABLE TO DISPATCH IT IN THE compiler.py
			   SO IT IS HERE BY NOW


"""

auto_delete_pointers = []
SHOULD_EXIST = 1
COULD_EXIST = 0
class DictKeyGenerator:
	def __init__(self,dico={}):
		self.dico = dico
	def keys(self):
		return self.dico.keys()
	def __getitem__(self,name):
		if type(name) == tuple:
			existance = name[1]
			name = name[0]
		else:
			existance = COULD_EXIST
		if type(name) == str:
			leaf_obj = context.getAnyByName(name)
			baked_ctx = context.bakeContextName(leaf_obj)
			if name in self.dico.keys():
				return self.dico[baked_ctx]
			if existance:
				traceback(
					"NameError",
					f"Unknown name \"{name}\".",
					__cdescr__=f"DictKeyGenerator::__getitem__({name=},{existance=}): "
				)
			if glb.config["KEEP_NAMES"]:
				self.dico[baked_ctx] = name
			else:
				self.dico[baked_ctx] = glb.genName()
			return self.dico[baked_ctx]
		else:
			baked_ctx = context.bakeContextName(name)
			if baked_ctx in self.dico.keys():
				return self.dico[baked_ctx]
			if existance:
				traceback(
					"NameError",
					f"Unknown object \"{name.getCSyntax().raw}\".",
					__cdescr__=f"DictKeyGenerator::__getitem__({name=},{existance=}): "
				)
			if glb.config["KEEP_NAMES"]:
				self.dico[baked_ctx] = name
			else:
				self.dico[baked_ctx] = glb.genName()
			return self.dico[baked_ctx]
	def __setitem__(self,name,value):
		self.dico[name] = value
	def __repr__(self) -> str:
		return str(self.dico)
names = DictKeyGenerator()

IN_EXTERN_C = False


def top_parser(e):
	buf = split_line(e.read())
	buf = regroup_text(buf)
	buff = buf
	if glb.READING_NLINE == None:
		glb.READING_NLINE = 1
	glb.READING_NLINE = 1
	for i in buff:
		if i=="":continue
		glb.READING_LINE = i
		if i == LineJump:
			glb.READING_NLINE += 1
		else:
			buf = split(i,f"top_parser({e=}): ")
			s = buf
			while "" in s:
				s.remove("")
			if len(s)>0:
				prs = parse(s,static=0,__cdescr__=f"top_parser({e=}):")
				if prs:
					yield prs

def getTypesFromArgDef(argdef: list[DefArgument]) -> Iterable:
	return list(map(lambda x: x.type, argdef))

def execPreProc(preproc):
	global __code__
	if preproc.command in ("include","incl"):
		includable = os.listdir(os.getcwd()) + os.listdir(__dir__+"/includes/")
		toinclude = []
		for incl in preproc.data:
			if incl[0] == '"':
				toinclude.append(incl[1:-1])
			elif incl+".lfh" in includable:
				toinclude.append(__dir__ + "/includes/"+incl+".lfh")
		for i in toinclude:
			save__code__ = __code__
			__code__ = ""
			backtracks = (glb.rfile, glb.READING_NLINE)
			glb.rfile, glb.READING_NLINE = (i,None)
			with open(i) as e:
				lf_compile_to_C(e,is_main=False)
			glb.rfile, glb.READING_NLINE = backtracks
			__code__ += "\n" + save__code__
	elif preproc.command == "funfix":
		argdecl_idx = glb.fstartwith(preproc.data,"(")
		if len(preproc.data) < 3 or argdecl_idx == None or len(preproc.data[:argdecl_idx]) < 2:
			traceback(
				"[Preprocessor] SyntaxError",
				"Incorrect syntax to use with #funfix.",
				syntax="#funfix [keywords,...] <return type> <name>([<arg type> <arg name>,...])",
				__cdescr__=f"execPreProc({preproc})"
			)
		if preproc.data[-2] == "as":
			names[preproc.data[-1]] = preproc.data[argdecl_idx-1]
			context.CTX << context.Func(
				context.getTypeByName(preproc.data[argdecl_idx-2]),
				preproc.data[-1],
				None,
			)
		else:
			names[preproc.data[argdecl_idx-1]] = preproc.data[argdecl_idx-1]
			context.CTX << context.Func(
				context.getTypeByName(preproc.data[argdecl_idx-2]),
				preproc.data[argdecl_idx-1],
				None,
			)
		decl = Declaration(
			context.getTypeByName(preproc.data[argdecl_idx-2]),
			preproc.data[argdecl_idx-1],
			None, FIXED_FUNCTION, preproc.data[:argdecl_idx-2], DECL_FUNC, octx=context.CTX[-1]
		) # Create declaration
		context.CTX = context.CTX[-1].ctx # Dive into ctx.Func's context.
		decl.init = makeDefArguments(preproc.data[argdecl_idx],context.CTX) # Set decl's arguments
		context.CTX = context.CTX.getParentCTX()
		context.CTX[-1].atypes = getTypesFromArgDef(decl.init)

		__code__included.append(decl)
	elif preproc.command == "classfix":
		if len(preproc.data) < 1:
			traceback(
				"[Preprocessor] SyntaxError",
				"Incorrect syntax to use with #classfix.",
				syntax="#classfix <name> [s(<size|class with defined type>)] [p(<properties>)] [a(<attrib0>[,attrib1, ...])]",
				__cdescr__=f"execPreProc({preproc})"
			)
		sized=None
		properties=0
		attribs=[]
		last = None
		ctx_class = context.Class(preproc.data[0],None,context.CTX,None)
		context.CTX << ctx_class
		for i in preproc.data[1:]:
			if last=="s":
				if i[1:-1].isnumeric():
					sized = int(i[1:-1])
				else:
					sized=context.getTypeSize(i[1:-1])
			elif last=="p":
				for j in i[1:-1].split(","):
					properties|=eval("classfix_consts."+j)
			elif last=="a":
				attribs = makeDefArguments(i,context.CTX[-1].ctx)
			last = i
		if properties == 0:
			properties = classfix_consts.CLASS_ANYUSE
		ctx_class.properties = properties
		ctx_class.size = sized
		context.types.append(ctx_class)
		context.types[-1].ctx += attribs
	elif preproc.command == "varfix":
		if context.CTX.obj == None:
			context.CTX << context.Var(context.getTypeByName(" ".join(preproc.data[:-1])),preproc.data[-1],context.GLOBAL)
		else:
			context.CTX << context.Var(context.getTypeByName(" ".join(preproc.data[:-1])),preproc.data[-1],context.CTX.obj)
	elif preproc.command in ("define","def"):
		buff = context.Macro(preproc.data[0])
		context.DEFINES[buff] = context.MacroResult(preproc.data[1],buff)
	return None
					

def lf_compile_to_C(file,is_main=True):
	global __code__
	def addCode(*s,sep=" "):
		global __code__
		__code__ += sep.join(s)
	def addLine(*s,sep=" ",end=";"):
		global __code__
		addCode(*s,sep=sep)
		__code__ += end
	def incmp(_if, cmp, _else):
		return _if if cmp else _else
	def mapjoin(str_join,ls, lmbd):
		return str_join.join(map(lmbd, ls))
	def build(i):
		global __code__
		if type(i) in (PreProc,):
			#execPreProc(i)
			__code__+="\n"
		elif type(i) == ExternalC:
			addCode(i.code)
		elif type(i) == Declaration:
			if i.decl_type == DECL_FUNC:
				if i.value == FIXED_FUNCTION:
					return
				#function
				addCode(*i.keywords,f"{i.type.getCSyntax().raw} {names[i.octx]}(")
				for j in i.init:
					build(j)
					__code__+=", "
				if len(i.init) > 0:
					__code__ = __code__[:-2] # Remove the last comma
				addCode(") {")
				for j in i.value:
					build(j)
					__code__+=";"
				addCode("}")
			elif i.decl_type == DECL_VAR_NO_DEFAULT:
				#variable/const with no value
				if i.name in names.keys():
					traceback("DeclarationError",f"You declared for the second time {i.name}.",__cdescr__=f"lf_compile_to_C(parsed=<long list...>, {is_main=}): build({i=})")
				addCode(*i.keywords,f"{i.type} {names[i.octx]}")
			elif i.decl_type == DECL_VAR_DEFAULT_VAL:
				if i.name in names.keys():
					traceback("DeclarationError",f"You declared for the second time {i.name}.",__cdescr__=f"lf_compile_to_C(parsed=<long list...>, {is_main=}): build({i=})")
				if type(i.value) == context.Constant:
					addCode(*i.keywords,i.type.getCSyntax().raw,names[i.octx],"=",f"({i.type.getCSyntax().raw})",str(i.value.value))
			elif i.decl_type == DECL_VAR_DEFAULT_INIT:
				if i.name in names.keys():
					traceback("DeclarationError",f"You declared for the second time {i.name}.",__cdescr__=f"lf_compile_to_C(parsed=<long list...>, {is_main=}): build({i=})")
				addCode(*i.keywords,i.type,names[i.octx])
				pre_cst_str = f"{i.type}::pre_cst(&{names[i.octx]},"+",".join([])
				addCode(pre_cst_str)
			else:
				print("WTF DECL")
		elif type(i) == DefArgument:
			if i.default_value:
				addCode(i.type.getCSyntax().raw,names[i.octx],"=",i.default_value)
			else:
				addCode(i.type.getCSyntax().raw,names[i.octx])
		elif type(i) == CallArgument:
			if i.name == None:
				if type(i.value) in (context.Var, context.Func):
					addCode(names[i.value,SHOULD_EXIST])
				else:
					addCode(i.value.getCSyntax().raw)
			else:
				addCode(names[i.octx],"=",i.value.getCSyntax().raw)
		elif type(i) == StaticCall:
			addCode(names[i.func] + '(')
			build(i.arguments[0])
			for j in i.arguments[1:]:
				addCode(",")
				build(j)
			addCode(')')
			
	"""if is_main:
		#fill auto_delete_pointers
		#find main function index
		m = glb.find(top_parser(file),lambda x: type(x) == Declaration and x.name == glb.config["MAIN_NAME"])
		m.value.extend((DeleteStatement(i) for i in auto_delete_pointers))
	"""
	for i in top_parser(file):
		print(i)
		build(i)
		__code__+= ";"




