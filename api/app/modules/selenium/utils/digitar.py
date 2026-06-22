import time
import random

def digitar_como_humano(elemento, texto, delay_min=0.01, delay_max=0.03):
    elemento.clear()
    for letra in texto:
        elemento.send_keys(letra)
        time.sleep(random.uniform(delay_min, delay_max))
