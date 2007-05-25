"""
Problem 20

n! means n (n 1) ... 3 2 1

Find the sum of the digits in the number 100!
"""

def factorial(n):
    if n ==0: return 1
    return n * factorial(n-1)

fact = factorial(100)

import operator
print reduce(operator.add, [int(i) for i in str(fact)] )



