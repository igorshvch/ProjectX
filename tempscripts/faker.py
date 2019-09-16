import random as rd

alph_options = {
    'capital': [chr(i) for i in range(1040, 1071)],
    'lower': [chr(i) for i in range(1072, 1104)],
    'mixed': (
        [chr(i) for i in range(1040, 1071)]
        + [chr(i) for i in range(1072, 1104)]
    )
}


def create_fake_string_with_fixed_length(length, char_t='mixed'):
    return ''.join(rd.choices(alph_options[char_t], k=length))

def fake_string_with_fixed_length_gen(quant, length, char_t='mixed'):
    char_set = alph_options[char_t]
    def inner_func(length, char_set):
        return ''.join(rd.choices(char_set, k=length))
    while quant:
        yield inner_func(length, char_set)
        quant -= 1


def create_fake_string_with_arb_length(len_b=10, char_t='mixed'):
    return ''.join(rd.choices(alph_options[char_t], k=rd.randint(1, len_b)))

def fake_string_with_arb_length_gen(quant, len_b=10, char_t='mixed'):
    char_set = alph_options[char_t]
    def inner_func(len_b, char_set):
        return ''.join(rd.choices(char_set, k=rd.randint(1, len_b)))
    while quant:
        yield inner_func(len_b, char_set)
        quant -= 1