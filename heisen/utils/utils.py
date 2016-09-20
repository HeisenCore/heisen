import string
import random


def unique_id(len=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for i in range(len))
