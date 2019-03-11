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
from datetime import datetime
from pprint import pprint

import requests, json, csv, hashlib, pytz


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
## Post provenance

serviceUrl = host + 'provenances'

headersMetadata = { 
    'Content-Type': 'application/json',
    'accept' : 'application/json',
    'Authorization':'Bearer ' + token
}


provenances = []
provenances.append({
    "label": "provenance-label",
    "comment":  "provenance-comment",
    "metadata": {}
})

json_provenance = json.dumps(provenances)

response = requests.post(serviceUrl, headers=headersMetadata, data=json_provenance)


provenanceUri = json.loads(response.text)['metadata']['datafiles'][0]

pprint(provenanceUri)
  

################################################################################
## Post data

serviceUrl = host + 'data'

headersMetadata = { 
    'Content-Type': 'application/json',
    'accept' : 'application/json',
    'Authorization':'Bearer ' + token
}

csvfile = open("POSTData-template.csv","r",encoding='utf-8')

colDate = 0
colVariable = 1
colObject = 2
colValue = 3

reader = csv.reader(csvfile, delimiter=";")

# skip headers
next(reader)

data = []
for line in reader:
    dateValue = line[colDate]
    variableUri = line[colVariable]
    objectUri = line[colObject]
    value = line[colValue]
    
    dateToSend = datetime.strptime(dateValue, "%Y-%m-%d %H:%M:%S")
    tz =  pytz.timezone('Europe/Paris')
    dateToSend = dateToSend.replace(tzinfo = tz)
    dateForWebservice = dateToSend.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    data.append({
        "provenanceUri": provenanceUri,
        "objectUri": objectUri,
        "variableUri": variableUri,
        "date": dateForWebservice,
        "value": value
    })

csvfile.close() 

json_data = json.dumps(data)

print(json_data)

response = requests.post(serviceUrl, headers=headersMetadata, data=json_data)

status = json.loads(response.text)['metadata']['status']

pprint(status)
  