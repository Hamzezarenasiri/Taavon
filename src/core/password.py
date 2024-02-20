import random
import string

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
symbols = string.punctuation
all_strings = lower + upper + num + symbols


def generate_random_password(length=8) -> str:
    return "".join(random.sample(all_strings, length))
