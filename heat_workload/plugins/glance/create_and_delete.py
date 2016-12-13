import sys
import subprocess
from create_image import create_image as glance_create
from delete_image import delete_image as glance_delete
import time
class create_and_delete():
      def __init__(self,url,disk,container):
         self.url=url
         self.disk=disk
         self.container=container
      def run(self):
         created = glance_create(self.url,self.disk,self.container)
         image_name=created.run()
         time.sleep(15)
         deleted = glance_delete(image_name)
         deleted.run()
