import os
def getParam(slice):
   count = 0
   with open(slice) as f:
       lines = f.readlines()
   for line in lines:
       if "resources:" not in line: 
             count=count+1
       else: break
   return count

slice="slice2"
slice = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/" + "slice." + slice + ".yaml")
i = 0
count = 0
vm = 0
with open(slice) as f:
     lines = f.readlines()
print("Workloads: ")
for line in lines:
   i = i + 1
   paramcount = getParam(slice)
   print paramcount
   count = len(line) - len(line.lstrip())
   if i >=paramcount and count == 2:
       vm=vm+1
f.close()
print vm
