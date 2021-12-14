from errors import *
from sly import Lexer,Parser

class ALULexer(Lexer):
	ignore = '\t '
	literals = { '=',  '(', ')', ',', ';',
				'{','}','[',']', '<', '>', '#'}
	tokens = {
		NAME,
		INTERGER,
		FLOAT,
		STRING,
		CHAR,
		BOOL,

		ADD,
		INCR,
		SUB,
		DECR,
		MUL,
		DIV,
		MOD,
		AND,
		OR,
		NOT,
		XOR,
		BAND,
		BOR,
		BNOT,
		RSHIFT,
		LSHIFT,
		EQL,
		INF,
		SUP,
		INFEQL,
		SUPEQL,
		NEW,
		PTRACCSS,
		MEMBACCSS
	}

	# Define tokens as regular expressions
	# (stored as raw strings)
	NAME = r'[a-zA-Z_]([a-zA-Z0-9_]|::|->|\.)*'
	STRING = r'\".*\"'
	CHAR = r"\'(.|\\.)\'"
	BOOL = r'(true|false)'
	INTERGER = r'-?\d+'
	FLOAT = r'[0-9]*\.[0-9]*(f|d)?'

	ADD = r"\+"
	INCR = r"\+\+"
	DECR = r"--"
	SUB = r"-"
	MUL = r"\*"
	DIV = r"/"
	MOD = r"\%"
	AND = r"&&"
	OR  = r"\|\|"
	NOT = r"\!"
	XOR = r"\^"
	BAND= r"&"
	BOR = r"\|"
	BNOT= r"~"
	RSHIFT=r">>"
	LSHIFT=r"<<"
	EQL = r"=="
	INF = r"<"
	SUP = r">"
	INFEQL=r"<="
	SUPEQL=r">="
	NEW = r"new"
	PTRACCSS = r"-\>" # NOT DONE !
	MEMBACCSS = r"\." # NOT DONE !

	def error(self, t):
		print("Illegal character '%s'" % t.value[0])
		self.index += 1

class ALUParser(Parser):
	#tokens are passed from lexer to parser
	tokens = ALULexer.tokens
	debugfile="parser.out"

	precedence = (
		("left", AND, OR),
		("left", EQL, SUP, INF, INFEQL, SUPEQL),
		("left", ADD, SUB),
		("left", MUL, DIV),
		("left", NOT),
		("left", INCR, DECR, MEMBACCSS, PTRACCSS),
	)
	def __init__(self):
		self.env = { }

	@_('')
	def statement(self, p):
		pass

	@_('expr')
	def statement(self, p):
		return p.expr

	@_('expr MEMBACCSS expr')
	def expr(self, p):
		return ('.',p.expr0, p.expr1)
	
	@_('expr PTRACCSS expr')
	def expr(self, p):
		return ('->',p.expr0, p.expr1)

	@_('expr SUPEQL expr')
	def expr(self,p):
		return ('>=',p.expr0, p.expr1)
	
	@_('expr SUP expr')
	def expr(self,p):
		return ('>',p.expr0, p.expr1)
	
	@_('expr RSHIFT expr')
	def expr(self,p):
		return ('>>',p.expr0, p.expr1)
	
	@_('expr LSHIFT expr')
	def expr(self,p):
		return ('<<',p.expr0, p.expr1)

	@_('expr INF expr')
	def expr(self,p):
		return ('<',p.expr0, p.expr1)
	
	@_('expr INFEQL expr')
	def expr(self,p):
		return ('<=',p.expr0, p.expr1)


	@_('expr ADD expr')
	def expr(self, p):
		return ('+',p.expr0,p.expr1)

	@_('expr INCR')
	def expr(self,p):
		return ('++',p.expr)

	@_('expr DECR')
	def expr(self,p):
		return ('--',p.expr)

	@_('expr SUB expr')
	def expr(self, p):
		return ('-',p.expr0,p.expr1)

	@_('expr MUL expr')
	def expr(self, p):
		return ('*',p.expr0,p.expr1)

	@_('expr DIV expr')
	def expr(self, p):
		return ('/',p.expr0,p.expr1)

	@_('expr MOD expr')
	def expr(self, p):
		return ('%',p.expr0,p.expr1)

	@_('expr AND expr')
	def expr(self, p):
		return ('&&',p.expr0,p.expr1)

	@_('expr OR expr')
	def expr(self, p):
		return ('||',p.expr0,p.expr1)

	@_('"(" expr ")"')
	def expr(self, p):
		return p.expr

	@_('NOT expr')
	def expr(self, p):
		return ('!',p.expr)

	@_('NEW expr')
	def expr(self, p):
		return ('NEW',p.expr)

	@_('expr XOR expr')
	def expr(self, p):
		return ('^',p.expr0,p.expr1)

	@_('expr BAND expr')
	def expr(self, p):
		return ('&',p.expr0,p.expr1)

	@_('expr BOR expr')
	def expr(self, p):
		return ('|',p.expr0,p.expr1)

	@_('BNOT expr')
	def expr(self, p):
		return ('~',p.expr)

	@_('expr EQL expr')
	def expr(self, p):
		return ('==',p.expr0,p.expr1)

	@_('NAME')
	def expr(self, p):
		return p.NAME
	@_('expr')
	def expr(self, p):
		return p.expr
	@_('STRING')
	def expr(self, p):
		return p.STRING
	@_('CHAR')
	def expr(self, p):
		return p.CHAR
	@_('FLOAT')
	def expr(self, p):
		return float(p.FLOAT)
	@_('INTERGER')
	def expr(self, p):
		return int(p.INTERGER)
	@_('BOOL')
	def expr(self, p):
		return bool(p.BOOL.capitalize())

	# def error(self, e):
	# 	if e.type == "SUB":
	# 		traceback("SyntaxError","Use parenthesis to let recognize signed numbers (use '(-3)' for example instead of '-3')")
	# 	print("ERROR")
	# 	for i in dir(e):
	# 		if i[0] != "_":
	# 			print(i,"=",getattr(e,i))

	def error(self, e):
		return

lexer = ALULexer()
parser = ALUParser()

