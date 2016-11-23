import os
name="net-client.yaml"
path = os.path.abspath("/opt/ops-workload-framework/heat_workload/resource_definition/"+name)
with open(path) as f:
    lines = f.readlines()
i=0
block=""
for line in lines:
    i = i + 1
    count = len(line) - len(line.lstrip())
    if i >= 31 and i<=88 and count > 2 and "get_param" in line:
       if "- " in line: line=line.replace("  - ","")
       line = line.replace("\n","")
       block = block+ line + "\n"
print "  " + name + ": \n" + "    "+"type"+": "+path+" \n"+"    "+"properties"+":"+" \n"+block
f.close()
