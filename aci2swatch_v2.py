#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging

print("""
--------------------
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
---------------------
""")


__author__ = "Dirk Woellhaf <dwoellha@cisco.com>"
__contributors__ = [
    "Dirk Woellhaf <dwoellha@cisco.com>"
]
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

import requests
import json

try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

# Enter all authentication info
SW_USER = "dcuni"
SW_PASSWORD = "C1sco12345"
SW_HOST = "smcve-01"
SW_PARENTID = 54350
ACI_USER = "dcuni"
ACI_PASSWORD = "C1sco12345"
ACI_HOST = "sec-apic-01"

def ACI_Login(HOST,USER,PASSWORD):
    # Set the URL for SMC login
    url = "https://" + HOST + "/api/aaaLogin.json"

    login_request_data = {
        "aaaUser":{
            "attributes":{
                "name": USER,
                "pwd": PASSWORD
                }
            }
        }

    # Initialize the Requests session
    aci_session = requests.Session()

    # Perform the POST request to login
    response = aci_session.request("POST", url, verify=False, data=json.dumps(login_request_data))

    # If the login was successful
    if(response.status_code == 200):
        print("[ ACI ] Login Successful!")
        token=json.loads(response.text)  
        token=token['imdata'][0]['aaaLogin']['attributes']['token']
        #print(token)
        return token
     # If the login was NOT successful
    else:
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
        #print(response.text)   

def ACI_Logout(HOST,USER,TOKEN):
    # Set the URL for SMC login
    url = "https://" + HOST + "/api/aaaLogout.json"
    cookies = {}
    cookies['APIC-Cookie'] = TOKEN

    logout_request_data = {
        "aaaUser":{
            "attributes":{
                "name": USER
                }
            }
        }

    # Initialize the Requests session
    aci_session = requests.Session()

    # Perform the POST request to login
    response = aci_session.request("POST", url, verify=False, cookies=cookies, data=json.dumps(logout_request_data))

    # If the login was successful
    if(response.status_code == 200):
        print("[ ACI ] Logout Successful!")
     # If the login was NOT successful
    else:
        print("An error has ocurred, while logging out, with the following code {}".format(response.status_code))
        print(response.text)   

def ACI_GET(HOST, TOKEN, URL):
    # Set the URL for SMC login
    url = "https://" + HOST + "/api"+URL
    cookies = {}
    cookies['APIC-Cookie'] = TOKEN

    #print(TOKEN)
    # Initialize the Requests session
    aci_session = requests.Session()

    # Perform the POST request to login
    response = aci_session.request("GET", url, verify=False, cookies=cookies)

    # If the login was successful
    if(response.status_code == 200):
        print("[ ACI ] GET Successful!")
        #print(response.text)  
        return json.loads(response.text)
     # If the login was NOT successful
    else:
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
        #print(response.text)   

def SW_Login(HOST,USER,PASSWORD):
    # Set the URL for SMC login
    url = "https://" + HOST + "/token/v2/authenticate"

    # Let's create the loginrequest data
    login_request_data = {
        "username": USER,
        "password": PASSWORD
    }

    # Initialize the Requests session
    sw_session = requests.Session()

    # Perform the POST request to login
    response = sw_session.request("POST", url, verify=False, data=login_request_data)

    # If the login was successful
    if(response.status_code == 200):
        print("[ SW ] Login Successful!")
        #print(response.cookies)   
        return sw_session, response.cookies
     # If the login was NOT successful
    else:
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
    
def SW_Logout(SW_Session):
    uri = 'https://' + SW_HOST + '/token'
    response = SW_Session.delete(uri, timeout=30, verify=False)
    
    # If the logout was unsuccessful
    if(response.status_code == 204):
        print("[ SW ] Logout Successful!")

def SW_GetTenantId(SW_Session, HOST):
    url = 'https://' + HOST + '/sw-reporting/v1/tenants'
    request_headers = {'Content-type': 'application/json'}
    response = SW_Session.request("GET", url, verify=False, headers=request_headers)
    SW_TENANT_ID = response.json()
    return SW_TENANT_ID["data"][0]["id"]

