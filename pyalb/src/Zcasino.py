# -*-coding:Latin-1 -*
import math
from random import randrange

b=0
d=40 #argent

while d != 0 :
    print("vous avez ",d, "$")
    a = int(input("Numero sur lequel parier : ")) #num    
    b = int(input("Mise : ")) #Mise
    if b>d :
        print("Mise sup�rieure � votre argent")
    else :    
        c = randrange(50) #al�a

        print("le num�ro est : ",c)

        if c == a :
            d += b
            print("vous avez gagn� ",b, "$")
        elif a % 2 == c % 2 :
                d += math.ceil(b / 2)
                print("vous avez gagn�", math.ceil(b/2), "$")
        else :
            d -= b
            print("vous avez perdu", b, "$")
            
print("Vous n'avez plus d'argent !")