
CLASS_ANYUSE        = 0b111111111111111
CLASS_INHERITED     = 0b000000000000001
CLASS_PTR			= 0b000000000000010
CLASS_SIZEOF_USAGE	= 0b000000000000100
CLASS_CONST			= 0b000000000001000
CLASS_STATIC		= 0b000000000010000
CLASS_NONSTATIC		= 0b000000000100000
CLASS_PRIVATE		= 0b000000001000000 # Private when including, let you use a structure and show void* to the user.
CLASS_C_ARRAY		= 0b000000010000000

"""
How does that work ?

CLASS_PTR | CLASS_STATIC
	=> This class can be used only when being declared as a pointer and as static.

CLASS_ANYUSE & ~CLASS_PTR
	=> You can't create a pointer of instance of this class.

CLASS_ANYUSE & ~(CLASS_STATIC|CLASS_NONSTATIC)
	=> You can't declare an instance of this class.
		Usage:
			Inheritor only classes.

"""