def SW_PostNewGroups(SW_Session, HOST, SW_TenantId, SW_request_data):
    url = 'https://' + HOST + '/smc-configuration/rest/v1/tenants/' + str(SW_TenantId) + '/tags'
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = SW_Session.request("POST", url, verify=False, data=json.dumps(SW_request_data), headers=request_headers)

    #print(response.status_code)
    if (response.status_code == 200):
        print("[ SW ] New host group successfully added")  
    else:
        if("5060" in response.text):
            print("[ SW ] Adding host group failed. Group exists already?") 
            #SW_UpdateGroups(SW_Session, HOST, SW_TenantId, SW_request_data)
        else:
            print("[ SW ] Adding host group failed.")  

def SW_UpdateGroups(SW_Session, HOST, SW_TenantId, SW_request_data):
    url = 'https://' + HOST + '/smc-configuration/rest/v1/tenants/' + str(SW_TenantId) + '/tags'
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = SW_Session.request("PUT", url, verify=False, data=json.dumps(SW_request_data), headers=request_headers)

    #print(response.status_code)
    if (response.status_code == 200):
        print("[ SW ] New host group successfully updated")  
    else: 
        print(response.text)
        print("[ SW ] Updating host group failed.")  

#-------- MAIN ----------

ACI_Token = ACI_Login(ACI_HOST,ACI_USER,ACI_PASSWORD)
ACI_Endpoints = ACI_GET(ACI_HOST,ACI_Token,'/node/class/fvCEp.json')
ACI_Logout(ACI_HOST,ACI_USER,ACI_Token)

print("[ ACI ] Total Endpoints: {}".format(ACI_Endpoints["totalCount"]))

ACI_Tenants = []

# Get all Tenants with EPs learned
for Endpoint in ACI_Endpoints["imdata"]:
    # print only EP which are marked as learned
    if("learned" in Endpoint["fvCEp"]["attributes"]["lcC"]):
        Endpoint = Endpoint["fvCEp"]["attributes"]["dn"].split("/")
        ACI_Tenant = Endpoint[1]#.lstrip("tn-")
        if ACI_Tenant not in ACI_Tenants:
            ACI_Tenants.append(ACI_Tenant)

# Print Number of Tenants with learned EPs
print("[ ACI ] Tenants: {}".format(len(ACI_Tenants)))

SW_request_data = []
for Tenant in ACI_Tenants:
    EPs = 0
      
    tenant_data = {
            "name": Tenant.upper(),
            "location": "INSIDE",
            "description": "DC-Uni Import from ACI",
            "ranges": [],
            "hostBaselines": False,
            "suppressExcludedServices": True,
            "inverseSuppression": False,
            "hostTrap": False,
            "sendToCta": False,
            "parentId": SW_PARENTID
        } 

    for Endpoint in ACI_Endpoints["imdata"]:
        if Tenant in Endpoint["fvCEp"]["attributes"]["dn"] and Endpoint["fvCEp"]["attributes"]["ip"] != "0.0.0.0":
            #print("  "+Endpoint["fvCEp"]["attributes"]["ip"])
            tenant_data["ranges"].append(Endpoint["fvCEp"]["attributes"]["ip"])
            EPs +=1
    print("[ ACI ] Tenant: "+Tenant+", EPs: {}".format(EPs))
    if(EPs >= 1):
        SW_request_data.append(tenant_data)
    

SW_Session, SW_Cookies = SW_Login(SW_HOST,SW_USER,SW_PASSWORD)

SW_TenantId = SW_GetTenantId(SW_Session, SW_HOST)
print("[ SW ] Tenant ID: {}".format(SW_TenantId))
SW_PostNewGroups(SW_Session, SW_HOST, SW_TenantId, SW_request_data)

SW_Logout(SW_Session)