import os
import re
import sys

# Token types
TOKEN_TYPES = [
    ('FOLDER', r'folder\s+(\w+(\.\w+)*)'),
    ('CLASS', r'class\s+(\w+)(\s+extends\s+\w+)?'),
    ('VARIABLE', r'variable\s+(\w+)(->\w+)?\s*=\s*("[^"]*"|\btrue\b|\bfalse\b|\b[a-zA-Z_]\w*\b)'),
    ('FUNCTION', r'(public\s+)?function\s+(\w+)'),
    ('RETURN', r'return\s+("[^"]*"|\btrue\b|\bfalse\b|\b[a-zA-Z_]\w*\b|\bnull\b)'),
    ('IF', r'if'),
    ('NOT', r'not'),
    ('ELSE', r'but if|otherwise'),
    ('IMPORT', r'import\s+([\w.]+)'),
    ('IDENTIFIER', r'\b[a-zA-Z_]\w*\b'),
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'{'),
    ('RBRACE', r'}'),
    ('SEMICOLON', r';'),
    ('DOT', r'\.'),
    ('YEET', r'yeet'),
    ('ARROW', r'->'),
    ('BOOLEAN', r'true|false'),
    ('NULL', r'null'),
]

# Keywords
KEYWORDS = {'if', 'not', 'but', 'otherwise', 'yeet', 'import', 'extends', 'return'}

class Node:
    def __init__(self, type, children=None, value=None, access_modifier=None):
        self.type = type
        self.children = children if children else []
        self.value = value
        self.access_modifier = access_modifier

def lexer(input_text):
    tokens = []
    position = 0

    while position < len(input_text):
        match = None
        for token_type, pattern in TOKEN_TYPES:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group(0)
                if token_type == 'IDENTIFIER' and value in KEYWORDS:
                    token_type = value.upper()
                if token_type != 'COMMENT':
                    tokens.append((token_type, value))
                break

        if not match:
            raise Exception('Lexer error: Unrecognized token at position ' + str(position))
        
        position = match.end()

    return tokens

def parse(tokens):
    index = 0

    def peek(ahead=0):
        nonlocal index
        if index + ahead < len(tokens):
            return tokens[index + ahead]
        return None

    def consume(token_type):
        nonlocal index
        token = peek()
        if token and token[0] == token_type:
            index += 1
            return token
        raise Exception(f'Parser error: Expected {token_type}, found {token}')

    def parse_import():
        consume('IMPORT')
        module_name = consume('IDENTIFIER')[1]
        while peek() and peek()[0] == 'DOT':
            consume('DOT')
            module_name += '.' + consume('IDENTIFIER')[1]
        consume('SEMICOLON')
        return Node('IMPORT', value=module_name)

    def parse_class():
        consume('CLASS')
        name = consume('IDENTIFIER')[1]
        extends = None
        if peek() and peek()[0] == 'EXTENDS':
            consume('EXTENDS')
            extends = consume('IDENTIFIER')[1]
        body = parse_body()
        return Node('CLASS', value=name, children=body, access_modifier=None)

    def parse_variable():
        consume('VARIABLE')
        name = consume('IDENTIFIER')[1]
        arrow = None
        if peek()[0] == 'ARROW':
            consume('ARROW')
            arrow = consume('IDENTIFIER')[1]
        consume('EQUALS')
        value = parse_value()
        consume('SEMICOLON')
        return Node('VARIABLE', value=(name, arrow, value))

    def parse_function():
        is_public = False
        if peek()[0] == 'PUBLIC':
            consume('PUBLIC')
            is_public = True
        consume('FUNCTION')
        name = consume('IDENTIFIER')[1]
        consume('LPAREN')
        params = parse_parameters()
        consume('RPAREN')
        body = parse_body()
        return Node('FUNCTION', value=(name, params), children=body, access_modifier='public' if is_public else None)
    
    def parse_parameters():
        parameters = []
        while peek() and peek()[0] != 'RPAREN':
            param = consume('IDENTIFIER')[1]
            parameters.append(param)
            if peek()[0] == 'COMMA':
                consume('COMMA')
        return parameters

    def parse_if():
        consume('IF')
        condition = parse_expression()
        body = parse_body()
        return Node('IF', children=[condition, body])

    def parse_body():
        consume('LBRACE')
        statements = []
        while peek() and peek()[0] != 'RBRACE':
            statement = parse_statement()
            statements.append(statement)
        consume('RBRACE')
        return statements

    def parse_statement():
        token = peek()
        if token[0] == 'IF':
            return parse_if()
        elif token[0] == 'IDENTIFIER':
            if peek(1) and peek(1)[0] == 'LPAREN':
                return parse_function_call()
            else:
                return parse_assignment()
        elif token[0] == 'YEET':
            return parse_yeet()
        elif token[0] == 'IMPORT':
            return parse_import()
        elif token[0] == 'RETURN':
            return parse_return()
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    def parse_expression():
        token = peek()
        if token[0] == 'IDENTIFIER':
            return parse_identifier()
        elif token[0] == 'STRING':
            return parse_string()
        elif token[0] == 'BOOLEAN':
            return parse_boolean()
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    def parse_identifier():
        token = consume('IDENTIFIER')
        return Node('IDENTIFIER', value=token[1])

    def parse_string():
        token = consume('STRING')
        return Node('STRING', value=token[1])

    def parse_boolean():
        token = consume('BOOLEAN')
        return Node('BOOLEAN', value=token[1])

    def parse_function_call():
        identifier = consume('IDENTIFIER')[1]
        consume('LPAREN')
        arguments = []
        while peek() and peek()[0] != 'RPAREN':
            arguments.append(parse_expression())
            if peek()[0] == 'COMMA':
                consume('COMMA')
        consume('RPAREN')
        consume('SEMICOLON')
        return Node('FUNCTION_CALL', value=identifier, children=arguments)

    def parse_assignment():
        variable = consume('IDENTIFIER')[1]
        consume('EQUALS')
        value = parse_expression()
        consume('SEMICOLON')
        return Node('ASSIGNMENT', value=(variable, value))
    
    def parse_return():
        consume('RETURN')
        value = parse_expression()
        consume('SEMICOLON')
        return Node('RETURN', value=value)

    def parse_yeet():
        consume('YEET')
        error = consume('STRING')[1]
        consume('SEMICOLON')
        return Node('YEET', value=error)

    def parse_value():
        token = peek()
        if token[0] == 'STRING':
            return consume('STRING')[1]
        elif token[0] == 'BOOLEAN':
            return token[1] == 'true'
        elif token[0] == 'IDENTIFIER':
            return consume('IDENTIFIER')[1]
        elif token[0] == 'NULL':
            consume('NULL')
            return None
        else:
            raise Exception('Parser error: Unexpected value')

    ast = []
    while peek():
        token = peek()
        if token[0] == 'FOLDER':
            consume('FOLDER')
        elif token[0] == 'CLASS':
            ast.append(parse_class())
        elif token[0] == 'VARIABLE':
            ast.append(parse_variable())
        elif token[0] == 'FUNCTION':
            ast.append(parse_function())
        elif token[0] == 'IF':
            ast.append(parse_if())
        elif token[0] == 'RETURN':
            ast.append(parse_return())
        elif token[0] == 'COMMENT':
            index += 1
        elif token[0] == 'IMPORT':
            ast.append(parse_import())
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    return ast

