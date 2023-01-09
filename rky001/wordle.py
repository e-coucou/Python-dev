import numpy as np
# import pandas as pd
from tqdm import tqdm as ProgressDisplay
import math
import json, os

mots_array = []
def convert_array_mot(arr):
    return np.array([''.join(chr(e) for e in ligne )for ligne in arr])
def convert_mot_array(mots):
    return np.array([[ord(c)for c in w] for w in mots], dtype=np.uint8)

def log2_(val,div):
    return math.log2(div/val) if val >0 else 0

def make_pattern(p=5):
    pattern=[]
    for k in range(pow(3,5)):
        if (k<1):
            pattern.append(np.base_repr(k,3,5))
        elif (k<3):
            pattern.append(np.base_repr(k,3,4))
        elif (k<9):
            pattern.append(np.base_repr(k,3,3))
        elif (k<27):
            pattern.append(np.base_repr(k,3,2))
        elif (k<81):
            pattern.append(np.base_repr(k,3,1))
        else:
            pattern.append(np.base_repr(k,3))
    return pattern

# Algo principal
def check_mot_pattern(check,pattern,M=mots_array.copy(),k=5):
    E=[] #2
    I=[] #1
    O=[] #0
    Il = dict()
    It = dict()
    for i in range(k):
        p=pattern[i]
        try:
            It[check[i]] += 1
        except:
            It[check[i]] = 1
        if (p=='0'):
            a = np.array((int(i) ,int(ord(check[i]))), dtype=np.uint8) # np.int16)
            O = np.append(O,a,axis=0)
            # It[check[i]] -= 1;
        elif (p=='1'):
            I.append([i, ord(check[i])])
            try:
                Il[check[i]] += 1
            except:
                Il[check[i]] = 1
        elif (p=='2'):
            E.append([i, ord(check[i])])
            # It[check[i]] -= 1;
    # On élimine les (2)
    T = np.array([0,1,2,3,4])
    for i in E:
        M = M[(M[:,i[0]] == i[1])]
        T = T[T[:] != i[0]]
    # on elimne 
    try:
        dO = int(O.shape[0] / 2)
        if (dO>0):
            O = O.reshape(dO,2)
        for j in O:
            M = M[(M[:,int(j[0])] != int(j[1]))]
        # for i in E: 
        #     O = O[(O[:,1] != i[1])]
        for i in I:
            O = O[(O[:,1] != i[1])]
    except:
        a=0
    # print(T)
    # print('elim 0 en place',M.shape,convert_array_mot(M) )
    for i in O:
        P = (np.sum(M[:,T] == i[1],axis=1)).reshape((1,M.shape[0]))
        M = np.insert(M,0,P,axis=1)
        M = M[(M[:,0] == 0)]
        M = np.delete(M,0,axis=1)
    # print('0 elim',M.shape,convert_array_mot(M) )
    # print(I,Il)
    for i in I:
        M = M[~(M[:,i[0]] == i[1])] # on elimine la bonne postion
    # print('1 elim',M.shape,convert_array_mot(M) )
    # print(T)
    # print('O',O,'I',I,'E',E,Il,It)
    if (len(I)>0):
        for i in Il:
            if (It[i]>Il[i]):
                a = (np.sum(M[:,T]==ord(i),axis=1) == Il[i])
            else:
                a = (np.sum(M[:,T]==ord(i),axis=1) >= Il[i])
            M = np.insert(M,0,a,axis=1)
            M = M[(M[:,0] == True)]
            M = np.delete(M,0,axis=1)
            # print('elim',i,M.shape,convert_array_mot(M) )
    return M, len(M)

# Calcul de l'entropy
def entropie_mot(check, M=mots_array.copy(), debug=False):
    dim = M.shape[0]
    e_sum=0
    e_pattern=[]
    pattern = make_pattern(5)
    for p in pattern:
        ret, nb = check_mot_pattern(check,p,M)
        e = log2_(nb,dim)
        e_pattern.append(e)
        e_sum = e_sum + e*nb/dim
        if (debug):
            print(f'{nb:5} {p:7} {dim:4} {">":->6} {e:=2.4f} {e_sum:2.4f} {e*nb/dim:2.4f}')
    return e_sum,e_pattern


def conseil(check,pattern,M=mots_array.copy()):
    ret, nb = check_mot_pattern(check,pattern,M)
    E = -log2_(nb,M.shape[0])
    new_liste = convert_array_mot(ret)
    # print(nb, E)
    new_entropie = {}
    for mot in ProgressDisplay(new_liste):
        new_entropie[mot] = entropie_mot(mot,ret)
    # print(f'Test : {new_entropie}')
    return(list(new_entropie))


#-----------------------

print(os.getcwd())
# os.chdir("rky001")
# mots_sc = pd.read_table("mots.txt",header=None) #version science etonnante
f = open('mots_off.json')
mots = json.load(f) #officielle depuis loane
f.close()
# words = pd.read_json("wordle_us.json")
mots_array = np.array(convert_mot_array(mots.copy()))
# print('les mots',mots_array)
# mat, n = check_mot_pattern('ETETA','20210',mots_array.copy())
# print(n,convert_array_mot(mat))
# reponse = conseil('AIRES','01200',mots_array.copy())
# print(reponse)
run = True
rep = mots.copy()
# print(convert_array_mot(rep))
while run:
    mot = input('proposition  : ').upper()
    if len(mot)==5:
        pattern = input('pattern  : ')
        rep = conseil(mot,pattern,convert_mot_array(rep))
        print('r',rep)
    else:
        run = False