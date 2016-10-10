import click
import os
import subprocess
@click.group()
def workload_def():
    pass


@workload_def.command('register-creds')
@click.option('--path', '-p', type=str, required=False)
def register_creds(path):
    command = ['bash', '-c', 'source ' + path]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.communicate()
    print("Credential OK.")


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
@click.option('-sf', type=str, required=False, default=1, help="Adjust scaling factor")
@click.option('--url', type=str, required=True, help="Webhook URL for scaling resources")
@click.option('--insecure', required=False, default=True, type=str, help="Self signed certificate")
def scale_up(scaling_factor,sf,url, insecure):
    for i in range(1,sf):
      if (insecure == "True"):
          comm = "curl -XPOST -i " + url + " --insecure"
      else:
          comm = "curl -XPOST -i " + url
      os.system(comm)
    print("Scaling done...")
