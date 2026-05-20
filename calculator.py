import numpy


def plus(x,y):
    return x + y

def minus(x,y):
    return x - y

def multiply(x,y):
    return x * y

def divide(x,y):
    return x / y

x = int(input("Whats your first number: " ))
y = int(input("Whats your second number: "))
z = input("Whats your operand: ")
if z == "+":
    print(plus(x,y))

elif z == "-":
     print(minus(x,y))

elif z == "*":
     print(multiply(x,y))

elif z == "/":
     print(divide(x,y))
