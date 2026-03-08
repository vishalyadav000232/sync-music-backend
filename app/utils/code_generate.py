import random
import string


def room_code_genrate()-> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits , k = 6))


