import click
import os
import subprocess
import time
import fileinput
import sys
import requests
import yaml


@click.group()
def workload_def():
    pass


@workload_def.command('workload-create', help = "Command to create workloads")
@click.option('--name', type=str, required=True, help = "Desired workload name")
@click.option('--insecure', required=False, default=True, type=str)
@click.option('-n', required=False, default=1, type=int, help  = "Desired number of slices")
def workload_define(name, insecure, n):
    print("Validating Quotas")
    validator = quota_validate(n)
    if (validator == 1):
        print("Quota Validated")
        template_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/main.yaml")
        env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
        newline = "  \"num_of_slices\": " + str(n)
        pattern = "  \"num_of_slices\": "
        replace(newline, pattern, env_path)
        if (insecure == "True"):
            comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name + " --insecure"
        else:
            comm = "openstack stack create -t " + template_path + " -e " + env_path + " " + name
        print(comm)
        print("Creating Stack...")
        os.system(comm)
        print("Stack Creation Finished")
    elif validator == 0:
        print("Quota will exceed. Please reduce the number of slices")
    else:
        print("Delete one of the resources that are full")


@workload_def.command('scale-up', help = "Scale up the workloads")
@click.option('-sf', type=int, required=False, default=1, help="Adjust scaling factor")
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
@click.option('--insecure', required=False, default="True", type=str, help="Self signed certificate")
def scale_up(sf, name, insecure):
    print("Validating Quotas")
    validator = quota_validate(sf)
    if (validator == 1):
        print("Quota Validated")
        template_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/main.yaml")
        env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
        comm_1 = "openstack stack show " + name
        comm_url = comm_1 + " | grep \"output_value: \" | awk 'BEGIN{ FS=\"output_value: \"}{print $2}' | awk 'BEGIN{ FS=\" \|\"}{print $1}'"
        url = subprocess.check_output(comm_url, shell=True)
        url = url.strip()
        #stream = open(env_path, 'r')
        #data = yaml.load(stream)
        #sf = int(data['parameters']['num_of_slices']) + int(sf)
        newline = "  \"scaling_size\": " + str(sf)
        pattern = "  \"scaling_size\": "
        replace(newline, pattern, env_path)
        if (insecure == "True"):
            comm = "openstack stack update -t " + template_path + " -e " + env_path + " " + name + " --insecure"
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
            comm = "openstack stack update -t " + template_path + " -e " + env_path + " " + name
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


@workload_def.command('workload-delete', help = "Delete workload and context")
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
def del_workload(name):
    comm_del = "openstack stack delete " + name
    os.system(comm_del)
    time.sleep(120)
    env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
    delete_context(env_path)
    print("Workload " + name + " deleted...")


def delete_context(env_path):
    stream = open(env_path, 'r')
    data = yaml.load(stream)
    comm_del_flavor = "openstack flavor delete " + data['parameters']['instance_type']
    comm_del_image = "openstack image delete " + data['parameters']['image_id']
    comm_del_network = "openstack network delete " + data['parameters']['network_id']
    os.system(comm_del_flavor)
    os.system(comm_del_image)
    os.system(comm_del_network)
    print("Context Deleted....")


@workload_def.command('context-create', help= "Create Context")
def create_context():
    env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
    flavor_name = create_flavor(env_path)
    print("Flavor used to create workloads: " + flavor_name)
    network_id = create_network(env_path)
    print("Network used to create workloads: " + network_id)
    image_id = create_image(env_path)
    print("Image used to create workloads: " + image_id)


@workload_def.command('quota-check', help="Check quotas before creating workloads ")
def quota_check():
    curr_instances = 0 if get_count("server") < 0 else get_count("server")
    curr_ports = 0 if get_count("port") < 0 else get_count("port")
    curr_ram = 2048 * curr_instances
    curr_cores = 2 * curr_instances
    curr_volumes = 1 * curr_instances
    curr_networks = 0 if get_count("network") < 0 else get_count("network")
    d = quota_parse()
    print(
    "Instances: \n" + "Current Usage: " + str(curr_instances) + "\n" + "Total Usage: " + str(d['instances']) + "\n")
    print("Ports: \n" + "Current Usage: " + str(curr_ports) + "\n" + "Total Usage: " + str(d['ports']) + "\n")
    print("Ram: \n" + "Current Usage: " + str(curr_ram) + "\n" + "Total Usage: " + str(d['ram']) + "\n")
    print("Cores: \n" + "Current Usage: " + str(curr_cores) + "\n" + "Total Usage: " + str(d['cores']) + "\n")
    print("Volumes: \n" + "Current Usage: " + str(curr_volumes) + "\n" + "Total Usage: " + str(d['volumes']) + "\n")
    print("Networks: \n" + "Current Usage: " + str(curr_networks) + "\n" + "Total Usage: " + str(d['networks']) + "\n")


