symbol_table = []
scope_stack = []

last_temp_address = 100

gstack = []
PB = []
i = 0


def add_block(indx, op, a1, a2="", r=""):
    global PB
    while len(PB) <= indx:
        PB.append("")
    PB[indx] = "(" + op + ', ' + a1 + ', ' + a2 + ', ' + r + ')'


def gettemp(size=1):
    global last_temp_address, i
    output = str(last_temp_address)
    for w in range(0, size):
        add_block(i, 'ASSIGN', '#0', str(last_temp_address))
        i += 1
        last_temp_address += 4
    return output


def add_variable(lexeme, typ, attributes):
    global symbol_table
    if typ == 'int':
        attributes = gettemp()
    elif typ == 'array':
        attributes = gettemp(int(attributes))
    symbol_table.append((lexeme, typ, attributes))


def end_scope():
    global scope_stack, symbol_table
    top_value = scope_stack.pop()
    while top_value < len(symbol_table):
        symbol_table.pop()


def start_scope():
    global scope_stack, symbol_table
    scope_stack.append(len(symbol_table))


def findaddr(id):
    global symbol_table
    for row in symbol_table:
        if id == row[0]:
            return row[2]


def code_gen(action, current_token):
    global i, PB, gstack

    if action == '#pid':
        p = findaddr(current_token[1])
        gstack.append(p)

    elif action == '#pnum':
        gstack.append('#' + current_token[1])

    elif action == '#mult':
        t = gettemp()
        top = len(gstack) - 1
        add_block(i, 'MULT', gstack[top], gstack[top - 1], t)
        i += 1
        gstack.pop()
        gstack.pop()
        gstack.append(t)

    elif action == '#setvar':
        add_variable(gstack.pop(), 'int', "")

    elif action == '#setarr':
        size = gstack.pop()
        add_variable(gstack.pop(), 'array', size[1:])

    elif action == '#assign':
        top = len(gstack) - 1
        add_block(i, 'ASSIGN', gstack[top], gstack[top - 1])
        i += 1
        gstack.pop()

    elif action == '#index':
        index = gstack.pop()
        address = gstack.pop()
        if index[0] == '#':
            gstack.append(str(int(address) + 4 * int(index[1:])))
        else:
            t = gettemp()
            add_block(i, 'MULT', '#4', index, t)
            i += 1
            add_block(i, 'ADD', '#' + address, t, t)
            i += 1
            gstack.append('@' + t)

    elif action == '#pop':
        gstack.pop()
    elif action == '#saveinp':
        gstack.append(current_token[1])


    elif action == '#opperation':
        second_op = gstack.pop()
        op = gstack.pop()
        first_op = gstack.pop()
        t = gettemp()
        if op == '+':
            add_block(i, 'ADD', first_op, second_op, t)
        elif op == '-':
            add_block(i, 'SUB', first_op, second_op, t)
        elif op == '<':
            add_block(i, 'LT', first_op, second_op, t)
        elif op == '==':
            add_block(i, 'EQ', first_op, second_op, t)
        gstack.append(t)
        i += 1

    elif action == '#signed':
        top_value = gstack.pop()
        t = gettemp()
        add_block(i, 'SUB', '#0', top_value, t)
        i += 1
        gstack.append(t)

    elif action == '#output_in':
        top_value = gstack.pop()
        add_block(i, 'PRINT', top_value)
        i += 1
    elif action == '#save':
        gstack.append(i)
        i += 1

    elif action == '#jpf_save':
        indx = gstack.pop()
        exp = gstack.pop()
        add_block(indx, 'JPF', exp, str(i + 1))
        gstack.append(i)
        i += 1

    elif action == '#jp':
        indx = gstack.pop()
        add_block(indx, 'JP', str(i))

    elif action == '#label':
        gstack.append(str(i))

    elif action == '#while':
        indx = gstack.pop()
        exp = gstack.pop()
        add_block(indx, 'JPF', exp, str(i + 1))
        label = gstack.pop()
        add_block(i, 'JP', label)
        i += 1

    elif action == '#startscope':
        start_scope()

    elif action == '#endscope':
        end_scope()


def save_code_gen():
    global PB
    output = open('output.txt', 'w')
    for i in range(0, len(PB)):
        output.write(f'{i}\t')
        output.write(f'{PB[i]}\n')
