# -*-coding:Latin-1 -*

import pickle
import os
import math
from random import randrange
from Modules.ModAff import SavePrint
during = str()
a=0
b=0
c=0
d = int()
print("Bienvenu � Zcasino !")
print("0 : charger une sauvegarde \nAutre touche : nouvelle partie")
start= input("")
if start == "0" :
    SavePrint()
    saveload = input("Saisir nom de la sauvegarde � charger: ")
    with open("multisave_save/{}".format(saveload), "rb") as fichier :
        my = pickle.Unpickler(fichier)
        d = my.load()
else :
    d=1000

while during != "0" and d > 0 : #boucle globale
    during = str()
    a = str()
    while a != "settings" and d>0: #boucle, arr�te quand le joueur n'a plus d'argent
        
        print("vous avez ",d, "$") #argent actuel
        
        a = input("Numero sur lequel parier (tapez settings pour ouvrir les options) : ") #num�ro
        if a== "settings" :
            print()
        else :
            a= int(a)
            if a>49 or a<0 : #test de convenabilit� du num�ro
                print("le num�ro doit �tre compris entre 0 et 49 inclus") #erreur sur ce test, vers fin de boucle
            else : #aucune erreur , continuation du programme
                
                b = int(input("Mise : ")) #Mise
                if b>d or b<0: #test de convenabilit� de la mise
                    print("La mise ne doit pas �tre sup�rieure � votre argent, ni inferieur � 0") #erreur sur ce test, vers fin du programme  
                else :    #aucune erreur, continuation du programme
                    
                    c = randrange(50) #al�a
            
                    print("le num�ro est : ",c) #affichage du num�ro gagnant
            
                    if c == a : #prime 25x
                        d += b*25
                        print("vous avez gagn� ",b*25, "$")
                        
                    elif a % 2 == c % 2 : #prime 1,5
                            d += math.ceil(b / 2)
                            print("vous avez gagn�", math.ceil(b/2), "$")
                            
                    else : #perdu
                        d -= b
                        print("vous avez perdu", b, "$")
                    
    
    if d>0 :
        print("0 : Sauvegarder et quitter\n1 : Renommer Sauvegarde\n2 : Liste des Sauvegardes\n3 : Supprimer une sauvegarede\n4 : Reprendre")
    while during !="0" and d>0 and during != "4":                                                    #boucle, arr�te (3), (0) et d =0
        during= input("")
        if during == "1" :                                                  #Rename (1)
            SavePrint()
            old_name=input("Saisir sauvegarde � renommer : ")
            new_name=input("Saisir le nouveau nom : ")
            try :
                os.rename("multisave_save/{}".format(old_name),"multisave_save/{}".format(new_name))
                print("Fichier renomm� avec succ�s")
            except OSError as e :
                print("Erreur : {} - {}.".format(e.filename, e.strerror))
        if during == "2" :                                                  #Affichage (2)
            SavePrint()
        if during == "help":
            print("0 : Sauvegarder et quitter\n1 : Renommer Sauvegarde\n2 : Liste des Sauvegardes\n3 : Reprendre")
        if during =="3" :
            SavePrint()
            delet = input("Saisir sauvegarde � supprimer : ")
            try :
                os.remove("multisave_save/{}".format(delet))
                print("Fichier supprim� avec succ�s")
            except OSError as e:
                print("Erreur : {} - {}.".format(e.filename, e.strerror))


if during =="0" :
    SavePrint()                                                         #Affichage
    saveA = str(input("Saisir nom de la sauvegarde : "))                #Sauvegarde (0)
    with open("multisave_save/{}".format(saveA), "wb") as fichier :
        my = pickle.Pickler(fichier)
        my.dump(d)
else :
    print("Vous n'avez plus d'argent !")
    os.system("pause")
