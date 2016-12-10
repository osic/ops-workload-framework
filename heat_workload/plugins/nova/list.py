import os
class list_server():
    def __init__(self):
       comm = "openstack server list"
       os.system(comm)
