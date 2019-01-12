#!/usr/bin/python
'''
date    27.12.2018
ver     1.0
subs    Jupyter 4.4.0, ext. latex_envs
        Python 3.6.7
        LaTex 

Konverzia Jupyter notebookov na LaTex dokument
==============================================

Skript komnvertuje notebooku umiestnene v spolocnom adresari na *.tex
dokumenty v samostatnych adresaroch. 

Konfiguracia skriptu - je potrebne definovat
- source - cesta k notebookom 
- dest   - cesta, kam maju byt ulozene konvertovane subory 
- files  - pole s nazvami suborov notebookov, bez pripon
 
Postup konverzie
1. subor *.ipynb su skopirovane do samostatnych adresarov

2. v *.ipynb su expandovane testu v neviditelnych komentaroch
   <!---
   text napr. LaTex commands
   -->
3. subory *.ipynb su konvertovane na LaTex subory pomocou latex_nvs 

4. uprava *.tex suborov
   - odstranenie zahlavia
   - doplnenie inkludovania main.tex suboru s formatovanim textu
   - odstranenie zbytocnych komentarov
   - doplnenie explicitneho umiestnenia obrazkov
   
5. expanzia LaTex kodu generovaneho prikazom display(lx(..))
   umiestneneho v postupnosti prikazov
   \begin{verbatim}
   $ latex kod $
   \end{verbatim}
'''

#-----------------------------------------------------------------------
# Konfiguracia skriptu
#-----------------------------------------------------------------------
source = '/home/pf/ownCloud/Notebooks/Notebook-FDTD/'
dest = './'

files = [ '001_vseobecny_prehlad', 
          '002_skalarne_pole', 
          '003_vektorove_pole',
          '010_gradient',
          '011_divergencia',
          '012_rotacia',
          '015_krivkovy_integral',
          '016_gaussova_veta',
          '017_stokesova_veta',
          '110_meep_1d'
          ]

import re
import os
from shutil import copyfile

def filter_jpn_comment(s):
    '''
    Filter neviditelnych komentarov v subore notebooku 
    
    Funkcia prehlada subor *.ipynb v tvare retazca a nahradi postupnost
    <!---  text -->  obsahom komentara
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor
    '''
    return s

def filter_tex_verbatim(s):
    '''
    Filter vyrazov \begin{verbatim} $ latex kod $ \end{verbatim}
    
    Funcia sekvencne prehlada *.tex subor v tvare retazca a nahradi text 
    vyrazu textovou postupnostou
    \begin{equation} latex kod \end{equation}
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor  
    '''
    cmd = re.compile(r"\\begin\{verbatim\}\s*'\$(.*)\$'\s*\\end\{verbatim\}") #, s)
    offs = 10 
    while True:
        equ = cmd.search(s, offs)
        if equ is None:
            break

        (offs,k) = equ.span()        
        e = equ[1]
        e = e.replace(r'\\', "\\")
        repl=r'\begin{equation*}' +'\n' + \
             e + '\n' +\
             '\end{equation*}' + '\n'
        s = s.replace(equ[0], repl)
        #s = re.sub(equ[0], repl, s)
    return s


#-----------------------------------------------------------------------
# 1. Vytvorenie adresarov pre kazdy notebook a ich skopirovanie
#-----------------------------------------------------------------------
for f in files:
    if not os.path.exists(dest + f):
        os.makedirs(dest + f)
    
    copyfile(source + f + '.ipynb', dest + f +'/' +  f + '.ipynb')


#-----------------------------------------------------------------------
# 3.  Konverzia Jupyter -> LaTex
#-----------------------------------------------------------------------
print('Konverzia Jupyter - LaTex\n')
for f in files:
    s = 'jupyter nbconvert --to latex_with_lenvs ' 
    os.system(s + dest + f +'/' + f + '.ipynb')
    print()

#-----------------------------------------------------------------------
# 4. Uprava *tex zdrojovych suborov
#-----------------------------------------------------------------------
print('Uprava suborov LaTex\n')
for f in files:
    # otvorenie suboru
    name = dest + f +'/' + f + '.tex'
    fp = open(name, 'r')
    print(name)
    s=fp.read()
    fp.close()

    # vytrepanie somarin v zahlavi
    q = s.find(r'\begin{document}')
    s = (s[q:])

    # vytrepanie somarin zo zdrojoveho textu 
    s = s.replace(r'\maketitle', '')
    s = s.replace(r'\tableofcontents', '')
    s = s.replace('% Add a bibliography block to the postdoc', '')
    s = s.replace(r'%\bibliographystyle{ieetran}', '')
    s = s.replace(r'%\bibliography{Thesis}', '')
    s = s.replace('    \n', '')
    
    # explicitne umiestnenie obrazkov na poziciu [h!]
    s = s.replace(r'\begin{figure}', r'\begin{figure}[h!]')
    
    # oprava sympy vystupu, pre pandoc musi byt pouzity bez lx
    # from IPython.display import Latex as lx
    #s = s.replace('display((s))','display(lx(s))')

    # 5. Filter na expanziu LaTex vyrazov
    s = filter_tex_verbatim(s)
    
    s = s.replace(r'\section', r'\chapter')
    s = s.replace(r'\subsection', r'\section')

    # ulozenie konvertovaneho zdrojaku
    z=r'\documentclass[../main.tex]{subfiles}' + '\n'
    s = z + s
    fp = open(name, 'w')
    fp.write(s)
    fp.close()


