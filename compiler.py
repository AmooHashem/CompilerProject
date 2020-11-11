from scanner import *
import re
import operator

errors = open('syntax_errors.txt', 'w')
parse_tree = open('parse_tree.txt', 'w')
non_terminals_set = set()
terminals_set = set()
ll1_table = {}
grammar_production_rules = []
no_error = True

errors.truncate()
parse_tree.truncate()


def split_grammar_rules():
    global grammar_production_rules
    grammar = open('pa2grammar.txt', 'r').read()
    grammar_production_rules = re.split('\n', grammar)
    for i in range(0, len(grammar_production_rules)):
        grammar_production_rules[i] = re.split(' -> | ', grammar_production_rules[i])


def find_T_and_NTs():
    global non_terminals_set, terminals_set
    for rule in grammar_production_rules:
        non_terminals_set.add(rule[0])
    for rule in grammar_production_rules:
        for T_or_NT in rule:
            if T_or_NT not in non_terminals_set:
                terminals_set.add(T_or_NT)


def convert_file_to_dict(file):
    all_terms = open(file, 'r').read()
    all_terms = re.split('\n', all_terms)
    for i in range(0, len(all_terms)):
        all_terms[i] = re.split(' ', all_terms[i])
    output_dict = {}
    for term in all_terms:
        key = term[0]
        output_dict[key] = set()
        for node in term[1:]:
            output_dict[key].add(node)
    return output_dict


def set_first_and_follows():
    global firsts, follows
    firsts = convert_file_to_dict("Firsts.txt")
    for terminal in terminals_set:
        firsts[terminal] = {terminal}
    follows = convert_file_to_dict("Follows.txt")


def create_table():
    global ll1_table

    for non_terminal in non_terminals_set:
        ll1_table[non_terminal] = {}

    # handle firsts
    rule_number = -1
    for rule in grammar_production_rules:
        rule_number += 1
        non_terminal = rule[0]
        for terminal in firsts[rule[1]]:
            if terminal != 'ε':
                ll1_table[non_terminal][terminal] = rule_number

    # handle follows
    rule_number = -1
    for rule in grammar_production_rules:
        rule_number += 1
        non_terminal = rule[0]
        if not 'ε' in firsts[non_terminal]:
            continue
        for terminal in follows[non_terminal]:
            ll1_table[non_terminal][terminal] = rule_number

    # handle synch
    for non_terminal in non_terminals_set:
        for terminal in follows[non_terminal]:
            if terminal not in ll1_table[non_terminal]:
                ll1_table[non_terminal][terminal] = 'synch'


def handle_error(text):
    global no_error, errors
    if no_error:
        errors.truncate()
        no_error = False
    errors.write(f'#{get_line_number()} : syntax error, {text}\n')


class Tree_node():
    def __init__(self, value, width=0, parent=None):
        self.parent = parent
        self.value = value
        self.childs = []
        self.width = width
        self.depth = 0
        self.height = 0
        self.is_terminal = False
        self.token = None

    def add_child(self, child):
        self.childs.append(child)
        child.width = self.width + 1

    def is_leave(self):
        return len(self.childs) == 0

    def __str__(self):
        return str(self.value) + " " + str(self.width) + " " + str(self.depth)

    def set_token(self, token):
        self.token = token
        self.is_terminal = True

    def show(self):
        if self.is_terminal:
            return "(" + self.token[0] + ", " + self.token[1] + ") "
        if self.value == 'ε':
            return 'epsilon'
        return self.value


def ll1():
    global all_nodes, head_node
    stack = [head_node]
    current_token = get_next_token()

    while True:
        X_node = stack[len(stack) - 1]
        X = X_node.value

        if current_token[0] == 'SYMBOL':
            a = current_token[1]
        elif current_token[0] == 'ID':
            a = current_token[0]
        elif current_token[0] == 'KEYWORD':
            a = current_token[1]
        elif current_token[0] == 'NUM':
            a = current_token[0]
        elif current_token == '$':
            a = current_token

        print()
        print(X)
        print(current_token)
        print(get_line_number())
        print(a)

        if X == 'ε':
            stack.pop()
        elif X == a and a == '$':
            break
        elif X == a and X in terminals_set:
            stack.pop()
            X_node.set_token(current_token)
            current_token = get_next_token()
        elif X != a and X in terminals_set:
            handle_error('missing ' + X)
            node = stack.pop()
            all_nodes.remove(node)
        elif a not in ll1_table[X]:
            if a == '$':
                handle_error('unexpected EOF')
                break
            handle_error('illegal ' + a)
            current_token = get_next_token()
        elif ll1_table[X][a] == 'synch':
            handle_error('missing ' + X)
            node = stack.pop()
            all_nodes.remove(node)
            try:
                node.parent.childs.remove(node)
            except:
                pass

        else:
            rule = grammar_production_rules[ll1_table[X][a]]
            node = stack.pop()
            for index in range(len(rule) - 1, 0, -1):
                new_node = Tree_node(rule[index], parent=node)
                all_nodes.append(new_node)
                stack.append(new_node)
                node.add_child(new_node)


def calculate_depth():
    global head_node

    def visit(node):
        if node.is_leave():
            return
        depth = node.depth + 1
        node.height = 0
        for index in range(len(node.childs) - 1, -1, -1):
            child = node.childs[index]
            child.depth = depth
            visit(child)
            depth += child.height + 1
            node.height += child.height + 1

    visit(head_node)


def draw_tree():
    for node in all_nodes:
        for counter in range(0, node.width - 1):
            parse_tree.write(f'│   ')
        if node.width != 0:
            parse_tree.write(f'├── ')
        parse_tree.write(f'{node.show()}\n')


if __name__ == '__main__':
    errors.write(f'There is no syntax error.')

    split_grammar_rules()
    find_T_and_NTs()
    set_first_and_follows()
    create_table()

    head_node = Tree_node('Program')
    all_nodes = [head_node]
    ll1()

    calculate_depth()
    all_nodes.sort(key=operator.attrgetter('depth'))

    draw_tree()
