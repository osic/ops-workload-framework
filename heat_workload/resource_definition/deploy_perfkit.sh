sed -i '1s/^/nameserver 8.8.8.8 /' /etc/resolv.conf
sudo apt-get udpate
sudo apt-get install git
git clone https://github.com/GoogleCloudPlatform/PerfKitBenchmarker.git
sudo pip install -r PerfKitBenchmarker/perfkitbenchmarker/providers/openstack/requirements.txt
