
#!/usr/bin/env python
import msvcrt
import os

os.system('cls')
while True:
    print('Press key [combination] (Kill console to quit): ', end='', flush=True)
    key = msvcrt.getwch()
    num = ord(key)
    if num in (0, 224):
        ext = msvcrt.getwch()
        print(f'prefix: {num}   -   key: {ext!r}   -   unicode: {ord(ext)}')
    else:
        print(f'key: {key!r}   -   unicode: {ord(key)}')