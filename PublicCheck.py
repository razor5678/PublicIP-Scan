__author__ = "Sudev Kurur"
__version__ = "0.1"
__maintainer__ = "Sudev Kurur"
__email__ = "skurur@rapid7.com"
__status__ = "Version 1"

#This script looks at the default Insight "Compute Instance With Public IP Attached (backoffice:536)" 
#and fetches all the public IP's from InsightCloudSec. It then runs a scan for a particular port 
#(tested for TCP 22 and 3389) and validates if these IP's are actually accessible over the internet.
#If the IP's are NOT publicly accessible, then a InsightCloudSec data collection is created with the current 
#timestamp is created. This data collection can then be used to ignore Public IP's which are not accessible
#when using an appropriate Insight

import json
import requests
import socket
import time

#Change the base_URL, apikey and scan_port (tested for TCP 22 / 3389)
#If scan_port changed to 22, change the datacollection_name variable to SSH
base_url = '<Add ICS URL here>'
apikey = '<Add API Key here>'
scan_port = 3389
datacollection_name= "RDP"

#Setting other variables
socket.setdefaulttimeout(1.0)
IP = []
Not_Public_IP = []
timestr = time.strftime("%Y%m%d-%H%M%S")
insight_id = "backoffice:536"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    'Api-Key': apikey
}
#This function queries the default Insight "Compute Instance With Public IP Attached (backoffice:536)" 
#and returns all the details for the resources and handles pagination. 

def resource_query(cursor):
    # v3 supports up to 1000 resources per call
    payload= {
                "selected_resource_type": "instance",
                "resource_types": ["instance"],
                "offset": 0,
                "limit": 1000,
                "insight": insight_id,
                "insight_exemptions": bool("false")
            }
    if cursor:
        payload['cursor'] = cursor
    response = requests.post(
        url=base_url + '/v3/public/resource/query',
        data=json.dumps(payload),
        headers=headers
    )
    return response.json()

#This function takes the Public IP's from the default Insight "Compute Instance With Public IP Attached (backoffice:536)" 
#and checks if the IP is publicly accessible

def check_public(IP=IP):
    for y in IP:
        create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destination = (y, scan_port)
        result = create_socket.connect_ex(destination)
        if result == 0:
            create_socket.close()
        else:
            create_socket.close()
            Not_Public_IP.append(y)
    return Not_Public_IP

#This function takes the list of Public IP's that are NOT accessible over the internet and creates an
#InsightCloudSec data collection

def create_datacollection(Not_Public_IP):
     url=base_url + '/v2/datacollections/?detailed_counts=true'
     dict = {}
     for x in Not_Public_IP:
         key_value = {x:"Not accesible externally to "+ str(scan_port)}
         dict.update(key_value)   
     payload = {
        "collection_data": dict,
        "collection_name": datacollection_name + timestr
        }
     response = requests.post(
          url= url,
          data=json.dumps(payload),
          headers=headers
      )

#The main script starts here
try:
    print("\033[1;32;40m############Executing Python script to validate Public exposure############\n")     
    cursor = None
    while True:
        response = resource_query(cursor)
        cursor = response.get('next_cursor', False)
        #print(cursor)
        if cursor:
            for x in response['resources']: 
                IP.append(x['instance']['public_ip_address'])
        else:
            for x in response['resources']:
                IP.append(x['instance']['public_ip_address'])
            print("Public IP List for all compute instances from InsightCloudSec Insight " + str(insight_id) + "\n" + str(IP))
            break

    Not_Public_IP = check_public(IP)
    print ("\nPublic IP's which are not accesible to port " + str(scan_port)+ " externally\n" + str(Not_Public_IP))
    if not Not_Public_IP:
        print("\nAll Public IP's from the Insight " + str(insight_id) + "are publicly accessible")
        print("\nNo Data Collection Created")
        print("\n#############################END###########################################")
    else:
        print("\nCreating Data Collection in InsightCloudSec with list of Public IP's which are not accessible over the internet over port "+str(scan_port))
        create_datacollection(Not_Public_IP)
        print("\nData Collection created, login to the InsightCloudSec UI to view the same")
        print("\nData Collection Name: "+ "\033[1;37;40m" + str(datacollection_name + timestr))    
        print("\n\033[1;32;40mSelect the data collection on InsightCloudSec UI for the Insight to ignore the Public IP's which are not accessible")
        print("\n\033[1;32;40m#############################END###########################################")
except:
    print("\033[1;31;40mERROR: Something wrong with the script, please check API Keys")


