#include "context.hpp"
#include "parser.hpp"
#define LO_SIMPLE_STRING 0
#define LO_NEW_LINE 1
#define NO_KEYWORD          0b000
#define KEYWORD_CONST       0b001
#define KEYWORD_STATIC      0b010
#define KEYWORD_VIRTUAL     0b100

typedef uchar keywords_t;

enum BEID {
	CONSTEXPR_HOLDER,
	CALL_ARG,
	DEF_ARG,
	FUNC_DECL,
	VAR_DECL_NO_VALUE,
	VAR_DECL_VALUE,
	VAR_DECL_INIT,
	OPERATION,
	VAR_SET,
	FUNC_CALL,
	IF_STATEMENT,
	ELIF_STATEMENT,
	ELSE_STATEMENT,
	FOR_STATEMENT,
	WHILE_STATEMENT,
	LOOP_STATEMENT
};

class BaseElement {
public:
	context::ContextObject* octx;
	uchar class_id;
};

class ConstexprHolder : public BaseElement {
public:
	string_t expr;
	ConstexprHolder(string_t expr, context::ContextObject* octx) : expr(expr) {
		this->octx = octx;
		this->class_id = BEID::CONSTEXPR_HOLDER;
	}
};

class CallArg : public BaseElement {
public:
	context::Class* type;
	context::ContextObject* value;

	CallArg(context::ContextObject* octx, context::ContextObject* value) {
		this->class_id = BEID::CALL_ARG;
		this->octx = octx;
		this->value = value;
	}
};

class DefArg : public BaseElement {
public:
	context::Class* type;
	context::ContextObject* value;

	DefArg(context::ContextObject* octx, context::ContextObject* value = nullptr) {
		this->class_id = BEID::DEF_ARG;
		this->octx = octx;
		this->value = value;
	}
};

class FuncDecl : public BaseElement {
public:
	context::Class* rtype;
	string_t name;
	list_t<DefArg> args;
	list_t<keywords_t> keywords;
	list_t<BaseElement> data;
	FuncDecl(context::Class* rtype, string_t name, list_t<DefArg> args, list_t<keywords_t> keywords, list_t<BaseElement> data, context::ContextObject* octx) {
		this->class_id = BEID::FUNC_DECL;
		this->rtype = rtype;
		this->name = name;
		this->args = args;
		this->keywords = keywords;
		this->data = data;
		this->octx = octx;
	};
};

struct LineObject {
	uchar flag;
	string_t content;
};

