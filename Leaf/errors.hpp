#pragma once
#include "glb.hpp"

#define SyntaxError(X) traceback("SyntaxError",X)
#define s_SyntaxError(X,Y) traceback("SyntaxError",X,Y)

#define NameError(X) traceback("NameError",X)
#define TypeError(X) traceback("TypeError",X)
#define ValueError(X) traceback("ValueError",X)
#define KeywordError(X) traceback("KeywordError",X)
#define ArgumentError(X) traceback("ArgumentError",X)
#define InternalError(X) traceback("InternalError",X)
#define BracketsError(X) traceback("BracketsError",X)




