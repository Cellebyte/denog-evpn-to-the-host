#!/usr/bin/env python
import ipaddress
import random
import json
import mrtparse
import gzip
import requests
from pathlib import Path
from typing import List
vni_map = {
    "Vrf_one": 1,
    "Vrf_two": 2,
    "Vrf_mgmt": 20,
    "Vrf_internet": 42
}
## Networks which are used for the Route-Dicer

network_map = {
    "Vrf_one": {
        "ipv4": "192.168.255.255/32",
        "ipv6": "fd10::1/128",
        "ipv4_slicer": 32,
        "ipv6_slicer": 128,
        "as_numbers": [65552],

    },
    "Vrf_two": {
        "ipv4": "192.168.254.254/32",
        "ipv6": "fd10::2/128",
        "ipv4_slicer": 32,
        "ipv6_slicer": 128,
        "as_numbers": [65536],
    },
    "Vrf_mgmt": {
        "ipv4": "10.0.0.0/9",
        "ipv6": "fd00::/8",
        "ipv4_slicer": 13,
        "ipv6_slicer": 12,
        "as_numbers": range(65536,65552),
    },
    "Vrf_internet": {} # this currently uses a full-table from ripe.
}

vrf_routes_ipv4 = {}
vrf_routes_ipv6 = {}



def get_internet_routes():
    data = requests.get("https://data.ris.ripe.net/rrc00/2023.10/updates.20231031.1630.gz", stream=True)

    if data.status_code == 200:
        return [entry.data for entry in mrtparse.Reader(gzip.GzipFile(fileobj=data.raw))]
    else:
        return []

def get_routes_from_mrt():
    routes_ipv4 = {}
    routes_ipv6 = {}
    for route in get_internet_routes():
        ipv4 = False
        # if "IPv4" in route["afi"].values():
        if "bgp_message" in route.keys() and "path_attributes" in route["bgp_message"].keys():
            as_path = []
            nlri = []
            communities = []
            for attribute in route["bgp_message"]["path_attributes"]:
                if "MP_REACH_NLRI" in attribute["type"].values():
                    nlri = attribute["value"]["nlri"]
                elif "AS_PATH" in attribute["type"].values():
                    for subattribute in  attribute["value"]:
                        if "AS_SEQUENCE" in subattribute["type"].values():
                            as_path = subattribute["value"]
                            break
                elif "COMMUNITY" in attribute["type"].values():
                    communities = attribute["value"]
            if "nlri" in route["bgp_message"].keys() and route["bgp_message"]["nlri"] and not nlri:
                nlri = route["bgp_message"]["nlri"]
                ipv4 = True
            if nlri:
                routes = routes_ipv6
                if ipv4:
                    routes = routes_ipv4
                for ip_route in nlri:
                    ip_route_network = ipaddress.ip_network(f'{ip_route["prefix"]}/{ip_route["length"]}')
                    if ip_route_network not in routes.keys():
                        routes[ip_route_network] = [{
                            "route": route,
                            "communities": communities,
                            "as_path": as_path
                        }]
                    else:
                        routes[ip_route_network].append({
                            "route": route,
                            "communities": communities,
                            "as_path": as_path
                        })
        else:
            # print("No NLRI information here!")
            # print(json.dumps(route, indent=2))
            pass

    return routes_ipv4, routes_ipv6

def gen_as_path(sample=[]) -> List[str]:
    return [str(integer) for integer in random.sample(sample, random.randint(1, len(sample)))]

for vrf in vni_map.keys():
    if vrf not in network_map.keys():
        continue
    networks = network_map[vrf]
    routes_ipv4 = []
    routes_ipv6 = []
    routes_ipv4_info = routes_ipv6_info = {}
    as_numbers = []
    if networks:
        py_network_ipv4 = ipaddress.ip_network(networks["ipv4"])
        routes_ipv4 = list(py_network_ipv4.subnets(new_prefix=networks.get("ipv4_slicer", 24)))
        py_network_ipv6 = ipaddress.ip_network(networks["ipv6"])
        routes_ipv6 = list(py_network_ipv6.subnets(new_prefix=networks.get("ipv6_slicer", 18)))
        as_numbers = list(networks["as_numbers"])
    else:
        routes_ipv4_info, routes_ipv6_info = get_routes_from_mrt()
        routes_ipv4 = routes_ipv4_info.keys()
        routes_ipv6 = routes_ipv6_info.keys()
    vrf_routes_ipv4[vrf] = {
        "routes": {
            str(route): [
                {
                    "valid": True,
                    "bestpath": True,
                    "pathFrom": "external",
                    "prefix": str(route.network_address),
                    "prefixLen": route.prefixlen,
                    "network": str(route),
                    "metric":45,
                    "weight":0,
                    "path": " ".join(gen_as_path(sample=as_numbers) if not routes_ipv4_info.get(route,[]) else routes_ipv4_info[route][0]["as_path"]),
                    "origin":"IGP",
                    "nexthops":[
                    {
                        "ip": "0.0.0.0",
                        "afi": "ipv4",
                        "used": True
                    }
                    ]
                },
            ]
            for route in routes_ipv4
        }
    }
    vrf_routes_ipv6[vrf] = {
        "routes": {
            str(route): [
                {
                    "valid": True,
                    "bestpath": True,
                    "pathFrom": "external",
                    "prefix": str(route.network_address),
                    "prefixLen": route.prefixlen,
                    "network": str(route),
                    "metric":45,
                    "weight":0,
                    "path": " ".join(gen_as_path(sample=as_numbers) if not routes_ipv6_info.get(route,[]) else routes_ipv6_info[route][0]["as_path"]),
                    "origin":"IGP",
                    "nexthops":[
                    {
                        "ip": "::",
                        "afi": "ipv6",
                        "used": True
                    }
                    ]
                },
            ]
            for route in routes_ipv6
        }
    }


with open(Path("./routes") / "ipv4.json", "w") as file:
    json.dump(vrf_routes_ipv4, file, indent=2)
with open(Path("./routes") / "ipv6.json", "w") as file:
    json.dump(vrf_routes_ipv6, file, indent=2)
