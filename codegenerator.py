symbol_table = []
scope_stack = []

last_temp_address = 100

SS = []
PB = []
i = 0


def add_instruction_to_program_block(index, op, a1, a2='', r=''):
    global PB
    while len(PB) <= index:
        PB.append('')
    PB[index] = f'({op}, {a1}, {a2}, {r})'


def get_temporary_variables(count=1):
    global last_temp_address, i
    output = str(last_temp_address)
    for w in range(0, count):
        add_instruction_to_program_block(i, 'ASSIGN', '#0', str(last_temp_address))
        i += 1
        last_temp_address += 4
    return output


def initialize_identifier(id, type, attributes):
    global symbol_table
    if type == 'int':
        attributes = get_temporary_variables()
    elif type == 'array':
        attributes = get_temporary_variables(int(attributes))
    symbol_table.append((id, type, attributes))


def end_scope():
    global scope_stack, symbol_table
    top_value = scope_stack.pop()
    while top_value < len(symbol_table):
        symbol_table.pop()


def start_scope():
    global scope_stack, symbol_table
    scope_stack.append(len(symbol_table))


def find_identifier_address(id):
    global symbol_table
    for row in symbol_table:
        if id == row[0]:
            return row[2]


def generate_intermediate_code(action_type, current_token):
    global i, PB, SS

    if action_type == '#pid':
        p = find_identifier_address(current_token[1])
        SS.append(p)

    elif action_type == '#pnum':
        SS.append('#' + current_token[1])

    elif action_type == '#mult':
        t = get_temporary_variables()
        top = len(SS) - 1
        add_instruction_to_program_block(i, 'MULT', SS[top], SS[top - 1], t)
        i += 1
        SS.pop()
        SS.pop()
        SS.append(t)

    elif action_type == '#setvar':
        initialize_identifier(SS.pop(), 'int', "")

    elif action_type == '#setarr':
        size = SS.pop()
        initialize_identifier(SS.pop(), 'array', size[1:])

    elif action_type == '#assign':
        top = len(SS) - 1
        add_instruction_to_program_block(i, 'ASSIGN', SS[top], SS[top - 1])
        i += 1
        SS.pop()

    elif action_type == '#index':
        index = SS.pop()
        address = SS.pop()
        if index[0] == '#':
            SS.append(str(int(address) + 4 * int(index[1:])))
        else:
            t = get_temporary_variables()
            add_instruction_to_program_block(i, 'MULT', '#4', index, t)
            i += 1
            add_instruction_to_program_block(i, 'ADD', '#' + address, t, t)
            i += 1
            SS.append('@' + t)

    elif action_type == '#pop':
        SS.pop()
    elif action_type == '#saveinp':
        SS.append(current_token[1])


    elif action_type == '#opperation':
        second_op = SS.pop()
        op = SS.pop()
        first_op = SS.pop()
        t = get_temporary_variables()
        if op == '+':
            add_instruction_to_program_block(i, 'ADD', first_op, second_op, t)
        elif op == '-':
            add_instruction_to_program_block(i, 'SUB', first_op, second_op, t)
        elif op == '<':
            add_instruction_to_program_block(i, 'LT', first_op, second_op, t)
        elif op == '==':
            add_instruction_to_program_block(i, 'EQ', first_op, second_op, t)
        SS.append(t)
        i += 1

    elif action_type == '#signed':
        top_value = SS.pop()
        t = get_temporary_variables()
        add_instruction_to_program_block(i, 'SUB', '#0', top_value, t)
        i += 1
        SS.append(t)

    elif action_type == '#output_in':
        top_value = SS.pop()
        add_instruction_to_program_block(i, 'PRINT', top_value)
        i += 1
    elif action_type == '#save':
        SS.append(i)
        i += 1

    elif action_type == '#jpf_save':
        indx = SS.pop()
        exp = SS.pop()
        add_instruction_to_program_block(indx, 'JPF', exp, str(i + 1))
        SS.append(i)
        i += 1

    elif action_type == '#jp':
        indx = SS.pop()
        add_instruction_to_program_block(indx, 'JP', str(i))

    elif action_type == '#label':
        SS.append(str(i))

    elif action_type == '#while':
        indx = SS.pop()
        exp = SS.pop()
        add_instruction_to_program_block(indx, 'JPF', exp, str(i + 1))
        label = SS.pop()
        add_instruction_to_program_block(i, 'JP', label)
        i += 1

    elif action_type == '#startscope':
        start_scope()

    elif action_type == '#endscope':
        end_scope()


def save_code_gen():
    global PB
    output = open('output.txt', 'w')
    for i in range(0, len(PB)):
        output.write(f'{i}\t')
        output.write(f'{PB[i]}\n')
