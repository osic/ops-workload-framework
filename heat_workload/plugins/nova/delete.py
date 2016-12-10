import os
class nova_delete():
    def __init__(self,name):
       self.name=name
    def delete_server(self):
       comm = "openstack server delete "+self.name
       os.system(comm)
       print "Deleted server..." +self.name
