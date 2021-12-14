/*
		HOW DOES THIS WORK ?
Let's explain trhough examples:
=============(splitText)==============
=>	print("Hello world")
=============(splitLine)==============
->	[print, ("Hello world")]
=============(tokenize)===============
->  [LX_NAME, LX_INPARENTH]
=============(parse)==================
	->  [LX_NAME, LX_INPARENTH] => ++EXPR_CALL
	->  [LX_INPARENTH]			=> EXPR_NOTHING
->  [EXPR_CALL] (result)
->  [EXPR_CALL] (sorted by level of precedence)
=============(top_parser)=============
	=====(top_parser:[for loop 1])====
->  FuncCall(
		print,
		[
			CallArg(
				context::ConstExpr(context::const char*, "\"Hello world\"")
			)
		]
	)
-> Add to list "should exist" in context::GLOBAL, context::Func(<Unknown>, print, [context::const char*])
	=====(top_parser:[outside of loops])
-> Verify coherence of "should exist" with context and sub-contexts of context::GLOBAL
===============(compiler)=============
-> Translate objects to C code.
===============(main)=================
-> Write C code into corresponding file.
-> Use gcc to compile
-> if "-run" run .exe


=============(splitText)==============
=>	a += 350
=============(splitLine)==============
->	[a, +, =, 350]
=============(tokenize)===============
->  [LX_NAME, LX_ADD, LX_SET, LX_INTEGER]
=============(parse)==================
	->  [LX_NAME, LX_ADD, LX_SET, LX_INTEGER] => ++EXPR_STATIC_ADD_NAME_INTEGER
	->  [LX_ADD, LX_SET, LX_INTEGER]		  => EXPR_NOTHING
	->  [LX_SET, LX_INTEGER]				  => EXPR_NOTHING
	->	[LX_INTEGER]						  => EXPR_NOTHING
->  [EXPR_STATIC_ADD_NAME_INTEGER] (result)
->  [EXPR_STATIC_ADD_NAME_INTEGER] (sorted by level of precedence)
=============(top_parser)=============
	=====(top_parser:[for loop 1])====
->	Operation(
		OPERATION_STATIC_ADD,
		[context::Var(a),context::ConstExpr(int,350)]
	)


=============(splitText)==============
=>	b = 2+350*50
=============(splitLine)==============
->	[b, +, =, 2, +, 350, *, 50]
=============(tokenize)===============
->  [LX_NAME, LX_ADD, LX_SET, LX_INTEGER, LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER]
=============(parse)==================
	->  [LX_NAME, LX_ADD, LX_SET, LX_INTEGER, LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER] => ++EXPR_STATIC_ADD_NAME_INTEGER
	->  [LX_ADD, LX_SET, LX_INTEGER, LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER]		  => EXPR_NOTHING
	->  [LX_SET, LX_INTEGER, LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER]				  => EXPR_NOTHING
	->	[LX_INTEGER, LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER]						  => ++EXPR_ADD_INTEGER_INTEGER
	->	[LX_ADD, LX_INTEGER, LX_MUL, LX_INTEGER]						  			  => EXPR_NOTHING
	->	[LX_INTEGER, LX_MUL, LX_INTEGER]						  					  => ++EXPR_MUL_INTEGER_INTEGER
	->	[LX_MUL, LX_INTEGER]						  					  			  => EXPR_NOTHING
	->	[LX_INTEGER]						  					  					  => EXPR_NOTHING
->  [EXPR_STATIC_ADD_NAME_INTEGER, EXPR_ADD_INTEGER_INTEGER, EXPR_MUL_INTEGER_INTEGER] (result)
->  [EXPR_STATIC_ADD_NAME_INTEGER, EXPR_MUL_INTEGER_INTEGER, EXPR_ADD_INTEGER_INTEGER] (sorted by level of precedence)
=============(top_parser)=============
	=====(top_parser:[for loop 1])====
(Check first element of parser, if it's static operation, read from back[-1] to front[0])
->	Operation(
		OPERATION_STATIC_ADD,
		[context::Var(b),Operation(OPERATION_ADD,context::ConstExpr(2),Operation())]
	)

*/

#pragma once
#include "glb.hpp"

typedef uint8_t lexic_t;
enum LEXIC : lexic_t {
	LX_MAIN,
	LX_NAME,
	LX_INTEGER,
	LX_FLOAT,
	LX_DOUBLE ,
	LX_HEX_INT,
	LX_BIN_INT,
	LX_STRING,
	LX_CHAR,
	LX_ADD,
	LX_BOOL,
	LX_INCR,
	LX_DECR,
	LX_SUB,
	LX_MUL,
	LX_DIV,
	LX_MOD,
	LX_AND,
	LX_OR,
	LX_NOT,
	LX_XOR,
	LX_BNOT,
	LX_SET,
	LX_INF,
	LX_SUP,
	LX_NEW,
	LX_MEMBACCSS,
	LX_INPARENTH, // ()
	LX_INBRACKETS, // []
	LX_INBRACES, // {}
	LX_CONSTANTSLICE,