def create_flavor(env_path):
    comm = "openstack flavor create custom.workload.c1 --ram 2048 --disk 10 --vcpu 1 --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    # os.system("openstack flavor create m1.small_1 --ram 2048 --disk 10 --vcpu 1 --public")
    comm_check = "openstack flavor show custom.workload.c1"
    try:
        result = subprocess.check_output(comm_check, shell=True)
        if ("No flavor with a name" in result):
            flavor_id = subprocess.check_output(comm, shell=True)
            flavor_id = flavor_id.strip()
            newline = "  \"instance_type\": " + flavor_id
            pattern = "  \"instance_type\": "
            replace(newline, pattern, env_path)
        else:
            comm_check = "openstack flavor show custom.workload.c1 | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
            flavor_id = subprocess.check_output(comm_check, shell=True)
            print("Flavor custom.workload.c1 already present")
    except:
        flavor_id = subprocess.check_output(comm, shell=True)
        flavor_id = flavor_id.strip()
        newline = "  \"instance_type\": " + flavor_id
        pattern = "  \"instance_type\": "
        replace(newline, pattern, env_path)
    return flavor_id.strip()


def replace(newline, pattern, env_path):
    f = fileinput.input(env_path, inplace=True)
    for line in f:
        if pattern in line:
            line = newline + "\n"
        print(line),
    f.close()


def create_network(env_path):
    # os.system("neutron net-create net1")
    print("Validate Network")
    validator = validate_network()
    if (validator == 1):
        comm = "neutron net-create net1 | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
        net_id = subprocess.check_output(comm, shell=True)
        net_id = net_id.strip()
        comm = "neutron subnet-create " + net_id + " 192.168.2.0/24 --name subnet1"
        os.system(comm)
        newline = "  \"network_id\": " + net_id
        pattern = "  \"network_id\": "
        replace(newline, pattern, env_path)
    elif validator == 0:
        net_id = "Quota will exceed. Please delete one of the networks"
    else:
        net_id = "Delete one of the networks"
    return net_id


def create_image(env_path):
    comm = "openstack --os-image-api-version 1 image create centos_14.04 --location \"http://cloud.centos.org/centos/6/images/CentOS-6-x86_64-GenericCloud-1508.qcow2\" --disk-format qcow2 --container-format bare --public | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
    comm_check = "openstack image show ubuntu_14.04"
    try:
        result = subprocess.check_output(comm_check, shell=True)
        comm_check = "openstack image show ubuntu_14.04 | awk 'BEGIN{ FS=\" id\"}{print $2}' | awk 'BEGIN{ FS=\" \"}{print$2}'"
        image_id = subprocess.check_output(comm_check, shell=True)
        print("Image ubuntu_14.04 already present")
    except:
        image_id = subprocess.check_output(comm, shell=True)
        image_id = image_id.strip()
        newline = "  \"image_id\": " + image_id
        pattern = "  \"image_id\": "
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


def quota_validate(slice_num):
    curr_instances = get_count("server")
    #  print(curr_instances)
    curr_ports = get_count("port")
    curr_ram = 2048 * curr_instances
    curr_cores = 2 * curr_instances
    curr_volumes = 1 * curr_instances
    d = quota_parse()
    #  print int(slice_num)
    pred_instances = curr_instances + int(slice_num * 3)
    #  print pred_instances
    pred_ram = curr_ram + int(slice_num * 3 * 2048)
    pred_cores = curr_cores + int(slice_num * 3 * 2)
    pred_volumes = curr_volumes + int(slice_num * 3 * 1)
    #   print pred_ram
    #  print pred_cores
    #  print pred_volumes
    #  print d

    if ((d['instances'] >= pred_instances and d['ram'] >= pred_ram and d['cores'] >= pred_cores and d[
        'volumes'] >= pred_volumes)):
        return 1
    else:
        if (d['instances'] < pred_instances):
            print "Instance Quota will exceed: Predicted Usage: " + str(pred_instances) + "/" + str(d['instances'])
        if (d['ram'] < pred_ram):
            print "Ram Quota will exceed: Predicted Usage: " + str(pred_ram) + "/" + str(d['ram'])
        if (d['cores'] < pred_cores):
            print "Cpu Quota will exceed: Predicted Usage: " + str(pred_cores) + "/" + str(d['cores'])
        if (d['volumes'] < pred_volumes):
            print "Volume Quota will exceed: Predicted Usage: " + str(pred_volumes) + "/" + str(d['volumes'])
        return 0


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
