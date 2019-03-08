#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##**********************************************************************************************
##                                       Accessing PHIS WS with a python api
##
## Author(s): Mogane VIDAL, Vincent MIGOT, Anne TIREAU
## Copyright - INRA - 2018
## Contact: vincent.migot@inra.fr, morgane.vidal@inra.fr, anne.tireau@inra.fr, pascal.neveu@inra.fr
## Last modification date:  November, 2018
## Subject: Accessing PHIS's webservice with python API and insert environment data
## from a given csv file
##**

# /!\ Script written in python 3 /!\
from pprint import pprint

import requests, json, hashlib


host = 'http://localhost:8080/phis2ws/rest/'

################################################################################
## Token generation
headers = { 
    'Content-Type': 'application/json',
    'accept' : 'application/json',
}

data = {
    'grant_type': 'password',
    'username': 'admin@phis.fr',
    'password': hashlib.md5('admin'.encode('utf-8')).hexdigest(),
    'client_id': 'string'
}

json_data = json.dumps(data).encode('utf-8')

url = host + 'brapi/v1/token'
response = requests.post(url, headers = headers, data = json_data)
print(response.text + "\n")

token = response.json()['access_token'];

print ("token : " + token + "\n")
  
################################################################################
## Get data by variable uri

serviceUrl = host + 'data'

headersMetadata = { 
    'Content-Type': 'application/json',
    'accept' : 'application/json',
    'Authorization':'Bearer ' + token
}

variableUri = 'http://www.phenome-fppn.fr/test/id/variables/v008'

headers = { 'Content-Type': 'application/json',
'accept' : 'application/json',
'Authorization':'Bearer ' + token
 }

url = host + 'data?variable=' + variableUri

response = requests.get(url, headers=headers)

pprint(response.text)
