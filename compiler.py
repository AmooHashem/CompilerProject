# Seyyed Alireza Hashemi and Erfan Moeini

input = open('input.txt', 'r').read()
errors = open('lexical_errors.txt', 'a')
tokens = open('tokens.txt', 'a')
symbols = open('symbol_table.txt', 'a')
input_size = len(input)
iterator = 0
last_lines = [0, 0, 0]
lineno = 1
all_IDS_or_KEYWORDS = []
WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
SYMBOL = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']
KEYWORD = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', ]
ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
COMMENT = ['/']
DIGIT = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
VALID_CHARACTERS = WHITESPACES + SYMBOL + ALPHABET + DIGIT + COMMENT


###############################


def get_char():
    global iterator, input_size, input
    if iterator == input_size:
        return 'EOF'
    iterator += 1
    return input[iterator - 1]


def star_char():
    global iterator
    iterator -= 1


def handle_whitespace(white_space):
    global lineno
    if white_space == '\n':
        lineno += 1


def handle_keyword_and_id(char):
    global ALPHABET, DIGIT, KEYWORD, VALID_CHARACTERS
    keyword_or_id = ''
    while char in ALPHABET or char in DIGIT:
        keyword_or_id += char
        char = get_char()

    if not char in VALID_CHARACTERS:
        keyword_or_id += char
        return 'error', 'Invalid input', keyword_or_id,

    star_char()
    if keyword_or_id in KEYWORD:
        return 'KEYWORD', keyword_or_id
    else:
        return 'ID', keyword_or_id


def handle_symbol(char):
    global SYMBOL, VALID_CHARACTERS
    if char != '=' and char != '*':
        return 'SYMBOL', char

    if char == '=':
        char = get_char()
        if char == '=':
            return 'SYMBOL', '=='
        if not char in VALID_CHARACTERS:
            return 'error', 'Invalid input', '=' + char
        star_char()
        return 'SYMBOL', '='

    if char == '*':
        char = get_char()
        if not char in VALID_CHARACTERS:
            return 'error', 'Invalid input', '*' + char
        if char == '/':
            return 'error', 'Unmatched comment', '*' + char
        star_char()
        return 'SYMBOL', '*'


def handle_digit(char):
    global DIGIT, ALPHABET, VALID_CHARACTERS
    number = ''
    while char in DIGIT:
        number += char
        char = get_char()
    if char in ALPHABET:
        number += char
        return 'error', 'Invalid number', number
    if not char in VALID_CHARACTERS:
        number += char
        return 'error', 'Invalid input', number
    star_char()
    return 'NUM', number


def handle_comment(char):
    char = get_char()
    if char == '/':
        char = get_char()
        while char != '\n':
            char = get_char()
        star_char()
        return
    if char == '*':
        char = get_char()
        comment = ''
        while char != 'EOF':
            comment += char
            if len(comment) >= 2 and comment[len(comment) - 2:] == '*/':
                return
            char = get_char()
        return 'error', 'Unclosed comment', '/*' + comment[0:min(5, len(comment) -1)] + '...'

    star_char()
    return 'error', 'Invalid input', '/'


def handle_invalid_input(char):
    return 'error', 'Invalid input', char


def get_next_token(char):
    token = ''
    if char in WHITESPACES:
        handle_whitespace(char)
    elif char in ALPHABET:
        token = handle_keyword_and_id(char)
    elif char in SYMBOL:
        token = handle_symbol(char)
    elif char in DIGIT:
        token = handle_digit(char)
    elif char in COMMENT:
        token = handle_comment(char)
    else:
        token = handle_invalid_input(char)

    return token

###############################

def handle_next_line(index, lineno, writer):
    global last_lines
    if lineno != last_lines[index]:
        if last_lines[index] != 0:
            writer.write('\n')
        last_lines[index] = lineno
        writer.write(f'{lineno}.\t')
        return True
    return False

def handle_space(is_needed, writer):
    if is_needed:
        writer.write(f' ')    
                

errors.truncate(0)
tokens.truncate(0)
symbols.truncate(0)

if __name__ == '__main__':
    there_is_lexical_errors = False
    char = get_char()
    while char != 'EOF':
        token = get_next_token(char)
        if token:
            if token[0] == 'error':
                is_new_line = handle_next_line(0, lineno, errors)
                handle_space(not is_new_line, errors)
                errors.write(f'({token[2]}, {token[1]})')
                there_is_lexical_errors = True
            if token[0] != 'error':
                is_new_line = handle_next_line(1, lineno, tokens)
                handle_space(not is_new_line, tokens)
                tokens.write(f'({token[0]}, {token[1]})')
            if token[0] == 'ID' or token[0] == 'KEYWORD':
                if not token[1] in all_IDS_or_KEYWORDS:
                    all_IDS_or_KEYWORDS.append(token[1])
                    handle_next_line(2, len(all_IDS_or_KEYWORDS), symbols)
                    symbols.write(f'{token[1]}')
        char = get_char()

    if not there_is_lexical_errors:
        errors.write(f'There is no lexical error.')

    for keyword in KEYWORD:
        if not keyword in all_IDS_or_KEYWORDS:
            all_IDS_or_KEYWORDS.append(keyword)
            handle_next_line(2, len(all_IDS_or_KEYWORDS), symbols)
            symbols.write(f'{keyword}')