list_t<LineObject> splitText(string_t s) {
	list_t<LineObject> ret = {LineObject{LO_SIMPLE_STRING,std::string()}};

	int newline_holder = 0;
	bool insgq = false;
	bool indbq = false;
	bool backslash = false;
	string_t parenth;
	parenth.reserve(3);
	// while reading position is less than the size of holder minus the return character
	for (char i: s) {
		if (insgq) {
			bool just_setted_backslash = false;
			switch (i) {
			case '\'':
				if (!backslash) {
					insgq = false;
				}
				break;
			case '\\':
				backslash = true;
				just_setted_backslash = true;
				break;
			}
			if (backslash && !just_setted_backslash) {
				backslash = false;
			}
			ret[ret.size()-1].content += i;
		} else if (indbq) {
			bool just_setted_backslash = false;
			switch (i) {
			case '"':
				if (!backslash) {
					indbq = false;
				}
				break;
			case '\\':
				backslash = true;
				just_setted_backslash = true;
				break;
			}
			if (backslash && !just_setted_backslash) {
				backslash = false;
			}
			ret[ret.size()-1].content += i;
		} else if (parenth.size() > 0) {
			switch (i) {
			case '(':
			case '[':
			case '{':
				parenth += i;
				break;
			case ')':
				if (parenth[parenth.size()-1] == '(') {
					parenth.pop_back();
				} else {
					BracketsError(string_t("You're trying to close \"()\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case ']':
				if (parenth[parenth.size()-1] == '[') {
					parenth.pop_back();
				} else {
					BracketsError(string_t("You're trying to close \"[]\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case '}':
				if (parenth[parenth.size()-1] == '{') {
					parenth.pop_back();
				} else {
					BracketsError(string_t("You're trying to close \"{}\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case '\'':
				insgq = true;
				break;
			case '"':
				indbq = true;
				break;
			case '\n':
				newline_holder++;
				break;
			}
			ret[ret.size()-1].content += i;
		} else {
			switch (i) {
			case '(':
			case '[':
			case '{':
				parenth += i;
				ret[ret.size()-1].content += i;
				break;
			case '\'':
				insgq = true;
				ret[ret.size()-1].content += i;
				break;
			case '"':
				indbq = true;
				ret[ret.size()-1].content += i;
				break;
			case '\n': {
				LineObject copied = ret[ret.size()-1];
				ret[ret.size()-1] = LineObject{LO_NEW_LINE, ""};
				for (; newline_holder > 0; newline_holder--)
					ret.push_back({LO_NEW_LINE, ""});
				ret.push_back(copied);
			}
			case '\t':
				break;
			default:
				ret[ret.size()-1].content += i;
				break;
			}
		}
	}
	if (insgq) {
		SyntaxError("Single quote lefted without closing at the end of a line.");
	} else if (indbq) {
		SyntaxError("Double quote lefted without closing at the end of a line.");
	} else if (parenth.size() > 0) {
		BracketsError("You lefted a bracket or a parenthesis open.");
	}
	return ret;
}

list_t<string_t>& regroup_line(list_t<string_t>& ls) {
	//list_t<string_t> ret; 
	ls = cleanListOfString(ls);
	return ls;
}

std::regex re_indents("^\\s*");
list_t<string_t> splitLine(string_t s) {
	list_t<string_t> ret;
	if (s.size() == 0) {
		return ret;
	}
	ret.push_back("");
	s = std::regex_replace(s,re_indents, "");
	
	bool insgq = false;
	bool indbq = false;
	bool ksplit = false;
	bool backslash = false;
	string_t parenth;
	char old = '\x00';
	parenth.reserve(3);

	for (char i: s) {
		if (insgq) {
			bool just_setted_backslash = false;
			switch (i) {
			case '\'':
				if (!backslash) {
					insgq = false;
					ksplit = true;
				}
				break;
			case '\\':
				backslash = true;
				just_setted_backslash = true;
				break;
			}
			if (backslash && !just_setted_backslash) {
				backslash = false;
			}
			ret[ret.size()-1] += i;
		} else if (indbq) {
			bool just_setted_backslash = false;
			switch (i) {
			case '"':
				if (!backslash) {
					indbq = false;
					ksplit = true;
				}
				break;
			case '\\':
				backslash = true;
				just_setted_backslash = true;
				break;
			}
			if (backslash && !just_setted_backslash) {
				backslash = false;
			}
			ret[ret.size()-1] += i;
		} else if (parenth.size() > 0) {
			switch (i) {
			case '(':
			case '[':
			case '{':
				parenth += i;
				break;
			case ')':
				if (parenth.back() == '(') {
					parenth.pop_back();
					ksplit = true;
				} else {
					BracketsError(string_t("You're trying to close \"()\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case ']':
				if (parenth.back() == '[') {
					parenth.pop_back();
					ksplit = true;
				} else {
					BracketsError(string_t("You're trying to close \"[]\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case '}':
				if (parenth.back() == '{') {
					parenth.pop_back();
					ksplit = true;
				} else {
					BracketsError(string_t("You're trying to close \"{}\" brackets type, but ") + parenth[-1] + " is opened.");
				}
				break;
			case '\'':
				insgq = true;
				break;
			case '"':
				indbq = true;
				break;
			}
			ret.back() += i;
		} else {
			switch (i) {
			case '(':
			case '[':
			case '{':
				parenth += i;
				ret.push_back("");
				ret.back() += i;
				break;
			case '\'':
				insgq = true;
				ret.push_back("");
				ret.back() += i;
				break;
			case '"':
				indbq = true;
				ret.push_back("");
				ret.back() += i;
				break;

				default: {
					if (ksplit) {
						ret.push_back("");
						ret.back() += i;
					} else if (i == ' ') {
						if (old == ' ') {
							// Do nothing
						} else if (ret.back().size() != 0) {
							ret.push_back("");
						}
					} else if (is_namesyntax(ret.back()+i)) {
						ret.back() += i;
					} else {
						string_t s ="[" + ret.back() + "]\\b[";
						s += i;
						s += "]";
						std::regex re_bound_split(s);
						if (std::regex_match(ret.back()+i, re_bound_split)) {
							ret.push_back("");
							ret.back() += i;
						} else {
							ret.back() += i;
						}
					}
					break;
				}
			}
		}
		old = i;
	}
	ret = regroup_line(ret);
	return ret;
}

list_t<DefArg> sortOutDefArgs(string_t s) {
	// TODO: Add support for keywords.
	s = uncoverString(s);
	list_t<string_t> ls = splitLine(s);
	LOG_V(ls);
	//std::remove(ls.begin(), ls.end(), ",");
	size_t pos = 0;
	enum PHASES {TYPE, NAME, EQUAL_SIGN, VALUE};
	uint_fast8_t phase = PHASES::TYPE;
	list_t<DefArg> ret;
	context::FlaggedClass temp_type;
	string_t name;

	while (pos < ls.size()) {
		if (ls[pos] == ",") {
			if (phase != PHASES::TYPE)
				SyntaxError("");
				break;
		} else {
			switch (phase) {
			case PHASES::TYPE:
				temp_type = context::FlaggedClass(context::getTypeByName(ls[pos]), context::CurrentObject);
				phase = PHASES::NAME;
				break;
			case PHASES::NAME:
				name = ls[pos];
				if (ls[pos+1] == "=")
					phase = PHASES::EQUAL_SIGN;
				break;
			}
		}
		pos++;
	}
}

list_t<BaseElement> top_parser() {
	list_t<BaseElement> ret;
	for (LineObject i: splitText(readfile(rfile))) {
		LOG(i.content);
		if (i.flag == LO_SIMPLE_STRING) {
			nline++;
			list_t<string_t> spl = splitLine(i.content);
			LOG_V(spl);
			list_t<TokenIdString_Output> gout = parse(tokenize(spl));
			if (gout.size() == 0)
				continue;
			switch (gout[0].tis) {
			case TIS_KEYS::EXPR_FUNC_DECL:
				if (gout.size() > 1) {
					for (TokenIdString_Output j: gout) {
						std::cout << "TokenIdString_Output([";
						for (S_Token k: j.stokens) {
							std::cout << k.str << ", ";
						}
						std::cout << "], " << j.tis << ", " << j.pre_lvl << ")\n";
					}
					std::cout << std::flush;
					SyntaxError("Invalid syntax while declaring a function.");
				}/*
				if (context::CurrentObject) {
					context::CurrentObject->addToContext(context::Func(gout[0].stokens[1].str));
				} else {
					context::GLOBAL.push_back(context::Func(gout[0].stokens[1].str));
				}
				ret.push_back(FuncDecl(context::getTypeByName(gout[0].stokens[0].str), gout[0].stokens[1].str, {}, {}, {}, &context::getLastContextObject()));
				*/
			case TIS_KEYS::EXPR_MAIN_DECL:
				ret.push_back(FuncDecl(
					context::getTypeByName("int"),
					"main",
					sortOutDefArgs(gout[0].stokens[0].str),

				))
			}
			
		}
	}
	return ret;
}

void precompile() {

};

void compile(BaseElement element) {
	LOG("Passed element with class id: " << element.class_id);
};

void top_compiler() {
	for (BaseElement i: top_parser()) {
		LOG("top_compiler: " << i.class_id);
		compile(i);
	}
}

