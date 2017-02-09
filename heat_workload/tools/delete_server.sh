#!/bin/bash
for server in `openstack server list -c ID -f value`; do
     openstack server delete $server
     echo $server
done
