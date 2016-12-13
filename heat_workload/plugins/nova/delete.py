import os
class nova_delete():
    def __init__(self,name):
       self.name=name
    def run(self):
       comm = "openstack server delete "+self.name
       os.system(comm)
       print "Deleted server..." +self.name
