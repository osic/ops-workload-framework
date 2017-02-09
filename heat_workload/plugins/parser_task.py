import yaml
import sys
import importlib
sys.path.append("/opt/ops-workload-framework/heat_workload/tools/")
from prettyoutput import Prettyoutput
disp_list = []
class parser_task():
    def __init__(self,name):
          self.file_name=name
    def parse(self):
          file=open(self.file_name)
          stream=yaml.load(file)
          for key,value in stream.iteritems():
              plugin_name=key.split('.')[0]
              pkg=sys.path.append("/opt/ops-workload-framework/heat_workload/plugins/"+plugin_name)
              class_name=key.split('.')[1]
              print plugin_name+" - Task: "+class_name+" started..."
              new_module = importlib.import_module(class_name,pkg)
              mod=getattr(new_module,class_name)
              obj=mod() if value is None else mod(**value) 
              disp_list = obj.run()
              pretty_obj = Prettyoutput(disp_list)
              pretty_obj.display()
