import keyword
import math
import string
import sys
from itertools import product
from random import random, choice

COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 50
TYPES = 'integer double'.split()
OPERATORS = '+-*'

numbers = (random() * COUNT for _ in range(COUNT))

chars = string.ascii_lowercase
params = tuple(
    ''.join(comb)
    for n in
    range(
        1,
        int(1 + math.ceil(math.log(COUNT, len(chars))))
    ) for comb in product(chars, repeat=n)
    if ''.join(comb) not in {
        "as", "asc", "declare", "dim", "do",
        "else", "end", "chr", "function",
        "if", "input", "length", "loop",
        "print", "return", "scope", "substr",
        "then", "while",
        "and", "continue",
        "elseif", "exit", "false", "for", "next", "not",
        "or", "shared", "static", "true",
        "integer", "double", "boolean", "string",

        # recursion params
        "n",
    } and ''.join(comb) not in keyword.kwlist
)[:COUNT]

expression = ' '.join(
    '{} {}'.format(
        param,
        choice(OPERATORS)
    ) for param in params
).strip().rstrip(OPERATORS)
values = tuple(int(random() * (2 ** 4)) for _ in range(COUNT))

expected_result = eval(expression, dict(), dict(zip(params, values)))

if __name__ == '__main__':
    print("""\
' big count of function parameters
    
function testing(n as integer, {params_header}) as integer
    dim res as integer
    if n > 0 then
        n = n - 1
        res = testing(n, {params_list})
        return res
    else 
        return {params_expression}
    end if
end function

scope
    dim res as integer
    res = testing(10, {params_values})
    if res = {expected_result} then
        print !"OK";
    else
        print !"NONOK";
    end if
end scope
""".format(
        params_header=', '.join('{} AS {}'.format(
            param,
            choice(TYPES)
        ) for param in params),
        params_expression=expression,
        params_list=', '.join(params),
        params_values=', '.join(map(str, values)),
        expected_result=expected_result
    ))
