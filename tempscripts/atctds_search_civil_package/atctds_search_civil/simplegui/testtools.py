import random as rd

def generate_tokens_secquence(length=5):
    alph = [chr(i) for i in range(97, 123, 1)]
    holder = []
    while length:
        holder.append(''.join(rd.choices(alph, k=rd.randint(3,7))).capitalize())
        length-=1
    return holder

gts = generate_tokens_secquence