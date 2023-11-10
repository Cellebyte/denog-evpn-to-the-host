# Excercise 1 Solution

Configure both border-leafs with a blackhole route in vrf Vrf_one.
Additionally you need to also confgure the network statement in the Vrf_one bgp router section on bl1 and bl2.

## bl1

```vtysh
vrf Vrf_one
 ipv6 route fd10::3/128 blackhole
exit-vrf
!
router bgp 64497 vrf Vrf_one
 bgp router-id 192.168.0.1
 no bgp ebgp-requires-policy
 no bgp default ipv4-unicast
 neighbor 192.168.102.1 remote-as 64496
 neighbor fc80:cafe:102::1 remote-as 64496
 !
 address-family ipv4 unicast
  neighbor 192.168.102.1 activate
  neighbor 192.168.102.1 prefix-list deny_ipv4 out
 exit-address-family
 !
 address-family ipv6 unicast
  network fd10::3/128
  neighbor fc80:cafe:102::1 activate
  neighbor fc80:cafe:102::1 prefix-list deny_ipv6 out
 exit-address-family
 !
 address-family l2vpn evpn
  advertise ipv4 unicast
  advertise ipv6 unicast
 exit-address-family
exit
```
## bl2
```config
vrf Vrf_one
 ipv6 route fd10::3/128 blackhole
exit-vrf
!
router bgp 64497 vrf Vrf_one
 bgp router-id 192.168.0.1
 no bgp ebgp-requires-policy
 no bgp default ipv4-unicast
 neighbor 192.168.102.1 remote-as 64496
 neighbor fc80:cafe:102::1 remote-as 64496
 !
 address-family ipv4 unicast
  neighbor 192.168.102.1 activate
  neighbor 192.168.102.1 prefix-list deny_ipv4 out
 exit-address-family
 !
 address-family ipv6 unicast
  network fd10::3/128
  neighbor fc80:cafe:102::1 activate
  neighbor fc80:cafe:102::1 prefix-list deny_ipv6 out
 exit-address-family
 !
 address-family l2vpn evpn
  advertise ipv4 unicast
  advertise ipv6 unicast
 exit-address-family
exit
```