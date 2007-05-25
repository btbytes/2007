"""
Problem 4
A palindromic number reads the same both ways. The largest palindrome made from the product of two 2-digit numbers is 9009 = 91 99.
Find the largest palindrome made from the product of two 3-digit numbers.
"""

def palindrome(word):
    l = len(word)
    s1 = word[:l/2]
    if l%2 == 0:        
        s2 = word [l/2:]
    else:
        s2 = word[l/2+1:]
    return s1 == s2[::-1]


def prodgen():
    for i in xrange(999,1,-1):
        for j in xrange(999,1,-1):
            yield str(i*j)


gen = prodgen()

pals = [int(prod) for prod in gen if palindrome(gen.next())]
pals.sort()
print pals[-1]
