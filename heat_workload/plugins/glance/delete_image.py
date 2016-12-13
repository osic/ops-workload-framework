import os
class delete_image():
      def __init__(self,name):
          self.name=name
      def run(self):
          comm = "openstack image delete "+self.name
          os.system(comm)
          print self.name+" image deleted.."
          
