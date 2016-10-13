import click
import os
import subprocess
import time
import fileinput
@click.group()
def workload_def():
    pass



@workload_def.command('workload-create')
@click.option('--name', type=str, required=True)
@click.option('--insecure', required=False, default=True, type=str)
@click.option('-n', required=False, default=1, type=str)
def workload_define(name,insecure,n):
    template_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/main.yaml")
    env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
    newline = "  \"num_of_slices\": " + n
    pattern = "  \"num_of_slices\": "
    replace(newline,pattern,env_path)
    if(insecure == "True"):
        comm = "openstack stack create -t " + template_path + " -e " + env_path + " "+ name + " --insecure"
    else:
        comm = "openstack stack create -t " + template_path + " -e " + env_path + " "+ name
    print(comm)
    print("Creating Stack...")
    os.system(comm)
    print("Stack Creation Finished")

@workload_def.command('scale-up')
@click.option('-sf', type=int, required=False, default=1, help="Adjust scaling factor")
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
@click.option('--insecure', required=False, default="True", type=str, help="Self signed certificate")
def scale_up(sf,name, insecure):
    comm_1 = "openstack stack show " + name
    comm_url = comm_1 + " | grep \"output_value: \" | awk 'BEGIN{ FS=\"output_value: \"}{print $2}' | awk 'BEGIN{ FS=\" \|\"}{print $1}'"
    url = subprocess.check_output(comm_url, shell=True)
    url = url.strip()
    if (insecure == "True"):
        for i in range(1, sf+1):
            comm = "curl -XPOST --insecure -i " + "'" + url + "'"
            os.system(comm)
            time.sleep(10)
    else:
        for i in range(1, sf+1):
            comm = "curl -XPOST -i " + url
            os.system(comm)
    print(comm)
    print("Scaling done...")

@workload_def.command('check-status')
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
def check_status(name):
    comm_1 =  "openstack stack show " + name
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

@workload_def.command('workload-delete')
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
def del_workload(name):
    ans = input("Are you sure you want to delete workload " + name + " (Y/N)")
    if(ans=="Y"):
        comm_del = "openstack stack delete" + name
        os.system(comm_del)
    print("Workload " + name + " deleted...")

@workload_def.command('context-create')
def create_context():
   env_path=os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
   flavor_name= create_flavor(env_path)
   print("Flavor used to create workloads: " +flavor_name)
   network_id= create_network(env_path)
   print("Network used to create workloads: " + network_id)
   image_id=create_image(env_path)
   print("Image used to create workloads: " + image_id)

def create_flavor(env_path):
    comm = "openstack flavor create custom.workload.c1 --ram 2048 --disk 10 --vcpu 1 --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    #os.system("openstack flavor create m1.small_1 --ram 2048 --disk 10 --vcpu 1 --public")
    flavor_id = subprocess.check_output(comm, shell=True)
    flavor_id = flavor_id.strip()
    newline = "  \"instance_type\": " + flavor_id
    pattern = "  \"instance_type\": "
    replace(newline,pattern,env_path)
    return flavor_id

def replace(newline,pattern,env_path):
    f= fileinput.input(env_path, inplace=True)
    for line in f:
        if pattern in line:
           line=newline+"\n"
        print(line),
    f.close()

def create_network(env_path):
    #os.system("neutron net-create net1")
    comm = "neutron net-create net1 | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    net_id = subprocess.check_output(comm, shell=True)
    net_id = net_id.strip()
    comm = "neutron subnet-create "+ net_id +" 192.168.2.0/24 --name subnet1"
    os.system(comm)
    newline = "  \"network_id\": " + net_id
    pattern = "  \"network_id\": "
    replace(newline,pattern,env_path)
    return net_id

def create_image(env_path):
    comm = "openstack --os-image-api-version 1 image create ubuntu_14.04 --location \"http://releases.ubuntu.com/14.04/ubuntu-14.04.5-server-i386.iso\" --disk-format qcow2 --container-format bare --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    image_id = subprocess.check_output(comm, shell=True)
    image_id = image_id.strip()
    newline = "  \"image_id\": " + image_id
    pattern = "  \"image_id\": "
    replace(newline, pattern, env_path)
    #os.system("openstack --os-image-api-version 1 image create ubuntu --location \"http://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img\" --disk-format qcow2 --container-format bare --public")
    return image_id
