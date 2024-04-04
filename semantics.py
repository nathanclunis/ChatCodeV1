from lark import Transformer, v_args, Token, Tree

class SemanticError(Exception):
    def __init__(self, message, token=None):
        self.message = message
        self.line = token.line if token else None
        self.column = token.column if token else None
        super().__init__(self.message)

    def __str__(self):
        return f"Semantic Error at line {self.line}, column {self.column}: {self.message}"

class ScopedSymbolTable:
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self.symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def define(self, name, symbol):
        self.symbols[name] = symbol

    def lookup(self, name, current_scope_only=False):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only or not self.enclosing_scope:
            return None
        return self.enclosing_scope.lookup(name)
    
class Symbol:
    def __init__(self, name, type=None, scope_level=0):
        self.name = name
        self.type = type
        self.scope_level = scope_level  # Useful for understanding the scope depth of the symbol

class FunctionSymbol(Symbol):
    def __init__(self, name, parameters=None, type=None, scope_level=0):
        super().__init__(name, type, scope_level)
        self.parameters = parameters if parameters else []

    def __str__(self):
        return f"<{self.name} : {self.type} with params {self.parameters}>"

class SemanticAnalyzer(Transformer):
    def __init__(self):
        self.global_scope = ScopedSymbolTable(scope_name='global', scope_level=0)
        self.current_scope = self.global_scope
        self.errors = []

    def start_scope(self, name):
        scope = ScopedSymbolTable(scope_name=name, scope_level=self.current_scope.scope_level + 1, enclosing_scope=self.current_scope)
        self.current_scope = scope

    def end_scope(self):
        if self.current_scope.enclosing_scope:
            self.current_scope = self.current_scope.enclosing_scope

    @v_args(inline=True)
    def check_contract(self, name, token):
        if self.current_scope.lookup(name, current_scope_only=True):
            self._add_error(f"Contract '{name}' is already defined in the current scope.", token)
        else:
            self.start_scope(name)
            # Define the contract in the current scope
            self.current_scope.define(name, Symbol(name, 'contract'))

    def check_function_declaration(self, name, parameters, token):
        if self.current_scope.lookup(name, current_scope_only=True):
            self._add_error(f"Function '{name}' is already defined in the current scope.", token)
        else:
            function_symbol = FunctionSymbol(name, parameters=parameters)
            self.current_scope.define(name, function_symbol)
            self.start_scope(name)  # Start a new scope for the function body

    def check_variable_declaration(self, name, type, token):
        if self.current_scope.lookup(name, current_scope_only=True):
            self._add_error(f"Variable '{name}' is already defined in the current scope.", token)
        else:
            var_symbol = Symbol(name, type)
            self.current_scope.define(name, var_symbol)

    def check_variable_use(self, name, token):
        if not self.current_scope.lookup(name):
            self._add_error(f"Variable '{name}' is not declared.", token)

    def check_assignment(self, variable, expr_type, token):
        var_symbol = self.current_scope.lookup(variable)
        if var_symbol and var_symbol.type != expr_type:
            self._add_error(f"Type mismatch: Cannot assign '{expr_type}' to '{var_symbol.type}'.", token)

    def _add_error(self, message, token=None):
        line = f" at line {token.line}, column {token.column}" if token else ""
        self.errors.append(f"Semantic Error{line}: {message}")

    def get_errors(self):
        return self.errors

class ASTSimplifier(Transformer):
    def if_statement(self, args):
        condition, then_block = args[0], args[1]
        else_block = args[2] if len(args) > 2 else None
        children = [self.flatten_expression(condition), Tree('then', [then_block])]
        if else_block:
            children.append(Tree('else', [else_block]))
        return Tree('if_statement', children)

    @staticmethod
    def display(args):
        return Tree('display', args)

    @staticmethod
    def block(args):
        if len(args) == 1:
            return args[0]
        return Tree('block', args)

    @staticmethod
    def type_specifier(args):
        return Tree('type_specifier', args)

    def term(self, args):
        if len(args) == 1:
            return self.flatten_expression(args[0])
        else:
            flattened_args = [self.flatten_expression(arg) for arg in args]
            return Tree('expression', flattened_args)

    def flatten_expression(self, tree):
        if tree.data in ['term', 'factor'] and len(tree.children) == 1:
            return self.flatten_expression(tree.children[0])
        else:
            return Tree(tree.data, [self.flatten_expression(child) if isinstance(child, Tree) else child for child in
                                    tree.children])


def analyze(ast):
    analyzer = SemanticAnalyzer()
    analyzer.transform(ast)
    return analyzer
