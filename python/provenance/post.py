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

import requests, json, csv, hashlib


host = 'http://localhost:8084/phis2ws/rest/'

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
## Post provenance

serviceUrl = host + 'provenances'

headersMetadata = { 
    'Content-Type': 'application/json',
    'accept' : 'application/json',
    'Authorization':'Bearer ' + token
}

csvfile = open("POSTProvenance-template.csv","r",encoding='utf-8')

colLabel = 0
colComment = 1
colsMetadata = {}

reader = csv.reader(csvfile, delimiter=";")

# Get the header
headers = next(reader)
numberOfColumns = 0
for cel in headers:
    if cel == "label":
        colLabel = numberOfColumns
    elif cel == "comment":
        colComment = numberOfColumns
    else:
        colsMetadata[numberOfColumns]=cel
    
    numberOfColumns += 1


data = []
for line in reader:
    labelValue = line[colLabel]
    commentValue = line[colComment]
    metadataValue = {}
    for col in range(0, numberOfColumns):
        if col != colLabel and col != colComment and line[col] not in (None, "") :
            metadataValue[colsMetadata[col]] = line[col]
    
    data.append({
        "label": labelValue,
        "comment": commentValue,
        "metadata": metadataValue
    })

csvfile.close() 

json_data = json.dumps(data)

response = requests.post(serviceUrl, headers=headersMetadata, data=json_data)

status = json.loads(response.text)

pprint(status)
  

