# Containerlab EVPN on the host

## Excercises

* [Exercise 1](docs/exc_1.md)
* [Exercise 2](docs/exc_2.md)

## General Info around the environment

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

Additionally you could also mount the shared folder into your VM.
This is an example for UTM on MacOS if you don't know how to mount your directory from the host system just clone it.

```bash
mkdir -p $HOME/git/containerlab-evpn-on-the-host
sudo mount -t 9p -o trans=virtio share $HOME/git/containerlab-evpn-on-the-host -oversion=9p2000.L
```

Or clone this repository:

```bash
mkdir -p $HOME/git/containerlab-evpn-on-the-host
git clone https://github.com/Cellebyte/denog-evpn-to-the-host.git $HOME/git/containerlab-evpn-on-the-host
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

FYI: you do not need to build the container as it is already published in the ghcr.io registry

We need a container which injects some training routes into our network fabric.

```bash
cd containerlab/containers/gobgp
podman build -t ghcr.io/cellebyte/denog-evpn-to-the-host/gobgp-fabric:0.0.1 .
# this copies the image from our local user to the root user.
podman image scp $USER@localhost::ghcr.io/cellebyte/denog-evpn-to-the-host/gobgp-fabric:0.0.1
```

### Host container

FYI: you do not need to build the container as it is already published in the ghcr.io registry

```bash
cd containerlab/containers/netplanner-frr
podman build -t ghcr.io/cellebyte/denog-evpn-to-the-host/netplanner-frr-fabric:0.0.1 .
# this copies the image from our local user to the root user.
podman image scp $USER@localhost::ghcr.io/cellebyte/denog-evpn-to-the-host/netplanner-frr-fabric:0.0.1
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
```console
~$ cd containerlab
~$ sudo containerlab deploy --runtime podman --reconfigure -t containerlab.yaml
> INFO[0000] Containerlab v0.47.2 started
> INFO[0000] Parsing & checking topology file: containerlab.yaml
> INFO[0000] Removing /home/tester/git/containerlab-evpn-on-the-host/containerlab/clab-containerlab-test-setup directory...
> INFO[0001] Creating lab directory: /home/tester/git/containerlab-evpn-on-the-host/containerlab/clab-containerlab-test-setup
> INFO[0007] Creating link: injector1:eth1 <--> bl1:eth1
> INFO[0011] Creating link: bl1:eth2 <--> sp1:eth1
> INFO[0017] Creating link: lf2:eth1 <--> sp1:eth4
> INFO[0019] Creating link: bl1:eth3 <--> sp2:eth1
> INFO[0020] Creating link: lf2:srv1 <--> srv1:lf2
> INFO[0020] Creating link: lf2:eth2 <--> sp2:eth4
> INFO[0033] Creating link: lf2:srv2 <--> srv2:lf2
> INFO[0033] Creating link: injector2:eth1 <--> bl2:eth1
> INFO[0034] Creating link: bl2:eth2 <--> sp1:eth2
> INFO[0035] Creating link: lf1:eth1 <--> sp1:eth3
> INFO[0036] Creating link: bl2:eth3 <--> sp2:eth2
> INFO[0036] Creating link: lf1:eth2 <--> sp2:eth3
> INFO[0037] Creating link: lf1:srv1 <--> srv1:lf1
> INFO[0038] Creating link: lf1:srv2 <--> srv2:lf1
> INFO[0046] Adding containerlab host entries to /etc/hosts file
> INFO[0046] Adding ssh config for containerlab nodes
> INFO[0646] Executed command "ip a add 192.0.2.5/32 dev lo" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv1 mtu 9100" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv1 address 00:50:56:2f:00:01" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv1 down" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv1 up" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv2 mtu 9100" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv2 address 00:50:56:2f:00:01" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv2 down" on the node "lf1". stdout:
> INFO[0646] Executed command "ip l set dev srv2 up" on the node "lf1". stdout:
> INFO[0646] Executed command "ip a add 192.168.0.4/32 dev lo" on the node "sp2". stdout:
> INFO[0646] Executed command "python3 /tool/load-routes.py" on the node "injector1". stdout:
> INFO[0646] Executed command "python3 /tool/load-routes.py" on the node "injector2". stdout:
> INFO[0646] Executed command "ip a add 192.0.2.6/32 dev lo" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv1 mtu 9100" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv1 address 00:50:56:2f:00:02" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv1 down" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv1 up" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv2 mtu 9100" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv2 address 00:50:56:2f:00:02" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv2 down" on the node "lf2". stdout:
> INFO[0646] Executed command "ip l set dev srv2 up" on the node "lf2". stdout:
> INFO[0646] Executed command "ip a add 192.168.0.3/32 dev lo" on the node "sp1". stdout:
> INFO[0646] Executed command "python3 /create-intfs.py 192.168.0.1" on the node "bl1". stdout:
> INFO[0646] Executed command "python3 /create-intfs.py 192.168.0.2" on the node "bl2". stdout:
> +----+----------------------------------------+--------------+-------------------------------------------+-------+---------+-----------------+-----------------------+
> | #  |                  Name                  | Container ID |                   Image                   | Kind  |  State  |  IPv4 Address   |     IPv6 Address      |
> +----+----------------------------------------+--------------+-------------------------------------------+-------+---------+-----------------+-----------------------+
> |  1 | clab-containerlab-test-setup-bl1       | 66372aab905d | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.34/24 | 2001:172:20:20::22/64 |
> |  2 | clab-containerlab-test-setup-bl2       | 62b2eda61478 | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.40/24 | 2001:172:20:20::28/64 |
> |  3 | clab-containerlab-test-setup-injector1 | d5d36a34ccfb | cellebyte.de/gobgp-fabric:latest          | linux | running | 172.20.20.32/24 | 2001:172:20:20::20/64 |
> |  4 | clab-containerlab-test-setup-injector2 | 4a8cc6dd2482 | cellebyte.de/gobgp-fabric:latest          | linux | running | 172.20.20.33/24 | 2001:172:20:20::21/64 |
> |  5 | clab-containerlab-test-setup-lf1       | 5bdd57bd763f | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.41/24 | 2001:172:20:20::29/64 |
> |  6 | clab-containerlab-test-setup-lf2       | c8a7a747c4d4 | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.36/24 | 2001:172:20:20::24/64 |
> |  7 | clab-containerlab-test-setup-sp1       | 537694f27f3b | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.35/24 | 2001:172:20:20::23/64 |
> |  8 | clab-containerlab-test-setup-sp2       | 24b5f1bb8bde | quay.io/frrouting/frr:9.0.1               | linux | running | 172.20.20.37/24 | 2001:172:20:20::25/64 |
> |  9 | clab-containerlab-test-setup-srv1      | f2b9e8eef317 | cellebyte.de/netplanner-frr-fabric:latest | linux | running | 172.20.20.38/24 | 2001:172:20:20::26/64 |
> | 10 | clab-containerlab-test-setup-srv2      | b90209ad2334 | cellebyte.de/netplanner-frr-fabric:latest | linux | running | 172.20.20.39/24 | 2001:172:20:20::27/64 |
> +----+----------------------------------------+--------------+-------------------------------------------+-------+---------+-----------------+-----------------------+
```

