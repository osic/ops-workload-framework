### ops-workload-framework:

About this Repository
---------------------
The purpose of the repo is to generate workloads in our OpenStack deployments that will help us gather meaningful data and close to production scenarios, that will help us to address each of the OSIC KPIs at scale.

Contents
---------
+ [Overview](https://github.com/osic/ops-workload-framework/blob/master/README.md#overview)
+ [Proposed Workloads](https://github.com/osic/ops-workload-framework/blob/master/README.md#proposed-workloads)
+ [Prerequisites](https://github.com/osic/ops-workload-framework/blob/master/README.md#prerequisites)
+ [Creating Workload Definition](https://github.com/osic/ops-workload-framework/blob/master/README.md#workload-definition)
+ [Autoscaling group](https://github.com/osic/ops-workload-framework/blob/master/README.md#autoscaling-group)
+ [Workload slice] (https://github.com/osic/ops-workload-framework/blob/master/README.md#workload-slice)
+ [Run control plane plugins](https://github.com/osic/ops-workload-framework/blob/master/README.md#control-plane-plugins)
+ [Centralized configuration of workloads and flavors](https://github.com/osic/ops-workload-framework/blob/master/README.md#centralized-configuration)
+ [Using multiple target hosts](https://github.com/osic/ops-workload-framework/blob/master/README.md#multiple-target-hosts)
+ [Quota Checks](https://github.com/osic/ops-workload-framework/blob/master/README.md#quota-checks)
+ [Environment Variables](https://github.com/osic/ops-workload-framework/blob/master/README.md#environment-variables)
+ [Installation](https://github.com/osic/ops-workload-framework/blob/master/README.md#installation)
+ [Workload Framework](https://github.com/osic/ops-workload-framework/blob/master/README.md#workload-framework)

Overview
--------
Understanding how Business-critical workloads (web servers, mail servers, app servers, etc) demand and use resources is key in capacity sizing, in infrastructure operation and testing, and in application performance management.
It is really hard to understand workload information due to its complexity (larger scale, heterogeneous, shared clusters). Based on “Statistical Characterization of Business-Critical Workloads Hosted in Cloud Datacenters” there are four key types of resources that can become bottlenecks for business-critical applications: CPU, disk I/O, memory and Network I/O.

Proposed Workloads
------------------
Type of workloads:
1. CPU Intensive workload: Spans 4 cpu workers that stresses the cpu cores.
2. Memory Intensive workload: Spans 55 memory workers that fills up the cpu.
3. Network IO workload: Uses netcat command to constantly send and receive large file which stresses the bandwidth.
4. Disk Intensive workload: Spans 60 disk workers that fills up the disk by creating 1 gb blocks of data.

Type of Vms:
There are 4 different types of VMs in which the workloads are executed:
1. Large VM ( CPU: 6, RAM: 4g, Disk: 6g)
2. Medium VM ( CPU: 4, RAM: 2g, Disk: 4g)
3. Small VM ( CPU: 1, RAM: 1g, Disk: 2g )
4. Slice VM ( CPU: 8, RAM: 8g, Disk: 8g)


Prerequisites
-------------

+ An existing OpenStack Cloud on which to deploy the resources.
+ Python Heat / OpenStack Client installed and configured with credentials on host machine.
+ Horizon Dashboard (optional) to check the status of autoscaling and workload generation.

Workload Definition
-------------------

This part involves creating your own resource using Heat templates which will be deployed on the cloud. An example for this could be a RAM Intensive resource
which can host applications consuming more memory.
All resource definition are located and stored inside the "resource_definition" directory and should be specified in the "slice.yaml" file.

Autoscaling group
-----------------

The autoscaling group are Heat templates that utilizes the autoscaling policy of Heat. They define a group of resources that are deployed as a slice and can be
scaled up or down as per the requirement. For a resource to be included in a autoscaling group, it must first be defined and then registered to resource path in
the environment file. The resource path is included in the group and a scaling policy for that group is created which can either scale up the particular resource
or scale down. An another alternative could be to generate a webhook URL for a scaling policy and then a simple POST request on the url would trigger a scaling
request.

The autoscaling groups are defined inside the "main.yaml" file.

```shell
# POST reques webhook URL to trigger scaling
curl -XPOST -i "<URL>"
```

Workload slice
--------------
A workload slice consists of multiple workloads along with their properties and parameters. Workload generator allows creation/delete/modification of slices and considers only those workloads that are in `resource_definition` directory. __For deploying a workload, it must be added to an existing slice.__  

Workload generator slice commands are as follows:

__Create an empty slice and autoscaling group for slice. A slice will be created in 'slices' directory and an autoscaling group file will be created by name__ `main-slice.<name-of-slice>.yaml`
```shell
workload_def slice-define --name <name-of-slice>
```

__Destroy slice__
```shell
workload_def slice-destroy --name <name-of-slice>
```

__View workloads in slice__
```shell
workload_def slice-show --slice <name-of-slice>
```

__List slices__
```shell
workload_def slice-list
```

__Remove specific workloads from slice__
```shell
workload_def slice-remove --slice <name-of-slice> --name <name-of-workload>
```

__Add workloads in an existing slice__
```shell
workload_def slice-add --name <name-of-slice> --add <name-of-workload>
```


Control Plane plugins
---------------------
The workload generator also provides control plane plugins to test API of core services. They are located under `plugins` directory and a YAML task can be created to invoke those plugins. 
Running a sample task:
```shell
workload_def task-start <name-of-task-file> -n <number-of-iterations(-1: infinite)>
```

Centralized configuration
-------------------------
The workload generator reads and applies values from the `config.yaml` file located in main directory before deploying any slice workloads. This configuration allows user to control cpu,ram,disk workloads as well as flavors that will be created during context creation.

Multiple target hosts
---------------------
It is possible to group multiple compute hosts using ansible host group. The workload generator then gives the option to either target a single compute host or an ansible group. The `host` file lists the different ansible host groups. The user can create their own ansible group or can use the `[all]` group which will deploy workloads on all compute hosts.
The following command can create an `[all]` group with all compute hosts inside host file:
```shell
workload_def gen-host
```

Quota Checks
------------

The workload framework can also perform a quota checks before creating workloads and scaling up. The Quota checks evaluates current quotas and will deploy workloads only if there are enough quotas available for creation or scaling up(depending on operation performed). 
Quota checks can be disabled by setting `QUOTA_CHECK_DISABLED` to '1':
```shell
export QUOTA_CHECK_DISABLED='1'
```

Environment Variables
---------------------

An environment file is defined in the "environment" directory which defines the input parameters and their values in "parameter: value" format. The file is
divided into two section: 

1. The "parameters" section defines the value of the input parameters used in the resource definition and the autoscaling groups heat templates.
The parameters section should define the attributes along with their values that will be used for booting each resource:

  + num_of_slices: Defines the number of slices of resources to be deployed initially while workload creation.
  + instance_type: The flavor of each resource should be specified.
  + image_id: The ID or name of a glance image which will be used to boot the instances.
  + scaling_size: The scaling factor which defines the number of slices that will be generated as a result of scale up operation.
  + availability_zone: The availability zone is of the form: zone:host allowing user to specify the compute host for deployment.
  + volume_size: The size of cinder volumes to be attached to each resource.
  + network_id: The ID or name of network whose subnets will be used for booting the instance.
  + key: The keypair name used to ssh into the vms.

2. The "resource_registry" maps one resource to another. The resource_registry section should specify the absolute path of the particular resource definition when mapping it to another resource.
  + "resource name to map to": "absolute path of resource which is to be mapped"

Installation
------------

##### Step 1: Clone repo in /opt:
```shell
git clone https://github.com/osic/ops-workload-framework.git /opt/ops-workload-framework
```

##### Step 2: Install Workload Framework:
```shell
cd /opt/ops-workload-framework/heat_workload/
python setup.py install
```

##### Step 3: Check Workload Framework:
```shell
workload_def --help
```

Workload Framework
------------------

A python wrapper is created which will perform most of the operations of workload generation which involves defining, deleting and scaling.
The wrapper also validates quotas while creation and scaling and terminates operation at runtime if existing quotas are insufficient.
The credentials required for connecting to exisitng Openstack deployment should be stored as environment variables.
```shell
#Create Context (will create Ubuntu 14.04 image, network, flavor and keypair)
workload_def create-context --ext <name-of-external-network>

#Check quotas before creating workloads (Recommended) 
workload_def check-quota

#List workload
workload_def workload-list

#Create Workload 
workload_def create --name <name-of-stack> -n <num-of-slices> --host <compute-hostname>/--group <ansible-group-name>/<none> --slice <name-of-slice> --envt <name-of-environment> 

#Check status of workload creation:
workload_def check-status --name <name-of-workload>

#Scale-up workload
workload_def scale -sf <scaling-factor> --name <name-of-workload>

#Delete Workload and context environment
workload_def workload-delete --name <name_of_workload>
```


To Do Items
-----------
+ Creating control plane plugins for all core services.
+ Creating API monitoring module
