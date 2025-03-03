# CFG-to-MG-algorithm
Supplement to paper.
Converts a categorized CFG into an MG.
Input: Categorized CFG = List of of rules.
Rule = 3-tuple (Non-Terminal, Word, Category), 
i.e. the Non-terminal can generate the word Word of category Category.
Capital letters are always interpretted as non-terminals here, minor letters as terminals.
Words are strings out of terminals and non-terminals.
Categories are strings that describe the type/category of a produced word.
S is the default start symbol.

Example for converting the following CFG:
S -> NV
N -> mouse
V -> WO
W -> eats
O -> cheese

cfg2mg([('S','NV','cSentence'),('N','mouse','cAnimal'),('V','WO','cVerbphrase'),('W','eats','cVerb'),('O','cheese','cFood')])
