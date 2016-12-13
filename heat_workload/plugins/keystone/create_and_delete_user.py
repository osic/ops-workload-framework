import sys
import subprocess
from create_user import create_user
from delete_user import delete_user
import os
import string
import time
class create_and_delete_user():
    def __init__(self,domain,project):
       self.domain=domain
       self.project=project
    def run(self):
       created=create_user(self.domain,self.project)
       user_name=created.run()
       deleted=delete_user(user_name)
       deleted.run()
