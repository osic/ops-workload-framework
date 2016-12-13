import os
class delete_volume():
    def __init__(self,name):
       self.name=name
    def run(self):
       comm="openstack volume delete "+self.name
       os.system(comm)
       print "Volume: "+volume_name+" deleted"
