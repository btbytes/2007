"""
Problem 25

The Fibonacci sequence is defined by the recurrence relation:
Fn = Fn1 + Fn2, where F1 = 1 and F2 = 1
... F11 = 89, F12 = 144
The 12th term, F12, is the first term to contain three digits.
What is the first term in the Fibonacci sequence to contain 1000 digits?
"""
def fibonacci():
    a, b = 0, 1
    yield 0
    while True:        
        yield b
        a, b = b, a + b

fib = fibonacci()
cnt = 1
while 1:
    num = fib.next()
    if len(str(num)) == 1000:
        print cnt-1
        break
    cnt +=1
#answer 4782
