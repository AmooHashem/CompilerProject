symbol_table = []
scope_stack = []

last_temp_address = 100

SS = []
PB = []
i = 0
breaklist = []
returnlist = []


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


def initialize_variable(id, type, attributes):
    global symbol_table, i
    if type == 'int':
        address = get_temporary_variables()
    elif type == 'array':
        address = get_temporary_variables()
        array = get_temporary_variables(int(attributes))
        add_instruction_to_program_block(i, 'ASSIGN', f'#{array}', address)
        i += 1
    symbol_table.append((id, type, address))


def end_scope():
    global scope_stack, symbol_table
    top_value = scope_stack.pop()
    while top_value < len(symbol_table):
        symbol_table.pop()


def start_scope():
    global scope_stack, symbol_table
    scope_stack.append(len(symbol_table))


def find_identifier_address(id):
    if id == 'output':
        return 'output'
    global symbol_table
    for row in symbol_table:
        if id == row[0]:
            return row[2]


def generate_intermediate_code(action_type, current_token):
    global i, PB, SS, breaklist, returnlist

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
        initialize_variable(SS.pop(), 'int', "")

    elif action_type == '#setarr':
        size = SS.pop()
        initialize_variable(SS.pop(), 'array', size[1:])

    elif action_type == '#assign':
        top = len(SS) - 1
        add_instruction_to_program_block(i, 'ASSIGN', SS[top], SS[top - 1])
        i += 1
        SS.pop()

    elif action_type == '#index':
        print(SS)
        print(":::::::::::::::::::::::::")
        index = SS.pop()
        address = SS.pop()

        t1 = get_temporary_variables()
        add_instruction_to_program_block(i, 'MULT', '#4', index, t1)
        i += 1
        t2 = get_temporary_variables()
        add_instruction_to_program_block(i, 'ASSIGN', f'@{address}', t2)
        i += 1
        add_instruction_to_program_block(i, 'ADD', t2, t1, t1)
        i += 1
        SS.append('@' + t1)

    elif action_type == '#pop':
        SS.pop()

    elif action_type == '#saveinp':
        SS.append(current_token[1])

    elif action_type == '#opperation':
        second_operand = SS.pop()
        operator = SS.pop()
        first_operand = SS.pop()
        t = get_temporary_variables()
        if operator == '+':
            add_instruction_to_program_block(i, 'ADD', first_operand, second_operand, t)
        elif operator == '-':
            add_instruction_to_program_block(i, 'SUB', first_operand, second_operand, t)
        elif operator == '<':
            add_instruction_to_program_block(i, 'LT', first_operand, second_operand, t)
        elif operator == '==':
            add_instruction_to_program_block(i, 'EQ', first_operand, second_operand, t)
        SS.append(t)
        i += 1

    elif action_type == '#signed':
        top_value = SS.pop()
        t = get_temporary_variables()
        add_instruction_to_program_block(i, 'SUB', '#0', top_value, t)
        i += 1
        SS.append(t)

    elif action_type == '#output_in':
        if SS[len(SS) - 2] != 'output':
            return
        top_value = SS.pop()
        add_instruction_to_program_block(i, 'PRINT', top_value)
        i += 1

    elif action_type == '#save':
        SS.append(i)
        i += 1

    elif action_type == '#jpf_save':
        index = SS.pop()
        expression = SS.pop()
        add_instruction_to_program_block(index, 'JPF', expression, str(i + 1))
        SS.append(i)
        i += 1

    elif action_type == '#jp':
        index = SS.pop()
        add_instruction_to_program_block(int(index), 'JP', i)

    elif action_type == '#label':
        SS.append(i)

    elif action_type == '#numeric_label':
        SS.append(f'#{i}')

    elif action_type == '#while':
        index = SS.pop()
        expression = SS.pop()
        add_instruction_to_program_block(index, 'JPF', expression, str(i + 1))
        label = SS.pop()
        add_instruction_to_program_block(i, 'JP', label)
        i += 1

    elif action_type == '#startscope':
        start_scope()

    elif action_type == '#endscope':
        end_scope()

    elif action_type == '#startswitch':
        caselist = []
        accept = get_temporary_variables()
        SS.append(caselist)
        SS.append(accept)

    elif action_type == '#case':
        t = get_temporary_variables()
        num = SS.pop()
        accept = SS[len(SS) - 2]
        x = SS[len(SS) - 1]
        j = i
        add_instruction_to_program_block(i, 'SUB', x, num, t)
        i += 1
        add_instruction_to_program_block(i, 'EQ', t, '#0', t)
        i += 1
        add_instruction_to_program_block(i, 'ADD', t, accept, t)
        i += 1
        add_instruction_to_program_block(i, 'LT', '#0', t, accept)
        i += 1
        SS[len(SS) - 3].append((i, j))
        i += 1

    elif action_type == '#casedefualt':
        accept = SS[len(SS) - 2]
        j = i
        add_instruction_to_program_block(i, 'ASSIGN', '#1', accept)
        i += 1
        SS[len(SS) - 3].append((i, j))
        i += 1

    elif action_type == '#endswitch':
        x = SS.pop()
        accept = SS.pop()
        caselist = SS.pop()
        caselist.append((0, i))
        for j in range(0, len(caselist) - 1):
            add_instruction_to_program_block(caselist[j][0], 'JPF', accept, str(caselist[j + 1][1]))

    elif action_type == '#start_symbol':
        symbol_table.append('STOP')

    elif action_type == '#add_function_to_symbol_table':  # todo: make cleaner
        length = len(SS)
        attributes = []
        function_name = SS[length - 4]
        last_object_of_symbol_table = symbol_table.pop()
        while last_object_of_symbol_table != 'STOP':
            attributes.append(last_object_of_symbol_table[2])
            last_object_of_symbol_table = symbol_table.pop()
        attributes.append(SS[length - 3])
        attributes.reverse()
        attributes.append(SS[length - 2])
        attributes.append(SS[length - 1])
        symbol_table.append((function_name, 'function', attributes))
        SS.pop()
        SS.pop()
        SS.pop()
        SS.pop()

    elif action_type == '#init_variable':
        address = get_temporary_variables()
        SS.append(address)

    elif action_type == '#return_address':
        if SS[len(SS) - 4] == 'main':
            return
        return_value = SS[len(SS) - 2]
        add_instruction_to_program_block(i, 'JP', f'@{return_value}')
        i = i + 1

    elif action_type == '#break':
        breaklist.append(i)
        i += 1

    elif action_type == '#startbreak':
        breaklist.append("start")

    elif action_type == '#endbreak':
        index = breaklist.pop()
        while index != 'start':
            add_instruction_to_program_block(index, 'JP', i)
            index = breaklist.pop()

    elif action_type == '#return':
        value = SS.pop()
        returnlist.append((i, value))
        i += 2

    elif action_type == '#startreturn':
        returnlist.append(("start", '#0'))

    elif action_type == '#endreturn':
        index = returnlist.pop()
        while index[0] != 'start':
            add_instruction_to_program_block(index[0], 'ASSIGN', index[1], SS[len(SS) - 1])
            add_instruction_to_program_block(index[0] + 1, 'JP', i)
            index = returnlist.pop()

    elif action_type == '#call_function':  # todo: make cleaner
        if SS[len(SS) - 1] == 'output':
            return
        function_attributes = []
        for j in range(len(SS) - 1, -1, -1):
            if isinstance(SS[j], list):
                function_attributes = SS[j]
        input_size = len(function_attributes) - 3
        # assign function inputs
        for j in range(input_size):
            add_instruction_to_program_block(i, 'ASSIGN', SS[len(SS) - input_size + j], function_attributes[j + 1])
            i = i + 1
        # assign return address
        add_instruction_to_program_block(i, 'ASSIGN', f'#{i + 2}', function_attributes[input_size + 1])
        i = i + 1
        # go  to function
        add_instruction_to_program_block(i, 'JP', function_attributes[0] + 1)
        i = i + 1
        for j in range(input_size + 1):
            SS.pop()
        # create a new variable and assign function output to it
        address = get_temporary_variables()
        SS.append(address)
        add_instruction_to_program_block(i, 'ASSIGN', function_attributes[input_size + 2], address)
        i = i + 1

    elif action_type == '#special_save':
        top = SS.pop()
        SS.append(i)
        SS.append(top)
        i += 1

    elif action_type == '#special_save_pair':
        if symbol_table[len(symbol_table) - 1][0] == 'main':
            t = get_temporary_variables()
            add_instruction_to_program_block(SS.pop(), 'ADD', '#0', '#0', t)
            i += 1
        else:
            add_instruction_to_program_block(SS.pop(), 'JP', i)

    print(SS)
    print(symbol_table)
    print(action_type)
    print()


def save_code_gen():
    global PB
    output = open('output.txt', 'w')
    for i in range(0, len(PB)):
        output.write(f'{i}\t{PB[i]}\n')
