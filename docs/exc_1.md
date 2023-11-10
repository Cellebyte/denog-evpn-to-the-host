# SIMPLE exc_1: Lets find out how we can advertise a new route to our servers.

## Goal

We want to achieve a new route in Vrf_one.
The Route should be an ipv6 unicast route.

* `fd10::3/128`

```bash
sudo podman exec -ti clab-containerlab-test-setup-srv1 bash
# FRR
vtysh
srv1$ show ipv6 route vrf Vrf_one
Codes: K - kernel route, C - connected, S - static, R - RIPng,
       O - OSPFv3, I - IS-IS, B - BGP, N - NHRP, T - Table,
       v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

VRF Vrf_one:
B>* fd10::1/128 [20/0] via ::ffff:c0a8:1, br.one onlink, weight 1, 02:48:48
  *                    via ::ffff:c0a8:2, br.one onlink, weight 1, 02:48:48
B>* fd10::3/128 [20/0] via ::ffff:c0a8:1, br.one onlink, weight 1, 00:00:04
  *                    via ::ffff:c0a8:2, br.one onlink, weight 1, 00:00:04

exit
# IP route
root@srv1:/$ ip vrf list
Name              Table
-----------------------
Vrf_internet        42
Vrf_mgmt            20
Vrf_one              1 ## <- our vrf
Vrf_two              2
Vrf_underlay       250

root@srv1:/$ ip -6 route show table 1
fd10::1 nhid 26869 proto bgp metric 20 pref medium
	nexthop via ::ffff:192.168.0.1 dev br.one weight 1 onlink
	nexthop via ::ffff:192.168.0.2 dev br.one weight 1 onlink
fd10::3 nhid 26869 proto bgp metric 20 pref medium
	nexthop via ::ffff:192.168.0.1 dev br.one weight 1 onlink
	nexthop via ::ffff:192.168.0.2 dev br.one weight 1 onlink
anycast fe80:: dev one_def proto kernel metric 0 pref medium
local fe80::bcfc:96ff:fe67:813c dev one_def proto kernel metric 0 pref medium
fe80::/64 dev one_def proto kernel metric 256 pref medium
multicast ff00::/8 dev one_def proto kernel metric 256 pref medium
multicast ff00::/8 dev br.one proto kernel metric 256 pref medium
```

## [Find the solution](solutions/exc_1.md)
