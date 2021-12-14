import glb

def traceback(title,description,syntax=None,__cdescr__="<incorrect call description>"):
	# No error rescue with "try" for now !
	print(title)
	print(f"\tIn file:\n\t{glb.rfile}")
	print(f"\tInfo:\n\t{description}")
	if syntax:
		print(f"\tSyntax:\n\t{syntax}")
	if glb.READING_NLINE!=None:
		buf = f": traceback({title})"
		print(f"\tText:\n\t {glb.readline(glb.READING_NLINE,__cdescr__ + buf)}")
		print(f"\tAt line: {glb.READING_NLINE}")
	print("DEBUG : ",__cdescr__)
	exit(1)

def warning(title,description, __cdescr__="<incorrect call description>"):
	# No error rescue with "try" for now !
	print(title)
	print(f"\tIn file:\n\t{glb.rfile}")
	print(f"\tInfo:\n\t {description}")
	if glb.READING_NLINE!=None:
		buf = f": wrning({title})"
		print(f"\tText:\n\t {glb.readline(glb.READING_NLINE,__cdescr__ + buf)}")
		print(f"\tAt line: {glb.READING_NLINE}")


"""
NOTE:

Erreur avec ["const int", "b", "=", "(a)"]
J'essaye de régler le problème de l'affichage du text de l'erreur, ça n'affiche pas la bonne ligne (2 lignes avant)
Regarde mon programme "test.lf" dans sublime text et regarde l'erreur de la console:

NameError
        In file:
        ./ex/test.lf
        Info:
        Unknown object "b".
        Text:
         main() {     <<< Là ça devrait afficher ça : 	print("%i\n",b)

        At line: 7


"""

