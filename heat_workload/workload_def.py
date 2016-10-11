import click
import os
import subprocess
import time
@click.group()
def workload_def():
    pass

@workload_def.command('workload-create')
@click.option('--name', '-n', type=str, required=True)
@click.option('--insecure', required=False, default=True, type=str)
def workload_define(name,insecure):
    template_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/main.yaml")
    env_path = os.path.abspath("/opt/ops-workload-framework/heat_workload/envirnoment/heat_param.yaml")
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
    comm_url = comm_1  +" | grep \"output_value: https\" | awk 'BEGIN{ FS=\" https\"}{print $2}' | awk 'BEGIN{ FS=\" \|\"}{print $1}'"
    url = subprocess.check_output(comm_url, shell=True)
    url = "https" + url.strip()
    print url
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
    comm_status = comm_1 + "| grep \"CREATE_COMPLETE\""
    result = subprocess.check_output(comm_status, shell=True)
    if "CREATE_COMPLETE" not in result:
        print("Workloads are still building up....")
    elif "CREATE_FAILED" in result:
        print("Workload build failed :(")
    else:
        print("Workload build succeeded :)")

@workload_def.command('workload-delete')
@click.option('--name', type=str, required=True, help="Name of the workload assigned during creation")
def del_workload(name):
    ans = input("Are you sure you want to delete workload " + name + " (Y/N)")
    if(ans=="Y"):
        comm_del = "openstack stack delete" + name
        os.system(comm_del)
    print("Workload " + name + " deleted...")
