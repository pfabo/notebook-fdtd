from IPython.display import *
from IPython.display import Latex as lx
from sympy import latex

def ltxprint(var, value):   
    # pomocna funkcia pre formatovanu tlac premennych
    s = '$' + latex(var) + '=' + latex(value) + '$'
    #display(lx(s))
    display(s)
