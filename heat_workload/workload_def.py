import click
import os
import subprocess
import time
import fileinput
import sys
import requests
import yaml
import string
import random
sys.path.append("/opt/ops-workload-framework/heat_workload/plugins/")
from parser_task import parser_task
@click.group()
def workload_def():
    pass


@workload_def.command('create', help = "Command to create workloads")
@click.option('--slice', type=str, required=True, help="Slice that will be used for deployment")
@click.option('--name', type=str, required=True, help = "Desired stack name")
@click.option('--insecure', required=False, default=True, type=str)
@click.option('-n', required=False, default=1, type=int, help  = "Desired number of slices")
@click.option('--host', required = False, default = " ", type= str, help = "Compute host name")
@click.option('--group', required=False, default = " ", type=str, help = "Select group of compute hosts for deployment")
@click.option('--envt', required=True, type=str, help="Environment file name used for creating slice")
def workload_define(slice, name, insecure, n, host, envt, group):
    env = "/opt/ops-workload-framework/heat_workload/envirnoment/" + envt + ".yaml"
    env_path = os.path.abspath(env)
    data = open(env_path)
    stream = yaml.load(data)
    flavor = stream['parameters']['flavor']
    if (os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED']!='1'):
        print "Validating Quotas..."
        validator = quota_validate(n,flavor,slice)
    else: validator=1
    if (validator == 1):
        print("Quota Validated")
        template= "/opt/ops-workload-framework/heat_workload/slices/main/main-slice."+slice+".yaml"

        template_path = os.path.abspath(template)

        newline = "  \"num_of_slices\": " + str(n)
        pattern = "  \"num_of_slices\": "
        hostList= ""
        name=name+"."+slice
        print "Updating "
        setConfig()
        replace(newline, pattern, env_path)
        if host != " ":
            print "Deploying in: " +host
            newline = "  \"availability_zone\": " + "nova:" + host
            pattern = "  \"availability_zone\": "
            replace(newline, pattern, env_path)
        elif group != " ":
            print "Deploying in group: "+group
            hostList = getHosts(group)
        elif host == " " and group == " ":
            print "Scheduler will perform deployment.."
            newline = "  \"availability_zone\": nova"
            pattern = "  \"availability_zone\": "
            replace(newline, pattern, env_path)
        if (insecure == "True"):
            if len(hostList) > 0:
                count = 0
                for host in hostList:

                    if ((os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED'] != '1') and count>0):
                        print "Validating Quotas..."
                        validator = quota_validate(n, flavor, slice)
                    else:
                        validator = 1
                    if validator==1:
                        newline = "  \"availability_zone\": " + "nova:" + host
                        pattern = "  \"availability_zone\": "
                        replace(newline,pattern,env_path)
                        comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name + "." + host + " --insecure"
                        print(comm)
                        os.system(comm)
                        count=count+1
                    elif validator == 0:
                        print("Quota will exceed. Please reduce the number of slices")
                    else:
                        print("Delete one of the resources that are full")
            else:
                comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name  + "." + host + " --insecure"
                print(comm)
                os.system(comm)
        else:
            if len(hostList) > 0:
                count = 0
                for host in hostList:

                    if ((os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED'] != '1') and count>0):
                        print "Validating Quotas..."
                        validator = quota_validate(n, flavor, slice)
                    else:
                        validator = 1
                    if validator==1:
                        newline = "  \"availability_zone\": " + "nova:" + host
                        pattern = "  \"availability_zone\": "
                        replace(newline,pattern,env_path)
                        comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name + "." + host
                        print(comm)
                        os.system(comm)
                        count=count+1
                    elif validator == 0:
                        print("Quota will exceed. Please reduce the number of slices")
                    else:
                        print("Delete one of the resources that are full")
            else:
                comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name + "." + host
                print(comm)
                os.system(comm)

        print("Creating Stack...")

        print("Stack Creation Finished")
    elif validator == 0:
        print("Quota will exceed. Please reduce the number of slices")
    else:
        print("Delete one of the resources that are full")

@workload_def.command('gen-host', help = "Generate hosts file with [all] group")
def gen_host():
    comm_1 = "echo [all] > /opt/ops-workload-framework/heat_workload/host"
    result = subprocess.check_output(comm_1,shell=True)
    comm_2 = "openstack host list | grep  \"compute\" | cut -d \"|\" -f 2 >> /opt/ops-workload-framework/heat_workload/host"
    result = subprocess.check_output(comm_2,shell=True)
    print "Host file generated in /opt/ops-workload-framework/heat_workload"

def getHosts(group):
    comm = "ansible "+ group + " -i /opt/ops-workload-framework/heat_workload/host --list-hosts  | grep -v \"^\s*hosts\" > /opt/ops-workload-framework/heat_workload/out"
    subprocess.check_output(comm, shell=True)
    hosts = [line.strip() for line in open('/opt/ops-workload-framework/heat_workload/out')]
    os.system("rm /opt/ops-workload-framework/heat_workload/out")
    return hosts

@workload_def.command('task-start',help="Run a control plane task")
@click.argument('file')
@click.option('-n',required=False,default=1,help="Number of task runs")
def task_start(file,n):
    count=0
    path=os.path.abspath("/opt/ops-workload-framework/heat_workload/tasks/"+file+".yaml")
    if n==-1:
        while True:
            obj = parser_task(path)
            obj.parse()
    else:
        while count<n:
            obj=parser_task(path)
            obj.parse()
            count=count+1

@workload_def.command('scale', help = "Scale up the workloads")
@click.option('-sf', type=int, required=False, default=1, help="Adjust scaling factor")
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
@click.option('--insecure', required=False, default="True", type=str, help="Self signed certificate")
def scale_up(sf, name, insecure):
    slice = name.split('.')[1]
    comm = "openstack stack show "+name+" -f shell | grep \"flavor\" | cut -d \":\" -f 2"
    flavor = subprocess.check_output(comm,shell=True)
    flavor = flavor.replace("\"","").replace("\\","").replace(",","").replace("\n","")
    print("Validating Quotas")
    if (os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED']!='1'):
        validator = quota_validate(sf,flavor,slice)
    else: validator=1
    if (validator == 1):
        print("Quota Validated")
        #envt = d.get(name)

        template_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/main/main-slice."+slice+".yaml")
        #env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/"+envt+".yaml")
        comm_1 = "openstack stack show " + name
        comm_url = comm_1 + " | grep \"output_value: \" | awk 'BEGIN{ FS=\"output_value: \"}{print $2}' | awk 'BEGIN{ FS=\" \|\"}{print $1}'"
        url = subprocess.check_output(comm_url, shell=True)
        url = url.strip()
        #stream = open(env_path, 'r')
        #data = yaml.load(stream)
        #sf = int(data['parameters']['num_of_slices']) + int(sf)
        #newline = "  \"scaling_size\": " + str(sf)
        #pattern = "  \"scaling_size\": "
        #replace(newline, pattern, env_path)

        if (insecure == "True"):
            comm = "openstack stack update "+ name + " -t "+template_path+ " --parameter \"scaling_size=\""+str(sf)+" --existing --insecure"


            # for i in range(0, sf):
            os.system(comm)
            print("Update started...")
            #response = requests.post(url, verify=False)
            #print response.status_code
            while True:
                update_status = poll_update(name)
                if update_status == 1:
                  comm = "curl -XPOST --insecure -i " + "'" + url + "'"
                  os.system(comm)
                  print "Update Completed. Scaling requested.."
                  break
                elif update_status == -1:
                  pass
                elif update_status == 0:
                  print "Update Failed."
                  break

            #time.sleep(20)
        else:
            comm = "openstack stack update " + name + " -t "+template_path+ " --parameter \"scaling_size=\"" + str(sf) + " --existing"
            os.system(comm)
            print("Update started...")
            # for i in range(0, sf):
            #response = requests.post(url)
            #print response.status_code
            while True:
                update_status = poll_update(name)
                if update_status == 1:
                  comm = "curl -XPOST -i " + "'" + url + "'" + " &"
                  os.system(comm)
                  print "Update Completed. Scaling requested.."
                  break
                elif update_status == -1:
                  pass
                elif update_status == 0:
                  print "Update Failed."
                  break
         # print(comm)
    elif validator == 0:
        print("Quota will exceed. Please reduce the scaling factor")
    else:
        print("Delete one of the resources that are full")

@workload_def.command('slice-define', help = "Define slice")
@click.option('--name', type=str, required=True, help="Name of slice")
@click.option('--main', type=str, required=False, default="main-slice")
@click.option('--envt', type=str, required=False, default="environment")
def slice_create(name,main,envt):
    name = "slice."+name
    comm = "cat /opt/ops-workload-framework/heat_workload/templates/"+envt+".yaml > /opt/ops-workload-framework/heat_workload/slices/"+name+".yaml"
    os.system(comm)
    comm = "cat /opt/ops-workload-framework/heat_workload/templates/"+main+".yaml > /opt/ops-workload-framework/heat_workload/slices/main/main-"+name+".yaml"
    os.system(comm)
    newline = "        type: /opt/ops-workload-framework/heat_workload/slices/"+name+".yaml"
    pattern = "        type: OS::Nova::Server::Slice"
    path = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/main/main-" + name + ".yaml")
    replace(newline,pattern,path)
    print "Slice Definition done..."



@workload_def.command('slice-add', help = "Add workloads to slice")
@click.option('--name', type=str, required=True, help = "Slice in which to add workloads")
@click.option('--add', type=str, required=True, help="Name of heat template in resource definition")
def slice_add(name,add):
    name_foo = name
    name="slice."+name
    path = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/"+ name + ".yaml")
    add_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/resource_definition/" + add + ".yaml")
    N=5
    suffix=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
    with open(path, "a") as file:
        resource = add.replace('.yaml','')
        #block = "  "+str(resource)+": \n "+"    "+"type"+": "+add_path+" \n  "+"   "+"properties"+":"+" \n "+"      "+"image_id: { get_param: image_id } \n"+"       "+"instance_type: {get_param: instance_type} \n"+"       "+"network_id: {get_param: network_id} \n"+"       "+"availability_zone: {get_param: availability_zone} \n"+"       "+"key: {get_param: key} \n"+"       "+"volume_size: { get_param: volume_size } \n"
        with open(add_path) as f:
            lines = f.readlines()
        i = 0
        block = ""
        for line in lines:
            i = i + 1
            count = len(line) - len(line.lstrip())
            if i >= 31 and i<=88 and (count ==6 or count >=8) and "get_param" in line:
                if "- " in line: line = line.replace("  - ", "")
                if "__" in line: line = line.replace("__","").replace(" ","",6)
                line = line.replace("\n", "")
                block = block + line + "\n"
        block = "  " + resource + "-" + suffix + ": \n" + "    "+"type"+": "+add_path+" \n"+"    "+"properties"+":"+" \n"+block
        f.close()
        file.write(block)
        print "Workload: "+add+" added to slice: "+name_foo

@workload_def.command('slice-list', help = "List Slices")
def slice_list():
    comm = "ls /opt/ops-workload-framework/heat_workload/slices/ | cut -d \".\" -f 2"
    result = subprocess.check_output(comm, shell=True)
    print result

@workload_def.command('slice-destroy', help = "Destroy a created slice")
@click.option('--name', required=True,help="Name of slice to delete")
def slice_destroy(name):
    del_slice = "rm /opt/ops-workload-framework/heat_workload/slices/slice."+name+".yaml"
    del_main = "rm /opt/ops-workload-framework/heat_workload/slices/main/main-slice."+name+".yaml"
    os.system(del_slice)
    os.system(del_main)
    print "Deleted Slice: "+name

@workload_def.command('slice-remove',help = "Remove specific from slice")
@click.option('--slice', required=True,help="Name of slice")
@click.option('--name', required=True,help="Name of workload to delete")
def slice_remove(slice,name):
    slice = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/" + "slice." + slice + ".yaml")
    f=open(slice)
    stream = yaml.load(f)
    if name in stream['resources']:
        flag=1
        del stream['resources'][name]
    else: flag=0
    #f = fileinput.input(slice, inplace=True)
    #pattern = "  "+name+":"
    #i = 0
    #flag=0
    #for line in f:
        #if pattern in line:
            #flag=1
            #i = i + 1
        #if i == 10:
            #i = 0
        #if i > 0:
            #if i <= 10:
                #i = i + 1
            #continue
        #print(line),
    with open(slice, 'w') as f1:
        yaml.dump(stream, f1, default_flow_style=False)
    f.close()
    f1.close
    if flag == 0: print "Workload: "+name+" not found in slice: "+slice
    else: print "Workload: "+name+" removed from slice: "+slice

@workload_def.command('slice-show', help="List workloads inside slice")
@click.option('--slice', required=True, help="Name of Slice")
def slice_show(slice):
    slice = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/" + "slice." + slice + ".yaml")
    i = 0
    count=0
    with open(slice) as f:
        lines = f.readlines()
    print("Workloads: ")
    for line in lines:
        i = i + 1
        count = len(line) - len(line.lstrip())
        if i >= getParam(slice) and count == 2:
            count=count+1
            print line.replace(":", "").strip()
    f.close()

def getParam(slice):
   count = 0
   with open(slice) as f:
       lines = f.readlines()
   for line in lines:
       if "resources:" not in line:
             count=count+1
       else: break
   return count

def getCount(slice):
    slice = os.path.abspath("/opt/ops-workload-framework/heat_workload/slices/" + "slice." + slice + ".yaml")
    i = 0
    count = 0
    vm = 0
    with open(slice) as f:
        lines = f.readlines()
    for line in lines:
        i = i + 1
        count = len(line) - len(line.lstrip())
        if i >= getParam(slice) and count == 2:
            vm = vm +1
    f.close()
    return vm

def getConfig():
    config = open("/opt/ops-workload-framework/heat_workload/config.yaml")
    config_data = yaml.load(config)
    return config_data

def setConfig():
    config_data = getConfig()
    cpu = "/opt/ops-workload-framework/heat_workload/resource_definition/cpu.yaml"
    pattern = "            sudo stress-ng --cpu"
    newline = "            sudo stress-ng --cpu "+ str(config_data['cpu_cores']) +" --cpu-load " + str(config_data['cpu_load']) + " --cpu-method all -t 2147483647"
    replace(newline,pattern,cpu)
    ram = "/opt/ops-workload-framework/heat_workload/resource_definition/ram.yaml"
    pattern = "            sudo stress-ng -m "
    newline = "            sudo stress-ng -m " + str(config_data['ram_workers']) + " --vm-bytes " + str(config_data['ram_bytes']) + " -t 2147483647"
    replace(newline,pattern,ram)
    disk = "/opt/ops-workload-framework/heat_workload/resource_definition/disk.yaml"
    pattern = "            sudo stress-ng --hdd "
    newline = "            sudo stress-ng --hdd " + str(config_data['disk_workers']) + " --hdd-bytes " + str(config_data['disk_bytes'])+" -t 2147483647"
    replace(newline, pattern,disk)
    slice = "/opt/ops-workload-framework/heat_workload/resource_definition/slice.yaml"
    pattern = "            sudo stress-ng --cpu "
    newline = "            sudo stress-ng --cpu 2 --cpu-load " + str(config_data['cpu_load']) + " --cpu-method all -m "+ str(config_data['ram_workers']) +" --vm-bytes "+ str(config_data['ram_bytes']) +" --hdd "+ str(config_data['disk_workers']) +" --hdd-bytes "+ str(config_data['disk_bytes']) +" -t 2147483647"
    replace(newline, pattern, slice)


@workload_def.command('workload-list', help = "List all workloads present in resource_definition")
def workload_list():
    path = "/opt/ops-workload-framework/heat_workload/resource_definition/*.yaml"
    comm = "ls "+path+" | grep -iwr '^description:'"
    result=subprocess.check_output(comm, shell=True)
    print result.replace("description: ","       Description: ")

@workload_def.command('check-status', help = "Check status of workload creation")
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
def check_status(name):
    comm_1 = "openstack stack show " + name
    comm_status = comm_1 + "| grep \"CREATE_\""
    try:
        result = subprocess.check_output(comm_status, shell=True)
        if "CREATE_COMPLETE" in result:
            print("Workload builds are created :)")
        elif "CREATE_FAILED" in result:
            print("Workload build failed :(")
        else:
            print("Workloads are still building up...")
    except Exception, e:
        print("Exception")

def poll_update(name):
    comm_1 = "openstack stack show -f shell " + name
    comm_status = comm_1 + "| grep  -w \"stack_status\" | cut -d \"=\" -f2"
    try:
        result = subprocess.check_output(comm_status, shell=True)
        if "UPDATE_COMPLETE" in result:
            return 1
        elif "UPDATE_IN_PROGRESS" in result:
            return -1
        elif "UPDATE_FAILED" in result:
            return 0
    except Exception, e:
        print ("Execution Failed. Please try again")


@workload_def.command('destroy', help = "Delete workload and context")
@click.option('--context', required=False, default="N", help = "Delete context as well (Y/N)")
def del_workload(context):
    if "Y" in context:
        delete_context()
    else: print "Skipping context deletion..."
    delete_server()
    delete_stack()

def delete_stack():
    stack_list = getStackList()
    for stack in stack_list:
        if stack != '':
            stack_id = check_stack(stack)
            if stack_id != -1:
                comm_delete = "openstack stack delete "+stack_id+" --yes"
                os.system(comm_delete)
                print "Deleted Stack: "+stack_id
        else:
            print "No stacks found. "

def check_stack(stack_id):
    comm_check = "openstack stack show "+stack_id+" -f shell | grep key | cut -d \":\" -f 2 "
    key_name = subprocess.check_output(comm_check,shell=True).strip()
    if "wload_key" in key_name:
        return stack_id
    else: return -1


def getStackList():
    comm_stack = "openstack stack list -c ID -f value"
    comm_list = subprocess.check_output(comm_stack,shell=True).strip().split("\n")
    return comm_list

def delete_server():
    server_list = getServerList()
    for server in server_list:
        if server != '':
            server_id = check_server(server)
            if server_id != -1:
                comm_delete = "openstack server delete "+server_id
                os.system(comm_delete)
                print "Deleted Server: "+server_id
        print "No servers found. "

def check_server(server_id):
    comm_check = "openstack server show "+server_id+" -f shell | grep key_name | cut -d \"=\" -f 2"
    key_name = subprocess.check_output(comm_check,shell=True).replace("\"","")
    if "wload_key" in key_name:
        return server_id
    else: return -1

def getServerList():
    comm_server = "openstack server list -c ID -f value"
    comm_list = subprocess.check_output(comm_server,shell=True).strip().split("\n")
    return comm_list

def delete_context():
    env_list = ["heat_param_large", "heat_param_medium", "heat_param_small", "heat_param_slice"]
    for env in env_list:
        delete_flavor("/opt/ops-workload-framework/heat_workload/envirnoment/"+env+".yaml")
        delete_network("/opt/ops-workload-framework/heat_workload/envirnoment/"+env+".yaml")
        delete_image("/opt/ops-workload-framework/heat_workload/envirnoment/"+env+".yaml")
    #delete_servers()
    #delete_stack()
    #comm_del_flavor = "openstack flavor delete " + data['parameters']['flavor']
    #comm_del_image = "openstack image delete " + data['parameters']['image']
    #comm_del_network = "openstack network delete " + data['parameters']['network']
    #os.system(comm_del_flavor)
    #os.system(comm_del_image)
    #os.system(comm_del_network)
    print("Context Deleted....")

def delete_flavor(env_path):
    f=open(env_path,'r')
    stream = yaml.load(f)
    comm_del_flavor = "openstack flavor delete "+ stream['parameters']['flavor']
    os.system(comm_del_flavor)
    print "Deleted Flavor: "+stream['parameters']['flavor']

def delete_image(env_path):
    f=open(env_path,'r')
    stream = yaml.load(f)
    comm_del_image = "openstack image delete "+ stream['parameters']['image']
    os.system(comm_del_image)
    print "Deleted Image: "+ stream['parameters']['image']

def delete_network(env_path):
    f = open(env_path, 'r')
    stream = yaml.load(f)
    network_id = stream['parameters']['network']
    comm_check = "openstack router show router1.small"
    try:
        result_comm_check = subprocess.check_output(comm_check,shell=True)
        delete_router()
    except:
        print "No router found"

    comm_subnet = "neutron net-show "+network_id +" -f shell | grep \"subnets\" | cut -d \"=\" -f 2"
    subnet_id = subprocess.check_output(comm_subnet,shell=True)
    subnet_id = subnet_id.replace("\"","").strip()
    delete_subnet(subnet_id)
    comm_net_del = "openstack network delete "+network_id
    os.system(comm_net_del)
    print "Deleted Network: "+network_id

def delete_subnet(subnet_id):
    comm_port_check = "neutron port-list -c id -c fixed_ips -f value | grep  "+subnet_id+" | cut -d \" \" -f 1"
    port_list = subprocess.check_output(comm_port_check,shell=True).split("\n")
    if port_list != '':
        for port in port_list[:-1]:
            delete_port(port)
    comm_subnet_del = "openstack subnet delete "+subnet_id
    os.system(comm_subnet_del)
    print "Deleted Subnet: "+subnet_id


def delete_port(port_id):
    comm_port_del = "openstack port delete "+port_id
    os.system(comm_port_del)
    print "Deleted Port "+port_id

def delete_router():
    router_list = ["router1.small","router1.medium","router1.large","router1.slice"]
    for router in router_list:
        router_id_list = get_list(router)
        delete_router_port(router_id_list)
        delete_router_id(router_id_list)

def delete_router_port(router_id_list):
    for id in router_id_list:
        subnet_id = getSubnet(id)
        if subnet_id != '':
            comm_port = "neutron router-interface-delete "+id+" "+subnet_id
            os.system(comm_port)
            print comm_port
    for id in router_id_list:
        comm_gw = "neutron router-gateway-clear "+id
        os.system(comm_gw)

def getSubnet(router_id):
    comm_subnet = "neutron router-port-list "+router_id+" -c fixed_ips -f value | awk 'BEGIN{ FS=\"\"subnet_id\":\"}{print $2}' | cut -d \",\" -f 1"
    subnet_id = subprocess.check_output(comm_subnet,shell=True).strip()
    return subnet_id

def delete_router_id(router_id_list):
    for id in router_id_list:
        comm_del = "neutron router-delete "+id
        os.system(comm_del)

def get_list(router):
    comm = "neutron router-list -f value | grep "+router+" | cut -d \" \" -f 1"
    router_id = subprocess.check_output(comm,shell=True)
    router_id_list = router_id.split("\n")
    return router_id_list

@workload_def.command('create-workload', help="Create workloads from script")
@click.option('--path',type=str,required='True', help="Path to script")
@click.option('--template', type=str, required='False', help="Path to Template used for creating workloads", default='main.yaml')
@click.option('--name', type=str,required='True',help='Name of workload')
def create_workload(path,template,name):
    with open(path, 'r') as myscript:
        data = myscript.read()
    print data
    myscript.close()
    f=open(template)
    stream=yaml.load(f)
    stream['resources']['nova_server']['properties']['user_data']['str_replace']['template']=data
    workload_file = '/opt/ops-workload-framework/heat_workload/resource_definition/'+name+'.yaml'
    create_file = 'touch '+workload_file
    os.system(create_file)
    with open(workload_file, 'w') as f1:
        yaml.dump(stream, f1, Dumper=yaml.RoundTripDumper)
    f.close()
    f1.close()



@workload_def.command('create-context', help= "Create Context")
@click.option('--ext',help="External Network ID/Name", required= False, default= '')
def create_context(ext):
    types = ['small', 'medium', 'large', 'slice']
    for type in types:
        print("***********Context create for " + type + " vms***********")
        path = "/opt/ops-workload-framework/heat_workload/envirnoment/heat_param_"+type+".yaml"
        env_path = os.path.abspath(path)
        flavor_name = create_flavor(env_path,type)
        print("Flavor used to create workloads: " + flavor_name)
        network_id = create_network(env_path,type,ext)
        print("Network used to create workloads: " + network_id)
        image_id = create_image(env_path,type)
        print("Image used to create workloads: " + image_id)
        key_name = create_key(env_path)
        print("Key Used to create workloads: " + key_name)
        print("Key wload_key.pem stored in the /root")
        print("*********************************************************")


@workload_def.command('check-quota', help="Check quotas before creating workloads ")
def quota_check():
    curr = getCurrentUsage()
    curr_instances = 0 if get_count("server") < 0 else get_count("server")
    curr_ports = 0 if get_count("port") < 0 else get_count("port")
    curr_ram = curr['ram']
    curr_cores = curr['cores']
    curr_volumes = curr['volumes']
    curr_networks = 0 if get_count("network") < 0 else get_count("network")
    d = quota_parse()
    print("Instances: \n" + "Current Usage: " + str(curr_instances) + "\n" + "Total Usage: " + str(d['instances']) + "\n")
    print("Ports: \n" + "Current Usage: " + str(curr_ports) + "\n" + "Total Usage: " + str(d['ports']) + "\n")
    print("Ram: \n" + "Current Usage: " + str(curr_ram) + "\n" + "Total Usage: " + str(d['ram']) + "\n")
    print("Cores: \n" + "Current Usage: " + str(curr_cores) + "\n" + "Total Usage: " + str(d['cores']) + "\n")
    print("Volumes: \n" + "Current Usage: " + str(curr_volumes) + "\n" + "Total Usage: " + str(d['volumes']) + "\n")
    print("Networks: \n" + "Current Usage: " + str(curr_networks) + "\n" + "Total Usage: " + str(d['networks']) + "\n")


def getCurrentUsage():
    d = {}
    comm_cores = "nova absolute-limits | grep Cores | awk 'BEGIN{ FS=\"Cores  \"}{print $2}' | cut -d \"|\" -f 2"
    comm_ram = "nova absolute-limits | grep RAM | awk 'BEGIN{ FS=\"RAM  \"}{print $2}' | cut -d \"|\" -f 2"
    comm_volume = "cinder quota-usage admin| grep -i volumes | awk 'BEGIN{ FS=\"volumes  \"}{print $2}' | cut -d \"|\" -f 2"
    cores = subprocess.check_output(comm_cores,shell=True)
    d['cores'] = 0 if '-' in cores else int(cores.strip())
    ram = subprocess.check_output(comm_ram,shell=True)
    d['ram'] = 0 if '-' in ram else int(ram.strip())
    volumes = subprocess.check_output(comm_volume,shell=True)
    d['volumes'] = 0 if '-' in volumes else int(volumes.strip())
    return d

def create_key(env_path):
    comm = "openstack keypair create wload_key > /root/wload_key.pem"
    comm_check = "openstack keypair show wload_key"
    try:
       result = subprocess.check_output(comm_check,shell=True)
       if ("No keypair" in result):
           print "CREATING KEY"
           os.system(comm)
           key_name = "wload_key"
           newline = "  \"key_name\": " + key_name
           pattern = "  \"key_name\":"
           replace(newline, pattern, env_path)
       else:
           key_name = "wload_key"
           print("Keypair wload_key already exists")
           newline = "  \"key_name\": " + key_name
           pattern = "  \"key_name\":"
           replace(newline, pattern, env_path)
    except:
        os.system(comm)
        comm_check = "openstack keypair show wload_key | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print $2}'"
        key_name = subprocess.check_output(comm_check, shell=True)
        key_name = "wload_key"
        newline = "  \"key_name\": " + key_name
        pattern = "  \"key_name\":"
        replace(newline, pattern, env_path)
    return key_name.strip()


def create_flavor(env_path,type):
    flavor = getConfig()
    if type == "small":
        params = {'name': "custom.workload.small",'ram': flavor['small']['ram'],'disk': flavor['small']['disk'],'vcpu': flavor['small']['vcpu']}
    elif type == "medium":
        params = {'name': "custom.workload.medium", 'ram': flavor['medium']['ram'], 'disk': flavor['medium']['disk'], 'vcpu': flavor['medium']['vcpu']}
    elif type == "large":
        params = {'name': "custom.workload.large", 'ram': flavor['large']['ram'], 'disk': flavor['large']['disk'], 'vcpu': flavor['large']['vcpu']}
    else:
        params = {'name': "custom.workload.slice", 'ram': flavor['slice']['ram'], 'disk': flavor['slice']['disk'], 'vcpu': flavor['slice']['vcpu']}
    comm = "openstack flavor create " + str(params['name']) + " --ram " + str(params['ram']) + " --disk " + str(params['disk']) + " --vcpu " + str(params['vcpu']) + " --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    # os.system("openstack flavor create m1.small_1 --ram 2048 --disk 10 --vcpu 1 --public")
    comm_check = "openstack flavor show " + params['name']
    try:
        result = subprocess.check_output(comm_check, shell=True)
        if ("No flavor with a name" in result):
            flavor_id = subprocess.check_output(comm, shell=True)
            flavor_id = flavor_id.strip()
            newline = "  \"flavor\": " + flavor_id
            pattern = "  \"flavor\": "
            replace(newline, pattern, env_path)
        else:
            comm_check = "openstack flavor show "+params['name']+ " | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
            flavor_id = subprocess.check_output(comm_check, shell=True)
            print("Flavor " + params['name'] + " already present")
            flavor_id = flavor_id.strip()
            newline = "  \"flavor\": " + flavor_id
            pattern = "  \"flavor\": "
            replace(newline, pattern, env_path)
    except:
        flavor_id = subprocess.check_output(comm, shell=True)
        flavor_id = flavor_id.strip()
        newline = "  \"flavor\": " + flavor_id
        pattern = "  \"flavor\": "
        replace(newline, pattern, env_path)
    return flavor_id.strip()


def replace(newline, pattern, env_path):
    f = fileinput.input(env_path, inplace=True)
    for line in f:
        if pattern in line:
            line = newline + "\n"
        print(line),
    f.close()


def create_network(env_path,type,ext):
    # os.system("neutron net-create net1")
    print("Validating Network Quota...")
    if (os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED']!='1'):
          validator = validate_network()
    else: validator=1
    if (validator == 1):
        comm = "neutron net-create net1."+type+" | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
        net_id = subprocess.check_output(comm, shell=True)
        net_id = net_id.strip()
        comm_1 = "neutron subnet-create " + net_id + " 192.161.2.0/24 --name subnet1."+type+" | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
        subnet_id = subprocess.check_output(comm_1, shell=True)
        subnet_id = subnet_id.strip()
        comm_1 = "neutron subnet-update " + subnet_id + " --dns-nameservers list=true 8.8.8.8 8.8.4.4"
        os.system(comm_1)
        newline = "  \"network\": " + net_id
        pattern = "  \"network\": "
        replace(newline, pattern, env_path)
        if ext != '':
            create_router(ext,net_id,subnet_id,type)
    elif validator == 0:
        net_id = "Quota will exceed. Please delete one of the networks"
    else:
        net_id = "Delete one of the networks"

    return net_id

def create_router(ext,net_id,subnet_id,type):
    comm = "neutron router-create router1." + type + " | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    router_id = subprocess.check_output(comm, shell=True)
    router_id = router_id.strip()
    router_gw = "neutron router-gateway-set " + router_id + " " + ext
    os.system(router_gw)
    router_int = "neutron router-interface-add " + router_id + " " + subnet_id
    os.system(router_int)
    print "Network: " + net_id + " has the following external gateway " + ext


def create_image(env_path, type):
    image = getConfig()
    if type == "small":
        params = {'name':'image.small','url': image['image_small']}
    elif type == "medium":
        params = {'name':'image.medium','url': image['image_medium']}
    elif type == "large":
        params = {'name': 'image.large',
                  'url': image['image_large']}
    else:
        params = {'name': 'ubuntu.slice',
                  'url': image['image_slice']}
    comm = "openstack --os-image-api-version 1 image create " + params['name'] + " --location \"" + params['url'] + "\" --disk-format qcow2 --container-format bare --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    comm_check = "openstack image show " + params['name']
    try:
        result = subprocess.check_output(comm_check, shell=True)
        comm_check = "openstack image show " + params['name'] + " | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
        image_id = subprocess.check_output(comm_check, shell=True)
        print("Image " + params['name'] + " already present")
        image_id = image_id.strip()
        newline = "  \"image\": " + image_id
        pattern = "  \"image\": "
        replace(newline,pattern,env_path)
    except:
        image_id = subprocess.check_output(comm, shell=True)
        image_id = image_id.strip()
        newline = "  \"image\": " + image_id
        pattern = "  \"image\": "
        replace(newline, pattern, env_path)
    # os.system("openstack --os-image-api-version 1 image create ubuntu --location \"http://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img\" --disk-format qcow2 --container-format bare --public")
    return image_id.strip()


def quota_parse():
    comm_instances = "openstack quota show -c instances admin -f shell  | cut -d \"=\" -f2"
    comm_ram = "openstack quota show -c ram admin -f shell  | cut -d \"=\" -f2"
    comm_cores = "openstack quota show -c cores admin -f shell  | cut -d \"=\" -f2"
    comm_volumes = "openstack quota show -c volumes admin -f shell  | cut -d \"=\" -f2"
    comm_networks = "openstack quota show admin -f shell | grep networ  | cut -d \"=\" -f2"
    comm_ports = "openstack quota show admin -f shell | grep port  | cut -d \"=\" -f2"
    instances = int(subprocess.check_output(comm_instances, shell=True).strip().replace('"', ''))
    cores = int(subprocess.check_output(comm_cores, shell=True).strip().replace('"', ''))
    volumes = int(subprocess.check_output(comm_volumes, shell=True).strip().replace('"', ''))
    ram = int(subprocess.check_output(comm_ram, shell=True).strip().strip().replace('"', ''))
    networks = int(subprocess.check_output(comm_networks, shell=True).strip().replace('"', ''))
    ports = int(subprocess.check_output(comm_ports, shell=True).strip().replace('"', ''))
    d = {}
    d['instances'] = sys.maxint if instances == -1 else instances
    d['cores'] = sys.maxint if cores == -1 else cores
    d['volumes'] = sys.maxint if volumes == -1 else volumes
    d['ram'] = sys.maxint if ram == -1 else ram
    d['networks'] = sys.maxint if networks == -1 else networks
    d['ports'] = sys.maxint if ports == -1 else ports
    return d

def getInfo(flavor):
    d={}
    comm_ram = "openstack flavor show "+flavor+" -f shell | grep \"ram\" | cut -d \"=\" -f2"
    ram = subprocess.check_output(comm_ram,shell=True)
    comm_cores = "openstack flavor show "+flavor+" -f shell | grep \"vcpus\" | cut -d \"=\" -f2"
    cores = subprocess.check_output(comm_cores, shell=True)
    d['ram']=int(ram.replace("\n","").replace("\"",""))
    d['cores']=int(cores.replace("\n","").replace("\"",""))
    return d

def quota_validate(slice_num,flavor,slice):
    #env = "/opt/ops-workload-framework/heat_workload/envirnoment/" + envt + ".yaml"
    #env_path = os.path.abspath(env)
    curr_instances = get_count("server")
    #  print(curr_instances)
    flavor=getInfo(flavor)
    curr = getCurrentUsage()
    curr_ports = get_count("port")
    curr_ram = curr['ram']
    curr_cores = curr['cores']
    curr_volumes = curr['volumes']
    #curr_volumes = 1 * curr_instances
    d = quota_parse()
    #  print int(slice_num)
    slice_count = getCount(slice)
    pred_instances = curr_instances + int(slice_num * slice_count)
    #  print pred_instances
    pred_ram = curr_ram + int(slice_num * slice_count * flavor['ram'])
    pred_cores = curr_cores + int(slice_num * slice_count * flavor['cores'])
    pred_volumes = curr_volumes + int(slice_num * slice_count * 0)
    #   print pred_ram
    #  print pred_cores
    #  print pred_volumes
    #  print d

    if (os.getenv('QUOTA_CHECK_DISABLED') is None or os.environ['QUOTA_CHECK_DISABLED']!=1):
        if ((d['instances'] >= pred_instances and d['ram'] >= pred_ram and d['cores'] >= pred_cores)):
            return 1
        else:
            if (d['instances'] < pred_instances):
                print "Instance Quota will exceed: Predicted Usage: " + str(pred_instances) + "/" + str(d['instances'])
            if (d['ram'] < pred_ram):
                print "Ram Quota will exceed: Predicted Usage: " + str(pred_ram) + "/" + str(d['ram'])
            if (d['cores'] < pred_cores):
                print "Cpu Quota will exceed: Predicted Usage: " + str(pred_cores) + "/" + str(d['cores'])
            return 0
    else:
        return 1




def get_count(str):
    comm_1 = "openstack " + str + " list"
    comm = comm_1 + " | wc -l"
    result = int(subprocess.check_output(comm, shell=True))
    result = result - 4
    return result


def validate_network():
    curr_networks = get_count("network")
    d = quota_parse()
    pred_networks = curr_networks + 1
    if (d['networks'] >= pred_networks):
        return 1
    else:
        if (d['networks'] < pred_networks):
            print "Network Quota will exceed: Predicted Usage: " + str(pred_networks) + "/" + str(d['networks'])
        return 0
