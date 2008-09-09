"""
Problem 145

Some positive integers n have the property that the sum [ n + reverse(n) ] consists entirely of odd (decimal) digits. 
For instance, 36 + 63 = 99 and 409 + 904 = 1313. We will call such numbers reversible; so 36, 63, 409, and 904 are reversible. 
Leading zeroes are not allowed in either n or reverse(n).
There are 120 reversible numbers below one-thousand.
How many reversible numbers are there below one-billion (10^9)?
"""
import time

def isOdds(n):
  s = set(str(n))
  odds = set(['0','2','4','6','8'])
  if len(s.intersection(odds)) < 1 : return True
  return False
  
def reverse(n):
  return int(str(n)[::-1])
  

def main(n):
  cnt = 0  
  for i in xrange(n):
    if (not str(i).endswith('0') and isOdds(i+reverse(i))): cnt += 1
  return cnt


if __name__ == "__main__":
    n  = 1000000000
    st = time.time()
    cnt = main(n)
    print n, time.time() - st, cnt
    #1000000000 9826.42385912 608720
    #Answer: 608720
    #Time taken: nearly 2 hours and 43 minutes on my Macbook