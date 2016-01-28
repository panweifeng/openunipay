import random


_NONCE_POPULATION = '123457890ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def generate_nonce_str(length):
    return ''.join(random.sample(_NONCE_POPULATION, length))