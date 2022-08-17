
 

def assegna_BIT_a_lista(numero):
    motori = [1,1,1,1]
    motori[0] = (numero >> 3) & 1
    motori[1] = (numero >> 2) & 1
    motori[2] = (numero >> 1) & 1
    motori[3] = (numero >> 0) & 1
    return motori

print(assegna_BIT_a_lista(1))
print(assegna_BIT_a_lista(4))
print(assegna_BIT_a_lista(17))