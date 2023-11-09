# Containerlab EVPN on the host

We use Ubuntu 22.04.03 LTS **Server** as our image for the guide.

It can be downloaded [here](https://releases.ubuntu.com/jammy/)

Please install the machine.

Clone this repository locally to your machine.

Destination could be something like `$HOME/git/containerlab-evpn-on-the-host`.

Internet should work on your VM/Machine without a proxy.

## Windows
not supported as I don't have a device to verify it.
I think HyperV or VirtualBox could be used to setup an Ubuntu Server 22.04.03 VM as mentioned above.

## MacOS

Install [UTM](https://docs.getutm.app/installation/macos/).

Setup the VM with the following settings.

![](./images/settings-on-macos.png)

## Install Ubuntu in your VM.

1. Choose the standard installation.
2. Use the default settings everywhere.
3. Use the curated package suite.
4. Use the full disk and do not encrypt it.
5. **username**: tester
6. **password**: tester
7. **hostname**: server

I you have a VM enable password authentication for ssh to allow to connect to it from your host system via ssh.

```ssh-config
PasswordAuthentication=yes
MaxAuthTries 15 # if you have a lot of ssh-keys.
```

Additionally you could also mount the shared folder into your VM

```bash
mkdir -p $HOME/git/containerlab-evpn-on-the-host
sudo mount -t 9p -o trans=virtio share $HOME/git/containerlab-evpn-on-the-host -oversion=9p2000.L
```

Or clone this repository:

```bash
git clone https://github.com/Cellebyte/denog-evpn-to-the-host.git
```

## Install requirements for our lab

### Arch/Manjaro

```bash
yay -S containerlab-bin podman python-poetry
```

Please follow the podman guide in the [ArchLinux wiki](https://wiki.archlinux.org/title/Podman).

### Others

**IDK**

### Ubuntu/Debian

```bash
## adds containerlab repository
echo "deb [trusted=yes] https://apt.fury.io/netdevops/ /" | \
sudo tee -a /etc/apt/sources.list.d/netdevops.list

## adds podman repository
echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/unstable/xUbuntu_22.04/ /' | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:unstable.list
curl -fsSL https://download.opensuse.org/repositories/devel:kubic:libcontainers:unstable/xUbuntu_22.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/devel_kubic_libcontainers_unstable.gpg > /dev/null

sudo apt update && sudo apt install containerlab podman curl git gnupg

systemctl start podman.socket

## if you get an masked service error

systemctl unmask podman.service
systemctl unmask podman.socket
systemctl start podman.socket

# check if subuid and subgid are correctly set
# /etc/subuid
# $USER:100000:65536

# /etc/subgid
# $USER:100000:65536
# If not run the following two commands.
usermod --add-subuids 65536-100000 --add-subgids 65536-100000 $USER
podman system migrate
```

additional installation methods can be found here ->
* ref: [ContainerLab Package Managers](https://containerlab.dev/install/#package-managers)

## Setup of the LAB

### General Description
Now that you have a VM or local running `podman` and `containerlab` cli available we can start with the building of some containers.

Every manual which is written in this guide assumes that you are in the root of this git project.

### Injector container

We need a container which injects some training routes into our network fabric.

```bash
cd containerlab/containers/gobgp
podman build -t cellebyte.de/gobgp-fabric:latest .
# this copies the image from our local user to the root user.
podman image scp $USER@localhost::cellebyte.de/gobgp-fabric:latest
```

### Host container

```bash
cd containerlab/containers/netplanner-frr
podman build -t cellebyte.de/netplanner-frr-fabric:latest .
# this copies the image from our local user to the root user.
podman image scp $USER@localhost::cellebyte.de/netplanner-frr-fabric:latest
```

### Getting a full-table from RIPE

1. If you want to try it you can run the script which generates the routes.
```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -
# load the poetry binary into the PATH
source $HOME/.profile
# install dependencies
poetry install --no-root
# instantiate a shell with all 
poetry shell
cd containerlab
# generate our sample routes for the environment
python scripts/route-dicer.py
cd ..
```

2. If you are not a programmer just copy the example files into place.

```bash
cp example-ipv4.json ipv4.json
cp example-ipv6.json ipv6.json
```

### Instantiating the lab.

Finally we can start with the lab.
```bash
cd containerlab
sudo containerlab deploy --runtime podman --reconfigure -t containerlab.yaml
```

Now you should be able to investigate your lab.

```console
# Show your running containers. 
$ sudo podman ps
CONTAINER ID  IMAGE                                      COMMAND               CREATED         STATUS         PORTS       NAMES
8e2a5ed8a694  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-sp1
6c473024ad3e  cellebyte.de/gobgp-fabric:latest                                 26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-injector2
87b911b50842  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-bl1
639094d42858  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-sp2
2f5f8378fc68  cellebyte.de/netplanner-frr-fabric:latest  /sbin/init            26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-srv2
ea3cfa58a440  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-lf2
0bc9a59137fc  cellebyte.de/netplanner-frr-fabric:latest  /sbin/init            26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-srv1
6c454ff0f697  cellebyte.de/gobgp-fabric:latest                                 26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-injector1
03419523f000  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-lf1
eb062c15f843  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-bl2
```

## The LAB

### General information

#### LoopBack Networks BGP Router ID Ranges
* Switches: 192.168.0.0/24
* Servers: 192.168.255.0/24

#### Node Overlay Network (e.g):
* IPv4: 10.255.255.0/24
* IPv6: fc00::/64

#### Peering Networks
* fc80:cafe:{vlan}::0/126
* 192.168.{vlan}.0/30
* {vlan} calculated counting upwards from 100 by the vrf keys in `routes/ipv4.json` and `routes/ipv6.json`
  * 192.168.{vlan}.1/30 <-> 192.168.{vlan}.2/30
  * fc80:cafe:{vlan}::1/126 <-> fc80:cafe:{vlan}::2/126

#### Routes per VRF

If you have performance issues. I suggest reducing the injected routes.
This can be changed in the `network_map` in the folder `containerlab/scripts/route-dicer.py`.

* Vrf_one
  * IPv4: 192.168.255.255/32
  * IPv6: fd10::1/128
* Vrf_two
  * IPv4: 192.168.254.254/32
  * IPv6: fd10::2/128
* Vrf_mgmt
  * IPv4: 10.0.0.0/9 evenly splitted into /13
  * IPv6: fc00::/8 evenly splitted into /12
* Vrf_internet (we will use a full-table)
  * IPv4: 0.0.0.0/0
  * IPv6: ::/0

#### Visualization

This visualizes your containerlab via a webserver.

```bash
sudo containerlab graph --runtime podman  -t containerlab.yaml
# if you have a local installation
# e.g.
localhost:50080
# if you use an vm. connect to the ip of the vm
# e.g.
192.168.64.2:50080
```