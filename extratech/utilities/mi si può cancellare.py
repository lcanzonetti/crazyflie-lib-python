
 

def assegna_BIT_a_lista(numero):
    motori = [1,1,1,1]
    motori[0] = (numero >> 3) & 1
    motori[1] = (numero >> 2) & 1
    motori[2] = (numero >> 1) & 1
    motori[3] = (numero >> 0) & 1
    return motori

GINO  = True
CARLO = True

def ginnico(chiVoglioAssertare):
    assert(chiVoglioAssertare)
    print("%s è ginnico" % chiVoglioAssertare)


def sonoGinnici():
    try:
        ginnico(GINO)
        ginnico(CARLO)
    except AssertionError:
        print('non sono tutti ginnici')
    print('sono tutti ginnici')
sonoGinnici()