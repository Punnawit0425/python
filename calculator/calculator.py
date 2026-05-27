def calculate(x, y, op):
    operations = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
    }

    if op not in operations:
        raise ValueError('Invalid operator')
    if op == '/' and y == 0:
        raise ZeroDivisionError('Cannot divide by zero')

    return operations[op](x, y)

try:
    x = float(input('Whats your first number: '))
    y = float(input('Whats your second number: '))
    op = input('Whats your operand: ').strip()
    print(calculate(x, y, op))
except ValueError as exc:
    print('Error:', exc)
except ZeroDivisionError as exc:
    print('Error:', exc)
