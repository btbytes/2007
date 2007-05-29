'''
Problem 42
25 April 2003

The nth term of the sequence of triangle numbers is given by, tn = 1/2*(n+1); so
the first ten triangle numbers are:

1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...

By converting each letter in a word to a number according to its alphabetical
position and adding these values, we can form a number for any given word. For
example, SKY, becomes, 19 + 11 + 25 = 55 = t10.

Using words.txt (right click and 'Save Link/Target As...'), a 16K text file
containing nearly two-thousand common English words, how many triangle words can
you make using this method?
'''
from string import lowercase as lc
from operator import add

tri_num = lambda n: n*(n+1)/2
charpos = lambda c: lc.index(c)+1
charsum = lambda word: reduce(add, [charpos(c) for c in word])
possible_tri = [tri_num(n) for n in xrange(1,27)]

data = open('words.txt','r').readline()
wordlist = [s.strip('"').lower() for s in data.split(',')]

print len(filter(lambda x: x in possible_tri, [charsum(w) for w in wordlist]))