	LX_BIN_AND,
	LX_BIN_OR,
	LX_RSHIFT,
	LX_LSHIFT,
	LX_EQL,
	LX_LESSEQL,
	LX_GREATEQL,
	LX_PTRACCSS,
	LX_STATIC_ADD,
	LX_STATIC_SUB,
	LX_STATIC_MUL,
	LX_STATIC_DIV,
	LX_STATIC_MOD,
	LX_STATIC_BIN_AND,
	LX_STATIC_BIN_OR,
	LX_STATIC_BIN_NOT,
	LX_STATIC_AND,
	LX_STATIC_OR,
	LX_STATIC_LSHIFT,
	LX_STATIC_RSHIFT,
	LX_NOT_EQL,
	LX_STATIC_XOR,

	LX_SLICE,
	LX_STATIC_ACCSS
};

class Token {
public:
	std::regex regx;
	lexic_t name;
	Token(lexic_t name, string_t rgx) : name(name), regx(rgx) {};
};

// Will try to match from top to bottom
Token lexic[] = {
	Token(LEXIC::LX_MAIN          ,"main"),
	Token(LEXIC::LX_BOOL          ,"(true|false)"),
	Token(LEXIC::LX_NAME          ,"[a-zA-Z_][a-zA-Z_0-9]*"),
	Token(LEXIC::LX_INTEGER       ,"(-)?[0-9]+"),
	Token(LEXIC::LX_FLOAT         ,"(-)?[0-9]+(\\.?)[0-9_]*f?"),
	Token(LEXIC::LX_DOUBLE        ,"(-)?[0-9]+(\\.?)[0-9_]*d"),
	Token(LEXIC::LX_HEX_INT       ,"0x[0-9a-fA-F]+"),
	Token(LEXIC::LX_BIN_INT       ,"0b[01]+"),
	Token(LEXIC::LX_STRING        ,"\"(.|\\\\\")*\""),
	Token(LEXIC::LX_CHAR          ,"'(.|\\.)'"),
	Token(LEXIC::LX_STATIC_ADD	  ,"\\+="),
	Token(LEXIC::LX_STATIC_SUB	  ,"-="),
	Token(LEXIC::LX_STATIC_MUL	  ,"\\*="),
	Token(LEXIC::LX_STATIC_DIV	  ,"\\/="),
	Token(LEXIC::LX_STATIC_MOD	  ,"\\%="),
	Token(LEXIC::LX_STATIC_BIN_AND,"&="),
	Token(LEXIC::LX_STATIC_BIN_OR ,"\\|="),
	Token(LEXIC::LX_STATIC_BIN_NOT,"~="),
	Token(LEXIC::LX_STATIC_AND	  ,"&&="),
	Token(LEXIC::LX_STATIC_OR	  ,"\\|\\|="),
	Token(LEXIC::LX_STATIC_LSHIFT ,"<<="),
	Token(LEXIC::LX_STATIC_RSHIFT ,">>="),
	Token(LEXIC::LX_NOT_EQL	      ,"!="),
	Token(LEXIC::LX_STATIC_XOR	  ,"\\^="),
	Token(LEXIC::LX_ADD           ,"\\+"),
	Token(LEXIC::LX_SUB           ,"-"),
	Token(LEXIC::LX_MUL           ,"\\*"),
	Token(LEXIC::LX_DIV           ,"/"),
	Token(LEXIC::LX_MOD           ,"\\%"),
	Token(LEXIC::LX_AND           ,"&&"),
	Token(LEXIC::LX_OR            ,"\\|\\|"),
	Token(LEXIC::LX_BIN_AND       ,"&"),
	Token(LEXIC::LX_BIN_OR        ,"\\|"),
	Token(LEXIC::LX_NOT           ,"\\!"),
	Token(LEXIC::LX_XOR           ,"\\^"),
	Token(LEXIC::LX_BNOT          ,"~"),
	Token(LEXIC::LX_SET           ,"="),
	Token(LEXIC::LX_EQL           ,"=="),
	Token(LEXIC::LX_INF           ,"<"),
	Token(LEXIC::LX_SUP           ,">"),
	Token(LEXIC::LX_LSHIFT        ,"<<"),
	Token(LEXIC::LX_RSHIFT        ,">>"),
	Token(LEXIC::LX_LESSEQL       ,"<="),
	Token(LEXIC::LX_GREATEQL      ,">="),
	Token(LEXIC::LX_NEW           ,"new"),
	Token(LEXIC::LX_MEMBACCSS     ,"\\."),
	Token(LEXIC::LX_PTRACCSS      ,"-\\>"),
	Token(LEXIC::LX_STATIC_ACCSS  ,"::"),
	Token(LEXIC::LX_SLICE         ,":"),
	Token(LEXIC::LX_CONSTANTSLICE ,"\\[(0(x|b))?[0-9]+(:(0(x|b))?[0-9]){0,2}\\]"),
	Token(LEXIC::LX_INPARENTH	  ,"\\(.*\\)"),
	Token(LEXIC::LX_INBRACKETS	  ,"\\[.*\\]"),
	Token(LEXIC::LX_INBRACES	  ,"\\{.*\\}"),
};
constexpr size_t lexic_size = sizeof(lexic)/sizeof(Token);