Now you should be able to investigate your lab.

```console
# Show your running containers. 
~$ sudo podman ps
> CONTAINER ID  IMAGE                                      COMMAND               CREATED         STATUS         PORTS       NAMES
> 8e2a5ed8a694  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-sp1
> 6c473024ad3e  cellebyte.de/gobgp-fabric:latest                                 26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-injector2
> 87b911b50842  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-bl1
> 639094d42858  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-sp2
> 2f5f8378fc68  cellebyte.de/netplanner-frr-fabric:latest  /sbin/init            26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-srv2
> ea3cfa58a440  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-lf2
> 0bc9a59137fc  cellebyte.de/netplanner-frr-fabric:latest  /sbin/init            26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-srv1
> 6c454ff0f697  cellebyte.de/gobgp-fabric:latest                                 26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-injector1
> 03419523f000  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-lf1
> eb062c15f843  quay.io/frrouting/frr:9.0.1                /usr/lib/frr/dock...  26 minutes ago  Up 26 minutes              clab-containerlab-test-setup-bl2
```

## The LAB

### General information

#### LoopBack Networks BGP Router ID Ranges

* Switches: 192.168.0.0/24
* Servers: 192.168.255.0/24

#### Node Overlay Network (e.g):
* IPv4: 10.255.255.0/24
  * **srv1**: 10.255.255.1/32
  * **srv2**: 10.255.255.2/32
* IPv6: fc00::/64
  * **srv1**: fc00::1/128
  * **srv2**: fc00::2/128

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

