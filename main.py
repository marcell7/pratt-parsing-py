from enum import Enum


class Token:
    def __init__(self, type_, val):
        self.type_ = type_
        self.val = val

    def __repr__(self):
        return f"TOKEN(type={self.type_}, val={self.val})"


class Num:
    def __init__(self):
        self.token = None
        self.val = None

    def __str__(self):
        return f"{self.val}"


class PrefixExp:
    def __init__(self):
        self.token = None
        self.operator = None
        self.right = None

    def __str__(self):
        return f"({self.operator}{self.right})"


class InfixExp:
    def __init__(self):
        self.token = None
        self.left = None
        self.operator = None
        self.right = None

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class Precedence(Enum):
    LOWEST = 1
    SUM = 2
    PRODUCT = 3
    EXPONENT = 4
    PREFIX = 5


def get_tokens(stmt):
    tokens = []
    for i in range(len(stmt)):
        char = stmt[i]
        if char == " ":
            pass
        if char.isdigit():
            integer = char
            peek = True
            look_ahead = 0
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
        if char in ["+", "-", "*", "/", "^", "(", ")"]:
            tokens.append(Token(char, char))
    tokens.append(Token("EOF", None))
    return tokens


class AST:
    def __init__(self, stmt):
        self.prefix_funcs, self.infix_funcs = self.register_prefix_infix_funcs()
        self.precedences = {
            "+": Precedence.SUM,
            "-": Precedence.SUM,
            "*": Precedence.PRODUCT,
            "/": Precedence.PRODUCT,
            "^": Precedence.EXPONENT,
        }
        self.token_ptr = 0
        self.tokens = get_tokens(stmt)
        self.token = self.tokens[self.token_ptr]
        self.peeked_token = self.tokens[self.token_ptr + 1]
        self.exp = self.parse_expression(Precedence.LOWEST)

    def parse_prefix_exp(self):
        exp = PrefixExp()
        exp.token = self.token
        exp.operator = self.token.val
        self.token_ptr += 1
        self.token = self.tokens[self.token_ptr]
        exp.right = self.parse_expression(Precedence.PREFIX)
        return exp

    def parse_infix_exp(self, left):
        exp = InfixExp()
        exp.token = self.token
        exp.operator = self.token.val
        exp.left = left
        precedence = self.precedences.get(self.token.type_, Precedence.LOWEST)
        self.token_ptr += 1
        self.token = self.tokens[self.token_ptr]
        exp.right = self.parse_expression(precedence)
        return exp

    def parse_num(self):
        exp = Num()
        exp.token = self.token
        exp.val = float(self.token.val)
        return exp
    
    def parse_paren(self):
        self.token_ptr += 1
        self.token = self.tokens[self.token_ptr]
        exp = self.parse_expression(Precedence.LOWEST)

        if not self.expectPeek(")"):
            return None
        return exp 

    def parse_expression(self, precedence):
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

    def expectPeek(self, token_type):
        if self.peeked_token.type_ == token_type:
            self.token_ptr += 1
            self.token = self.tokens[self.token_ptr]
            return True
        else:
            return False


    def __str__(self):
        return f"{self.exp}"

if __name__ == "__main__":
    stmt = "(1 + 2 - 3 * 2) ^ (- 3 + 8)"
    ast = AST(stmt)
    print(ast)
