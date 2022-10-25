import sys

def IDFromURI(uri):
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        # print(int(address, 16) - 996028180448)
        return int(address, 16) - 996028180448
    except ValueError:
        print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
        return None


def convert_motor_pass(numeroBinario):
    motori = [1,1,1,1]
    motori[0] = (numeroBinario >> 3) & 1
    motori[1] = (numeroBinario >> 2) & 1
    motori[2] = (numeroBinario >> 1) & 1
    motori[3] = (numeroBinario >> 0) & 1
    return motori

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)
"""

500 p/s

logs =   10
gotos =  20
rgbs  =  10
 
"""