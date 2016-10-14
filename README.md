### ops-workload-framework:

### About this Repository

This is a repository for artifacts realted to generating Workload slices  and autoscaling those slices based on resource utilization.

### Elements
+ Prerequisites
+ Resource Definition
+ Autoscaling group
+ Environment Variables
+ Create Heat Stack
+ Python Wrapper

### Prerequisites

+ An existing OpenStack Cloud on which to deploy the resources.
+ Python Heat / OpenStack Client installed and configured with credentials on host machine.
+ Horizon Dashboard (optional) to check the status of autoscaling and workload generation.

### Resource Definition

This part involves creating your own resource using Heat templates which will be deployed on the cloud. An example for this could be a RAM Intensive resource
which can host applications consuming more memory.
All resource definition are located and stored inside the "resource_definition" directory and should be specified in the "slice.yaml" file.

### Autoscaling group

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

### Environment Variables

An environment file is defined in the "environment" directory which defines the input parameters and their values in "parameter: value" format. The file is
divided into two section: 

1. The "parameters" section defines the value of the input parameters used in the resource definition and the autoscaling groups heat templates.
The parameters section should define the attributes along with their values that will be used for booting each resource:

  + num_of_slice: Defines the number of slices of resources to be deployed initially while workload creation.
  + instance_type: The flavor of each resource should be specified.
  + image_id: The ID or name of a glance image which will be used to boot the instances.
  + scaling_size: The scaling factor which defines the number of slices that will be generated as a result of scale up operation.
  + availability_zone: The availability zone or region in which the slices will be deployed.
  + volume_size: The size of cinder volumes to be attached to each resource.
  + network_id: The ID or name of network whose subnets will be used for booting the instance.

2. The "resource_registry" maps one resource to another. The resource_registry section should specify the absolute path of the particular resource definition when mapping it to another resource.
  + "resource name to map to": "absolute path of resource which is to be mapped"


### Create Heat Stack

Once the resources are defined and are added into the autoscaling group, Heat stacks can be created using python heat/openstack client.

```shell
#Create Heat Stack using heat client
heat stack-create -f main.yaml -e environment/heat_param.yaml <name_of_stack>

#Create Heat Stack using openstack client
openstack stack create -t main.yaml -e environment/heat_param.yaml <name_of_stack>
```
### Python Wrapper

A python wrapper is created which will perform most of the operations of workload generation which involves defining, deleting and scaling.
The wrapper also validates quotas while creation and scaling and terminates operation at runtime if existing quotas are insufficient.
The credentials required for connecting to exisitng Openstack deployment should be stored as environment variables.
```shell
#Install python wrapper
python setup.py install

#Create Context (will create Ubuntu 14.04 image, network and flavor)
workload_def context-create

#Check quotas before creating workloads (Recommended)
workload_def quota-check

#Create Workload
workload_def workload-create -name <name_of_workload> -n <num_of_slices>

#Check status of workload creation:
workload_def check-status --name <name_of_workload>

#Scale-up workload
workload_def scale-up -sf <scaling-factor> --url <Webhook URL>

#Delete Workload and context environment
workload_def workload-delete --name <name_of_workload>
```


### To Do Items

+ Some variable values in the environment file (Image, Instance Type) are not being reflected in the individual resource definition. Debugging the cause for the same. -- done
+ Adding feature for  deleting workload, view status of workload, and having the scale-up perform scaling up by just specifying the workload name. --done