class S_Token : public Token {
public:
	string_t str;
	S_Token(Token tk, string_t str) : Token(tk), str(str) {};
};

list_t<S_Token> tokenize(list_t<string_t> s) {
	list_t<S_Token> ret;
	for (string_t i: s) {
		for (size_t j = 0; j < lexic_size; j++) {
			LOG("tokenize: \"" << i << "\"; " << (int)lexic[j].name);
			if (std::regex_search(i, lexic[j].regx)) {
				ret.push_back(S_Token(lexic[j], i));
				break;
			}
		}
	}
	return ret;
}



typedef uint8_t token_id_string_t;
enum TIS_KEYS : token_id_string_t {
	EXPR_NOTHING, // Have to be 0
	EXPR_CALL,
	EXPR_GET_INDEX,
	EXPR_CONST_SLICE,
	EXPR_FUNC_DECL,
	EXPR_MAIN_DECL
};

typedef uint8_t precedence_level_t;
enum PRE_LEVEL : precedence_level_t {
	PRE_VERY_LOW,
	PRE_LOW,
	PRE_MEDIUM,
	PRE_HIGH,
	PRE_VERY_HIGH
};

class TokenIdString_Output {
public:
	list_t<S_Token> stokens;
	token_id_string_t tis;
	precedence_level_t pre_lvl;
	TokenIdString_Output(list_t<S_Token> stokens, token_id_string_t tis, precedence_level_t pre) : stokens(stokens), tis(tis), pre_lvl(pre) {};
	TokenIdString_Output(const TokenIdString_Output& other) {
		this->stokens.reserve(other.stokens.size());
		for (S_Token i: other.stokens) {
			this->stokens.push_back(i);
		}
		this->tis = other.tis;
		this->pre_lvl = other.pre_lvl;
	}
	TokenIdString_Output& operator=(TokenIdString_Output other) {
		this->stokens.reserve(other.stokens.size());
		for (S_Token i: other.stokens) {
			this->stokens.push_back(i);
		}
		this->tis = other.tis;
		this->pre_lvl = other.pre_lvl;
		return *this;
	}
};

class TokenIdString {
public:
	list_t<lexic_t> str;
	token_id_string_t name;
	precedence_level_t prio;

	TokenIdString(list_t<lexic_t> lxs, token_id_string_t name, precedence_level_t priority=0) : str(lxs), name(name), prio(priority) {};
	TokenIdString_Output isme(S_Token* s, size_t length) {
		if (length < this->str.size()) {
			return TokenIdString_Output({}, TIS_KEYS::EXPR_NOTHING, 0);
		}
		for (size_t i = 0; i < this->str.size(); i++) {
			if (s[i].name != this->str[i]) {
				return TokenIdString_Output({}, TIS_KEYS::EXPR_NOTHING, 0);
			}
		}
		if (length == this->str.size()) {
			list_t<S_Token> buf;
			buf.reserve(length);
			for (size_t i=0; i < length; i++) {
				buf.push_back(s[i]);
			}
			return TokenIdString_Output(buf, this->name, this->prio);
		}
		list_t<S_Token> ls;
		for (size_t i = 0; i < this->str.size(); i++) {
			ls.push_back(s[i]);
		}
		return TokenIdString_Output(ls, this->name, this->prio);
	}
};

TokenIdString tis[] = {
	TokenIdString({LEXIC::LX_MAIN,LEXIC::LX_INPARENTH, LEXIC::LX_INBRACES}, TIS_KEYS::EXPR_MAIN_DECL, PRE_LEVEL::PRE_VERY_HIGH),
	TokenIdString(
		{LEXIC::LX_NAME,LEXIC::LX_NAME,LEXIC::LX_INPARENTH, LEXIC::LX_INBRACES},
		TIS_KEYS::EXPR_FUNC_DECL,
		PRE_LEVEL::PRE_VERY_HIGH
	),
	TokenIdString({LEXIC::LX_NAME,LEXIC::LX_INPARENTH}, TIS_KEYS::EXPR_CALL, PRE_LEVEL::PRE_VERY_HIGH),
	TokenIdString({LEXIC::LX_NAME,LEXIC::LX_CONSTANTSLICE}, TIS_KEYS::EXPR_CONST_SLICE, PRE_LEVEL::PRE_VERY_HIGH),
	TokenIdString({LEXIC::LX_NAME,LEXIC::LX_INBRACKETS}, TIS_KEYS::EXPR_GET_INDEX, PRE_LEVEL::PRE_VERY_HIGH),
};

list_t<TokenIdString_Output> parse(list_t<S_Token> s) {
	list_t<TokenIdString_Output> return_list;
	for (size_t i=0; i < s.size(); i++) {
		S_Token* arr = &(s.front())+i;
		for (TokenIdString i_tis: tis) {
			// TODO: Optimize here
			TokenIdString_Output buf(i_tis.isme(arr,s.size()-i));
			if (buf.tis) {
				return_list.push_back(buf);
				break;
			}
		}
	}
	bubbleSort(return_list, [&](TokenIdString_Output a) {
		return a.pre_lvl;
	});
	return return_list;
}







