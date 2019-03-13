#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##**********************************************************************************************
##                                       Accessing PHIS WS with a python api
##
## Author(s): Morgane Vidal, Guilhem HEINRICH, Anne TIREAU
## Copyright - INRA - 2017
## Creation date: December 2017
## Contact: morgane.vidal@inra.fr, anne.tireau@inra.fr, pascal.neveu@inra.fr
## Last modification date:  March, 2019
## Subject: Accessing PHIS's webservice with python API and insert images
## from a given csv file
##**

import requests, json, csv, os.path, hashlib, pytz
import ntpath
import mimetypes
from datetime import datetime

host = 'http://localhost:8080/phis2ws/rest/'
fileName = "POSTImages-template.csv";

################################################################################
## Token generation
headers = { 'Content-Type': 'application/json',
'accept' : 'application/json',
}

data = {
    'grant_type': 'password',
    'username': 'admin@opensilex.org',
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
    "label": "test-provenance",
    "comment":  "Python script",
    "metadata": {}
})

json_provenance = json.dumps(provenances)

response = requests.post(serviceUrl, headers=headersMetadata, data=json_provenance)


provenanceUri = json.loads(response.text)['metadata']['datafiles'][0]

print(provenanceUri)
  

################################################################################
## Post images

urlfilepost = host + 'data/file'

headersfilepost = {
'accept' : 'application/json',
'Authorization':'Bearer ' + token
}

csvfile = open(fileName,"r", encoding='utf-8')

colimagepath = 0
colimagetype = 1
colconcernedItemUri = 2
colconcernedItemType = 3
colposition = 4
coldate = 5
colsensoruri = 6

reader = csv.reader(csvfile)

next(reader)

for line in reader:
    #metadata images
    imagepath = line[colimagepath]
    imagetype = line[colimagetype]
    concernedItemUri = line[colconcernedItemUri]
    concernedItemType = line[colconcernedItemType]
    position = line[colposition]
    sensor = line[colsensoruri]
    date = line[coldate]
    datetosend = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    tz =  pytz.timezone('Europe/Paris')
    datetosend = datetosend.replace(tzinfo = tz)
    dateforwebservice = datetosend.strftime("%Y-%m-%dT%H:%M:%S%z")

    imagename = ntpath.basename(imagepath)
    #file informations (checksum + extension)
    imagetosend = open(imagepath, "rb")

    filetype = mimetypes.guess_type(imagepath)
    multipart_form_data = {
      'description': ('', json.dumps({
        'rdfType': imagetype,
        'date': dateforwebservice,
        'provenanceUri': provenanceUri,
        'concernedItems': [{
          'uri': concernedItemUri,
          'typeURI': concernedItemType
        }],
        'metadata': {
          'sensor': sensor,
          'position': position
        }
      })),
      'file': (imagename, imagetosend, filetype[0])
    }

    #send file and metadata to webservice
    req = requests.Request('POST', urlfilepost, headers=headersfilepost, files=multipart_form_data)
    prepared = req.prepare()

    def pretty_print_POST(req):
      """
      At this point it is completely built and ready
      to be fired; it is "prepared".

      However pay attention at the formatting used in 
      this function because it is programmed to be pretty 
      printed and may differ from the actual request.
      """
      print('{}\n{}\n{}\n\n{}'.format(
          '-----------START-----------',
          req.method + ' ' + req.url,
          '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
          req.body,
      ))

    #pretty_print_POST(prepared)

    response = requests.Session().send(prepared)
    print(response.text)

    imagetosend.close()

csvfile.close()
