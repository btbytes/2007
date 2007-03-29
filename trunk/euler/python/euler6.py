"""
Problem 6

The sum of the squares of the first ten natural numbers is,
385
The square of the sum of the first ten natural numbers is,
3025

Hence the difference between the sum of the squares of the 
first ten natural numbers and the square of the sum is 3025 385 = 2640.

Find the difference between the sum of the squares of the 
first one hundred natural numbers and the square of the sum.
"""

#Method 1 
sum = 0
asum = 0
for i in range(1,101):
    asum += i
    sum += i*i 
asum = asum*asum  
print "Difference: ",asum - sum


#Method 2: functional style
from  operator import add
asum = reduce(add, [i for i in range(1,101)])
asum = asum*asum
sum  = reduce(add, [i*i for i in range(1,101)])
print "Difference: ", asum - sum


