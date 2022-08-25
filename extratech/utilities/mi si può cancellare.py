import sys

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
# sonoGinnici()


# quattro = "2022"
# quattrobittico = quattro.encode('raw_unicode')
# # quattro = bytes(34567831)
# print(quattrobittico)

# n = 2
# baitti                = [quattro[i:i+n] for i in range(0, len(quattro), n)]
# baitti_ribaittificati = [int(baitto) for baitto in baitti]
# baitti_decodificati   = [baitto.decode('utf-8') for baitto in baitti]
# # print(baitti)
# print(baitti_decodificati)
# # print(baitti_interificati)


# l1 = quattrobittico.decode('utf-8')


# l1 = quattro.decode('utf-8').split()[2:]  # Initial decode
# print (l1)
# #  slice out the embedded byte string "b'  '" characters
# l1_string = ''.join([x[:-2] if x[0] != 'b' else x[2:] for x in l1])
# l1_bytes = l1_string.encode('utf-8')
# l1_final = l1_bytes.decode('utf-8')

# print('Results')
# print(f'l1_string is {l1_string}')
# print(f'l1_bytes is {l1_bytes}')
# print(f'l1_final is {l1_final}')


number = 32424234

import struct
result = struct.pack("I", number)
# print (result)

f = [2,0,2,4]

fb = struct.pack("I", f)

fbd = struct.unpack("I", fb)

print (fbd)
