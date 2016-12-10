import random
import string
class getrandom():
     def __init__(self,n):
         self.n=n
     def getSuffix(self):
         self.suffix=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(self.n))
         return self.suffix
