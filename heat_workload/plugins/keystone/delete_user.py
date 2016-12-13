import os
class delete_user():
    def __init__(self,name):
       self.name=name
    def run(self):
       comm = "openstack user delete "+self.name
       os.system(comm)
       print "Deleted User..." +self.name
