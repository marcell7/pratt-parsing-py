from enum import Enum


class AST:
    """
    Abstract Syntax Tree (AST).
    Constructs an AST from a given expression statement (stmt). Tree is stored in the 'exp' attribute.
    """

    def __init__(self, stmt):
        self.prefix_funcs, self.infix_funcs = self.register_prefix_infix_funcs()

        # Precedence levels for operators
        self.precedences = {
            "+": Precedence.SUM,  # Precedence level for the "+" operator. Same as "-"
            "-": Precedence.SUM,  # Precedence level for the "-" operator. Same as "+"
            "*": Precedence.PRODUCT,  # Precedence level for the "*" operator. Same as "/"
            "/": Precedence.PRODUCT,  # Precedence level for the "/" operator. Same as "*"
            "^": Precedence.EXPONENT,  # Precedence level for the "^" operator. '^' has the highest precedence
        }
        self.token_ptr = 0  # Pointer to the current token being processed
        self.tokens = get_tokens(stmt)  # List of tokens
        self.token = self.tokens[self.token_ptr]  # Current token
        self.peeked_token = self.tokens[self.token_ptr + 1]  # Next token in the list
        self.exp = self.parse_expression(Precedence.LOWEST)  # AST

    def parse_prefix_exp(self):
        """Parse prefix expressions. Prefix expressions are expressions where the operator comes before the operand eg. -1"""

        exp = PrefixExp()  # Create a new PrefixExp object
        exp.token = self.token
        exp.operator = self.token.val
        self.token_ptr += 1
        self.token = self.tokens[self.token_ptr]  # Move to the next token
        exp.right = self.parse_expression(
            Precedence.PREFIX
        )  # Parse the right side of the expression. Could be a number or another expression
        return exp

    def parse_infix_exp(self, left):
        """
        Parse infix expressions. Infix expressions are expressions where the operator comes between the operands eg. 1 + 2

        """
        exp = InfixExp()  # Create a new InfixExp object
        exp.token = self.token
        exp.operator = self.token.val
        exp.left = left
        precedence = self.precedences.get(
            self.token.type_, Precedence.LOWEST
        )  # Get the precedence of the current token
        self.token_ptr += 1
        self.token = self.tokens[self.token_ptr]
        exp.right = self.parse_expression(precedence)
        return exp

    def parse_num(self):
        """Parse numbers"""
        exp = Num()
        exp.token = self.token
        exp.val = float(self.token.val)  # Represent the parsed number as a float
        return exp

    def parse_paren(self):
        """Parse parentheses. Parentheses are used to group expressions"""
        self.token_ptr += 1
        self.token = self.tokens[
            self.token_ptr
        ]  # The next token should be the start of the expression inside the parentheses
        exp = self.parse_expression(
            Precedence.LOWEST
        )  # Start parsing the expression inside the parentheses

        # If the next token is not a closing parenthesis, return None
        if not self.expect_peek(")"):
            return None
        return exp

    def parse_expression(self, precedence):
        """Parse expressions"""
        prefix_func = self.prefix_funcs.get(self.token.type_, None)
        if prefix_func is None:
            return None
        left_exp = prefix_func()
        if self.token_ptr + 1 >= len(self.tokens):
            return left_exp
        self.peeked_token = self.tokens[self.token_ptr + 1]
        self.peeked_precedence = self.precedences.get(
            self.peeked_token.type_, precedence.LOWEST
        )
        while (
            self.peeked_token.type_ != "EOF"
            and precedence.value < self.peeked_precedence.value
        ):
            infix_func = self.infix_funcs.get(self.peeked_token.type_, None)
            if infix_func is None:
                return left_exp
            self.token_ptr += 1
            self.token = self.tokens[self.token_ptr]
            left_exp = infix_func(left_exp)
        return left_exp

    def register_prefix_infix_funcs(self):
        """Register prefix and infix functions. Assigns parsing functions to specific token types"""
        prefix_funcs = {
            "-": self.parse_prefix_exp,
            "NUM": self.parse_num,
            "(": self.parse_paren,
        }
        infix_funcs = {
            "+": self.parse_infix_exp,
            "-": self.parse_infix_exp,
            "*": self.parse_infix_exp,
            "/": self.parse_infix_exp,
            "^": self.parse_infix_exp,
        }
        return prefix_funcs, infix_funcs

    def expect_peek(self, token_type):
        """Check if the next token is of a specific type. If it is, move to the next token and return True. Otherwise, return False"""
        if self.peeked_token.type_ == token_type:
            self.token_ptr += 1
            self.token = self.tokens[self.token_ptr]
            return True
        else:
            return False

    def __str__(self):
        return f"{self.exp}"


def tree_walk_eval(node):
    """# Tree walk evaluator. Evaluates all nodes in the AST"""
    if isinstance(node, Num):
        return node.val
    elif isinstance(node, PrefixExp):
        right = tree_walk_eval(node.right)
        if node.operator == "-":
            return -right
    elif isinstance(node, InfixExp):
        left = tree_walk_eval(node.left)
        right = tree_walk_eval(node.right)
        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            return left / right
        elif node.operator == "^":
            return left**right


def get_tokens(stmt):
    """Simple tokenizer. Tokenizes the input expression statement"""
    tokens = []
    # Go through all chars
    for i in range(len(stmt)):
        char = stmt[i]

        # Skip spaces
        if char == " ":
            pass
        # Check if char represents a number
        if char.isdigit():
            integer = char
            peek = True
            look_ahead = 0
            # Check if the next chars are also numbers. If they are that means we have a multidigit number
            while peek:
                look_ahead += 1
                if i + look_ahead >= len(stmt):
                    peek = False
                    continue
                peek_char = stmt[i + look_ahead]
                if peek_char.isdigit():
                    integer += peek_char
                else:
                    peek = False
                    continue
            tokens.append(Token("NUM", integer))
        # Check if char is an operator specified in the list
        if char in ["+", "-", "*", "/", "^", "(", ")"]:
            tokens.append(Token(char, char))
    # No more chars to tokenize. Append EOF token
    tokens.append(Token("EOF", None))
    return tokens


class Token:
    def __init__(self, type_, val):
        self.type_ = type_
        self.val = val

    def __repr__(self):
        return f"TOKEN(type={self.type_}, val={self.val})"


class Num:
    """Number node in the AST"""

    def __init__(self):
        self.token = None
        self.val = None  # Float value of the number

    def __str__(self):
        return f"{self.val}"


class PrefixExp:
    """Prefix expression node in the AST"""

    def __init__(self):
        self.token = None
        self.operator = None
        self.right = None

    def __str__(self):
        return f"({self.operator}{self.right})"


class InfixExp:
    """Infix expression node in the AST"""

    def __init__(self):
        self.token = None
        self.left = None  # Expression on the left side of the operator
        self.operator = None  # Operator +, -, *, /, ^
        self.right = None  # Expression on the right side of the operator

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class Precedence(Enum):
    """Precedence levels for operators. From lowest to highest"""

    LOWEST = 1
    SUM = 2  # + and - have the same precedence level
    PRODUCT = 3  # * and / have the same precedence level
    EXPONENT = 4  # ^ has higher precedence level than * and /
    PREFIX = 5  # Prefix operators have the highest precedence level. Eg. -1


if __name__ == "__main__":
    stmt = "1+(2+3^2)*2"
    ast = AST(stmt)
    evaled = tree_walk_eval(ast.exp)
    print(f"Result of the expressions is: {evaled}")
