from copy import deepcopy
from typing import Iterable, Union
from errors import *
import re
from classprops import *

READING_LINE = ""
READING_NLINE = 1
DEFINES = {}

class ctx:
	def __init__(self,obj):
		self.v = []
		self.obj = obj # Upper object (Class(), Func(), or None)
	def getProcessedOBJ(self):
		if self.obj == None:
			return self
		return self.obj
	def getOBJctx(self):
		if self.obj == None:
			return self
		return self.obj.ctx
	def getParentCTX(self):
		if type(self.obj.parent) == ctx:
			return self.obj.parent
		return self.obj.parent.ctx
	def __getitem__(self,it):
		return self.v[it]
	def __setitem__(self,it,v):
		self.v[it] = v
	def __lshift__(self,el):
		self.v.append(el)
	def __iadd__(self,el):
		self.v += el
	def __repr__(self):
		return str(self.v)
	def __hash__(self):
		return self.v
	def makeList(self):
		l = []
		for i in self.v:
			l.append(i)
		if self.obj != None:
			for i in GLOBAL:
				ok = True
				for j in l:
					if i.name==j.name:
						ok=False
				if ok:
					l.append(i)
		return l


GLOBAL = ctx(None)

CTX = GLOBAL

def bakeContextName(obj: object,lasting: Union[None, str] = None) -> str:
	#print(lasting)
	if obj == None:
		traceback(
			"ContextBakingError",
			"Trying to bake context of object, but the object could not be found.",
			__cdescr__=f"bakeContextName({obj=}, {lasting=})"
		)
	if type(obj) == Constant:
		return obj.value
	if lasting == None:
		return bakeContextName(obj.parent, obj.name)
	if type(obj) == ctx: # GLOBAL env reached
		return lasting
	elif issubclass(type(obj), BaseClass):
		return bakeContextName(obj.parent,obj.name+"::"+lasting)
	else:
		return bakeContextName(obj.parent,obj.name+":"+lasting)

class Macro:
	def __init__(self,string: str):
		self.string = string
		# _.start()[1:-1] because I need to remove the brackets.
		self.vars = [_.start()[1:-1] for _ in re.finditer(r"[^\\]\{[a-zA-Z_][a-zA-Z_0-9]*[^\\]\}", string)]
		self.regx = re.sub(r"[^\\]\{[a-zA-Z_][a-zA-Z_0-9]*[^\\]\}","\b.*\b",self.string)
	def matchMacro(self, string):
		return re.match(self.regx, string)


class MacroResult:
	def __init__(self,string: str, macro: Macro):
		pass

class CSyntaxOutcome:
	def __init__(self, raw: str, after: list[str] = []):
		self.raw = raw
		self.data = after
	def __repr__(self) -> str:
		return f"CSyntaxOutcome(raw={self.raw},(after,data)={self.data})"

class Constant:
	def __init__(self,value,type):
		self.value = value
		self.type = type
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(f"({self.value})")
	def __repr__(self):
		return repr(self.value)

class BaseClass:
	def __repr__(self) -> str:
		return "<BaseClass>"
	def getCSyntax(self) -> CSyntaxOutcome:
		pass
	def getKeyWords(self) -> list[str]:
		pass
	def getSize(self) -> int:
		pass
	def makeTemplatedCopy(self,template: list) -> object:
		pass

class ClassMod(BaseClass):
	pass

class CArray(ClassMod):
	def __init__(self,_class: BaseClass,size=None):
		self._class = _class
		self.size = size
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(self._class.getCSyntax().raw,[f"[{self.size}]"])
	def __repr__(self):
		return f"(ARRAY[{self.size}] {self._class})"
	def getSize(self) -> int:
		return self._class.getSize() * self.size
	def makeTemplatedCopy(self, template: list) -> object:
		return CArray(self._class.makeTemplatedCopy(template), self.size)

class Pointer(ClassMod):
	def __init__(self,_class: BaseClass):
		self._class = _class
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(f"{self._class.getCSyntax().raw}*")
	def getSize(self) -> int:
		return glb.config["MAX_SIZE"]
	def makeTemplatedCopy(self, template: list) -> object:
		return Pointer(self._class.makeTemplatedCopy(template))
	def __repr__(self):
		return f"(PTR {self._class})"

class Templated(ClassMod):
	def __init__(self,_class: BaseClass,data=[]):
		self._class = _class
		self.data = data
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(f"{self._class.getCSyntax().raw}_T{'_'.join(self.data)}")
	def getKeyWords(self) -> list[str]:
		return ["template "+" ".join(self.data)] + self._class.getKeyWords()
	def getSize(self) -> int:
		cpy = self._class.makeTemplatedCopy(self.data)
		return cpy.getSize()
	def makeTemplatedCopy(self, template: list) -> object:
		return Templated(self._class.makeTemplatedCopy(template),self.data)
	def __repr__(self):
		return f"(TYPED<{self.data}> {self._class})"

class Extended(ClassMod):
	def __init__(self,_class: BaseClass):
		self._class = _class
	def getCSyntax(self) -> CSyntaxOutcome:
		# TODO
		pass
	def __repr__(self):
		return f"(EXTEND... {self._class})"

