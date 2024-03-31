import os
import re
import sys

# Token types
TOKEN_TYPES = [
    ('FOLDER', r'folder\s+(\w+(\.\w+)*)'),
    ('CLASS', r'class\s+(\w+)'),
    ('VARIABLE', r'variable\s+(\w+)'),
    ('FUNCTION', r'function\s+(\w+)'),
    ('IF', r'if'),
    ('NOT', r'not'),
    ('ELSE', r'but if|otherwise'),
    ('IDENTIFIER', r'\b[a-zA-Z_]\w*\b'),
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'{'),
    ('RBRACE', r'}'),
    ('SEMICOLON', r';'),
    ('YEET', r'yeet'),
]

# Keywords
KEYWORDS = {'if', 'not', 'but', 'otherwise', 'yeet'}

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

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

    def peek():
        nonlocal index
        if index < len(tokens):
            return tokens[index]
        return None

    def consume(token_type):
        nonlocal index
        token = peek()
        if token and token[0] == token_type:
            index += 1
            return token
        raise Exception(f'Parser error: Expected {token_type}, found {token}')

    def parse_folder():
        consume('FOLDER')
        # You can perform additional processing here if needed

    def parse_class():
        consume('CLASS')
        name = consume('IDENTIFIER')[1]
        return Node('CLASS', value=name)

    def parse_variable():
        consume('VARIABLE')
        name = consume('IDENTIFIER')[1]
        return Node('VARIABLE', value=name)

    def parse_function():
        consume('FUNCTION')
        name = consume('IDENTIFIER')[1]
        return Node('FUNCTION', value=name)

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
        return Node('BODY', children=statements)

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
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    def parse_expression():
        token = peek()
        if token[0] == 'IDENTIFIER':
            return parse_identifier()
        elif token[0] == 'STRING':
            return parse_string()
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    def parse_identifier():
        token = consume('IDENTIFIER')
        return Node('IDENTIFIER', value=token[1])

    def parse_string():
        token = consume('STRING')
        return Node('STRING', value=token[1])

    def parse_function_call():
        identifier = consume('IDENTIFIER')[1]
        consume('LPAREN')
        arguments = []
        if peek()[0] != 'RPAREN':
            arguments.append(parse_expression())
            while peek()[0] == 'SEMICOLON':
                consume('SEMICOLON')
                arguments.append(parse_expression())
        consume('RPAREN')
        return Node('FUNCTION_CALL', children=[Node('IDENTIFIER', value=identifier)] + arguments)

    def parse_assignment():
        variable = parse_variable()
        consume('SEMICOLON')
        return Node('ASSIGNMENT', children=[variable])

    def parse_yeet():
        consume('YEET')
        error = consume('STRING')[1]
        consume('SEMICOLON')
        return Node('YEET', value=error)

    ast = []
    while peek():
        token = peek()
        if token[0] == 'FOLDER':
            parse_folder()
        elif token[0] == 'CLASS':
            ast.append(parse_class())
        elif token[0] == 'VARIABLE':
            ast.append(parse_variable())
        elif token[0] == 'FUNCTION':
            ast.append(parse_function())
        elif token[0] == 'IF':
            ast.append(parse_if())
        elif token[0] == 'COMMENT':
            index += 1
        else:
            raise Exception(f'Parser error: Unexpected token {token}')

    return ast

def compile_file(file_path):
    # Compile the contents of the .ws file
    with open(file_path, 'r') as file:
        input_text = file.read()

    tokens = lexer(input_text)
    ast = parse(tokens)
    print(ast)  # Replace this with your compilation logic

def compile_files_in_directory(directory):
    # Traverse the directory structure and compile .ws files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.ws'):
                file_path = os.path.join(root, file)
                compile_file(file_path)

def execute_ast(ast):
    # Function to execute the AST (Abstract Syntax Tree)
    for node in ast:
        if node.type == 'CLASS':
            print(f"Declaring class: {node.value}")
        elif node.type == 'VARIABLE':
            print(f"Declaring variable: {node.value}")
        elif node.type == 'FUNCTION':
            print(f"Declaring function: {node.value}")
        elif node.type == 'IF':
            execute_if_statement(node)
        elif node.type == 'YEET':
            print(f"Error: {node.value}")
        elif node.type == 'FUNCTION_CALL':
            execute_function_call(node)

def execute_function_call(call_node):
    function_name = call_node.children[0].value
    arguments = call_node.children[1:]

    if function_name == 'say':
        if len(arguments) != 1:
            raise Exception('Error: say function requires exactly one argument')
        message = arguments[0].value
        print(f"Saying: {message}")
    else:
        print(f"Error: Unknown function '{function_name}'")

def execute_if_statement(if_node):
    condition = if_node.children[0]
    body = if_node.children[1]
    if condition.value == 'true':  # Assuming 'true' condition for demonstration
        execute_ast(body.children)
    else:
        print("Condition not met for if statement")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    compile_files_in_directory(directory)

if __name__ == "__main__":
    main()