def semantic_analysis(ast):
    symbol_table = {}

    def analyze_node(node):
        if node.type == "CLASS":
            if node.value in symbol_table:
                raise Exception(f"Semantic error: Class {node.value} already declared")
            symbol_table[node.value] = node
        elif node.type == "VARIABLE":
            var_name = node.value[0]
            if var_name in symbol_table:
                raise Exception(f"Semantic error: Variable {var_name} already declared")
            symbol_table[var_name] = node
        elif node.type == "FUNCTION":
            func_name = node.value[0]
            if func_name in symbol_table:
                raise Exception(f"Semantic error: Function {func_name} already declared")
            symbol_table[func_name] = node
        elif node.type == "IF":
            analyze_node(node.children[0])  # condition
            analyze_node(node.children[1])  # body
        elif node.type == "RETURN":
            analyze_node(node.value)
        elif node.type == "FUNCTION_CALL":
            func_name = node.value
            if func_name not in symbol_table:
                raise Exception(f"Semantic error: Function {func_name} not declared")
            for arg in node.children:
                analyze_node(arg)

    for node in ast:
        analyze_node(node)

    return symbol_table

def compile_file(file_path):
    # Compile the contents of the .us file
    with open(file_path, 'r') as file:
        input_text = file.read()

    tokens = lexer(input_text)
    ast = parse(tokens)
    symbol_table = semantic_analysis(ast)

    execute_ast(ast)

def execute_ast(ast):
    for node in ast:
        if node.type == "CLASS":
            print(f"Declaring class: {node.value}")
        elif node.type == "VARIABLE":
            print(f"Declaring variable: {node.value[0]} of type {node.value[1]}")
        elif node.type == "FUNCTION":
            print(f"Declaring {'public ' if node.access_modifier == 'public' else ''}function: {node.value[0]}")
        elif node.type == "IF":
            execute_if_statement(node)
        elif node.type == "RETURN":
            execute_return_statement(node)
        elif node.type == "YEET":
            print(f"Error: {node.value}")
        elif node.type == "FUNCTION_CALL":
            execute_function_call(node)

def execute_if_statement(if_node):
    condition = if_node.children[0]
    body = if_node.children[1]
    if condition.value == 'true':
        execute_ast(body)
    else:
        print("Condition not met for if statement")

def execute_return_statement(return_node):
    value = return_node.value
    print(f"Returning: {value}")

def execute_function_call(call_node):
    function_name = call_node.value
    arguments = call_node.children

    if function_name == 'say':
        if len(arguments) != 1:
            raise Exception('Error: say function requires exactly one argument')
        message = arguments[0].value
        print(f"Saying: {message}")

def compile_files_in_directory(directory):
    # Traverse the directory structure and compile .us files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.us'):
                file_path = os.path.join(root, file)
                compile_file(file_path)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    compile_files_in_directory(directory)

if __name__ == "__main__":
    main()