class ConstantType(ClassMod):
	def __init__(self,_class: BaseClass):
		self._class = _class
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(f"const "+self._class.getCSyntax().raw)
	def getKeyWords(self) -> list[str]:
		return ["const"] + self._class.getKeyWords()
	def getSize(self) -> int:
		return self._class.getSize()
	def makeTemplatedCopy(self, template: list) -> object:
		return ConstantType(self._class.makeTemplatedCopy(template))
	def __repr__(self) -> str:
		return f"(CONSTANT {self._class})"

class TupleType(ClassMod):
	def __init__(self,types: Iterable[BaseClass]):
		self._class = types
	def getKeyWords(self) -> list[str]:
		return self._class[0].getKeyWords()
	def getCSyntax(self) -> CSyntaxOutcome:
		# TODO
		pass
	def getSize(self) -> int:
		return max((i.getSize() for i in self._class))
	def makeTemplatedCopy(self, template: list) -> object:
		traceback(
			"ComplexityError",
			"It's becoming a bit of a mess.",
			"(type0,type1,...)<template> // Not allowed !",
			f"TupleType::makeTemplatedCopy({self=},{template=})"
		)
	def __repr__(self) -> str:
		return str(tuple(self._class))

class Class(BaseClass):
	def __init__(self,name,size:Union[int,None] =None,parent:Union[ctx, object] =GLOBAL,properties:int =CLASS_ANYUSE):
		self.name = name
		self.size = size
		self.properties = properties
		self.ctx: ctx = ctx(self)
		self.parent=parent
	def getSize(self) -> int:
		if self.size == None:
			self.size = 0
			for i in self.ctx:
				if type(i) == Var:
					self.size += i.getSize()
		return self.size
	def makeTemplatedCopy(self, template: list) -> object:
		buf = deepcopy(self)
		for i in buf.ctx:
			for t in template:
				if i.type.name == t.name:
					i.type = t.name
					break # Get to the next variable.
		return buf
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(self.name)
	def getKeyWords(self) -> list:
		return []
	def propertyTest(self, _property: int) -> bool:
		return self.properties & _property
	def __repr__(self):
		return f"<Class {self.name} [{self.size}]>"

types = [
	Class("bool",1),
	Class("int",4),
	Class("char",1),
	Class("short",2),
	Class("long",8),
	Class("float",4),
	Class("double",8),
	Class("void",1),
	Class("byte",1)
]

defaults = {
	"int":types[1],
	"float":types[5],
	"bool":types[0]
}

def getTypeByName(name: str):
	name = name.removeprefix(" ").removesuffix(" ")
	if name == "":
		return None
	if name[-1]=="*":
		return Pointer(getTypeByName(name[:-1]))
	elif name[-1]==">":
		# Correct this shit, because it will crash if we're in a comparison.
		template_def_idx = name.rfind("<")
		return Templated(getTypeByName(name[:template_def_idx]), [getTypeByName(i) for i in name[template_def_idx+1:-1].split(",")])
	elif name[0] == "(":
		return getAnyByName(name[1:-1])
	elif name.split(" ",1)[0] == "const":
		if len(name.split(" ",1)) < 2:
			return None
		return ConstantType(getTypeByName(name.split(" ",1)[1]))
	for i in types:
		#matched =re.search("^"+i.name+"\\b",name)
		if i.name == name:
			return i

def getTypeSize(name: str) -> int:
	name = name.removeprefix(" ").removesuffix(" ")
	if name == "":
		return None
	if name[-1]=="*":
		return glb.config["MAX_SIZE"]
	elif name[-1]==">":
		# Correct this shit, because it will crash if we're in a comparison.
		template_def_idx = name.rfind("<")
		return Templated(getTypeByName(name[:template_def_idx]), [getTypeByName(i) for i in name[template_def_idx+1:-1].split(",")])
	elif name[0] == "(":
		return TupleType([getTypeByName(i) for i in name[1:-1].split(",")])
	for i in types:
		matched =re.search("^"+i.name+"\\b",name)
		if matched:
			return i

def getFuncByName(name):
	s = CTX.makeList()
	for i in s:
		if i.name == name:
			return i

getVarByName = getFuncByName
# It's just the concept of use that is different
# I'm not throwing errors when we try to call a variable
# because we can store functions into vars

def getAnyByName(name):
	s = CTX.makeList()
	for i in s:
		if i.name == name:
			return i
	for i in types:
		if i.name == name:
			return i

class Var:
	def __init__(self,type: BaseClass,name: str, parent: Union[object, ctx]):
		self.type = type
		self.name = name
		self.parent = parent
	def getSize(self):
		return getTypeSize(self.type)
	def getCSyntax(self) -> CSyntaxOutcome:
		return CSyntaxOutcome(bakeContextName(self))
	def __repr__(self):
		return f"<Var {self.name} [{self.type}]>"

class Func:
	def __init__(self,rtype: BaseClass, name: str, atypes: list[BaseClass], parent: Union[object, ctx]=GLOBAL):
		self.rtype = rtype
		self.name = name
		self.atypes = atypes
		self.ctx = ctx(self)
		self.parent = parent
	def getSize(self):
		return 8
	def __repr__(self):
		return f"<Func {self.rtype} {self.name}{self.atypes}>"


### TODO
class Namespace:
	def __init__(self,name,parent=GLOBAL):
		self.name = name
		self.ctx = ctx(self)
		self.parent = parent
	def getSize(self):
		return 0
	def __repr__(self):
		return f"<Namespace {self.name} {self.ctx}>"


