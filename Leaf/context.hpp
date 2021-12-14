#pragma once
#include "errors.hpp"
#define ctx_osize sizeof(ContextObject)


typedef uchar class_flag_t;
#define TYPE_NORMAL		0b00000
#define TYPE_UNDEFINED	0b00000
#define TYPE_CONST 		0b00001
#define TYPE_PTR   		0b00010
#define TYPE_TEMPLATE	0b00100
#define TYPE_CARRAY		0b01000
#define TYPE_EXTEND		0b10000

namespace context {
	enum TID {
		CLASS,
		VAR,
		NMSP,
		FUNC,
		DYNAMIC // This is a constant value, like 0, 2, 3.14f or even "hello".
	};
	class ContextObject;

	list_t<ContextObject> GLOBAL;

	class ContextObject {
	public:
		list_t<ContextObject> ctx;
		ContextObject* parent;
		uchar object_id;
		bool isGlobal;
		ContextObject() {
			this->isGlobal = false;
		}
		ContextObject(bool isGlobal) {
			this->isGlobal = isGlobal;
		}

		virtual list_t<ContextObject> makeList() {
			list_t<ContextObject> ret(ctx.size());
			ret.insert(ret.cend(), this->ctx.cbegin(), this->ctx.cend());
			if (!isGlobal) {
				ret.insert(ret.cend(), GLOBAL.cbegin(), GLOBAL.cend());
			}
			return ret;
		}

		
		// virtual void setValue(string_t) {};
		
		virtual inline string_t getValue() {return "";};
		virtual inline string_t getName() {return "";};
		virtual inline void setName(string_t) {};
		void addToContext(ContextObject obj) {
			this->ctx.push_back(obj);
		};
		ContextObject* isInContext(ContextObject* obj) {
			if (obj > this->ctx.data() && obj < &(this->ctx.back())) {
				return obj;
			}
			return nullptr;
		};
		ContextObject* isInContext(string_t obj) {
			std::cout << "Avoid using ContextObject::isInContext pls." << std::endl;
			for (ContextObject& i: this->ctx) {
				if (i.getName() == obj) {
					return &i;
				}
			}
			return nullptr;
		};
		inline bool b_isInContext(ContextObject* obj) {
			if (this->isInContext(obj)) {
				return true;
			}
			return false;
		};
		inline bool b_isInContext(string_t obj) {
			if (this->isInContext(obj)) {
				return true;
			}
			return false;
		};
	};

	ContextObject* CurrentObject = nullptr;
	void addToCurrentContext(ContextObject obj) {
		if (CurrentObject) {
			CurrentObject->ctx.push_back(obj);
		} else {
			GLOBAL.push_back(obj);
		}
	}

	ContextObject& getLastContextObject() {
		if (CurrentObject) {
			return CurrentObject->ctx.back();
		}
		return GLOBAL.back();
	}

	string_t bakeContextName(ContextObject* obj, string_t lasting) {
		if (lasting.size() == 0)
			return bakeContextName(obj->parent, obj->getName());
		if (obj == nullptr) {
			// GLOBAL REACHED
			return lasting;
		}
		switch (obj->object_id) {

		case TID::DYNAMIC:
			return obj->getValue();

		case TID::NMSP:
		case TID::CLASS:
			return bakeContextName(obj->parent, obj->getName() + "::" + lasting);

		default:
			return bakeContextName(obj->parent, obj->getName() + ":" + lasting);
		}
	}

	class GarbageObject {};

	class Class : public ContextObject, public GarbageObject {
	public:
		string_t name;
		Class(string_t name, ContextObject* parent) : ContextObject(false), name(name) {
			this->object_id = TID::CLASS;
			this->parent = parent;
		};

		
		inline string_t getValue() {
			InternalError("Usage of Class::getValue() which isn't supposed to be called.");
			return "";
		}
		inline string_t getName() {
			return this->name;
		}
		inline void setName(string_t name) {
			this->name = name;
		}
	};

	class Constant : public ContextObject, public GarbageObject {
	public:
		Class* type;
		string_t value;
		Constant(Class* type, string_t value) : type(type), value(value) {}
		inline string_t getValue() {return this->value;}
	};

	class FlaggedClass : public Class {
	public:
		class_flag_t flags;
		FlaggedClass(Class* type, ContextObject* parent) : Class(type->name, type->parent) {
			this->flags = flags;
		}
		FlaggedClass() : Class("<undefined>", nullptr) {
			this->flags = TYPE_UNDEFINED;
		}
	};

	list_t<Class*> types;


	list_t<GarbageObject*> garbage_collection;
	void empty_garbage() {
		for (GarbageObject* i : garbage_collection) {
			delete i;
		}
	}

	inline GarbageObject* push_garbage(GarbageObject* garbage) {
		garbage_collection.push_back(garbage);
		return garbage;
	}

	Class* getTypeByName(string_t name) {
		for (Class* i: types) {
			if (i->getName() == name)
				return i;
		}
		NameError("Unknown type name " + name + ".");
		return nullptr;
	}

	class Func : public ContextObject {
	public:
		string_t name;
		Func(string_t name) {
			this->name = name;
			this->object_id = TID::FUNC;
		}
		inline string_t getName() {return this->name;};
		inline void setName(string_t) {this->name = name;};
	};
};