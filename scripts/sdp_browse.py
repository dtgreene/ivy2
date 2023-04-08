import sys

import bluetooth

if len(sys.argv) < 2:
    print("Usage: sdp-browse.py <addr>")
    print("   addr - can be a bluetooth address, \"localhost\", or \"all\"")
    sys.exit(2)

target = sys.argv[1]
if target == "all":
    target = None

services = bluetooth.find_service(address=target)

if len(services) > 0:
    print("Found {} services on {}.".format(len(services), sys.argv[1]))
else:
    print("No services found.")

for svc in services:
    print("\nService Name:", svc["name"])
    print("    Host:       ", svc["host"])
    print("    Description:", svc["description"])
    print("    Provided By:", svc["provider"])
    print("    Protocol:   ", svc["protocol"])
    print("    channel/PSM:", svc["port"])
    print("    svc classes:", svc["service-classes"])
    print("    profiles:   ", svc["profiles"])
    print("    service id: ", svc["service-id"])
