
##**********************************************************************************************
##                                       Accessing PHIS WS with a python api
##
## Author(s): Morgane Vidal, Guilhem HEINRICH, Anne TIREAU
## Copyright - INRA - 2017
## Creation date: December 2017
## Contact: morgane.vidal@inra.fr, anne.tireau@inra.fr, pascal.neveu@inra.fr
## Last modification date:  December, 2017
## Subject: Accessing PHIS's webservice with python API and insert images
## from a given csv file
##**

import requests, json, csv, os.path, hashlib, pytz
from datetime import datetime

host = 'http://localhost:8084/phis2ws/rest/'

################################################################################
## Token generation
headers = { 'Content-Type': 'application/json',
'accept' : 'application/json',
}

data = {
    'grant_type': 'password',
    'username': 'username',
    'password': hashlib.md5('password').hexdigest(),
    'client_id': 'string'
}

json_data = json.dumps(data).encode('utf-8')

url = host + 'brapi/v1/token'
response = requests.post(url, headers = headers, data = json_data)
print(response.text + "\n")

token = response.json()['access_token'];

print ("token : " + token + "\n")


################################################################################
## Post images

urlimagemetadata = host + 'images'

headersimagemetadata = { 'Content-Type': 'application/json',
'accept' : 'application/json',
'Authorization':'Bearer ' + token
}

headersimageupload = { 'Content-Type': 'application/octet-stream',
'accept' : 'application/json',
'Authorization':'Bearer ' + token
}

csvfile = open("POSTImages-template.csv","rb")

colimagepath = 0
colimagetype = 1
colconcerneduri = 2
colconcernedtype = 3
colposition = 4
coldate = 5
colsensoruri = 6

reader = csv.reader(csvfile)

reader.next()

for line in reader:
    #metadata images
    imagepath = line[colimagepath]
    imagetype = line[colimagetype]
    concerneduri = line[colconcerneduri]
    concernedtype = line[colconcernedtype]
    position = line[colposition]
    sensor = line[colsensoruri]
    date = line[coldate]
    datetosend = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    tz =  pytz.timezone('Europe/Paris')
    datetosend = datetosend.replace(tzinfo = tz)
    dateforwebservice = datetosend.strftime("%Y-%m-%d %H:%M:%S%z")
    
    #file informations (checksum + extension)
    imagetosend = open(imagepath, "r")
    extension = os.path.splitext(imagepath)[1][1:]
    checksum = hashlib.md5(open(imagepath, "r").read()).hexdigest()
    
    #send image metadata to webservice
    if position != "":
        data = [{
        "rdfType": imagetype,
        "concern": [
          {
            "uri": concerneduri,
            "typeURI": concernedtype
          }
        ],
        "configuration": {
          "date": dateforwebservice,
          "position": position,
          "sensor": sensor
        },
        "fileInfo": {
          "checksum": checksum,
          "extension": extension
        }
        }]
    else:
        data = [{
        "rdfType": imagetype,
        "concern": [
          {
            "uri": concerneduri,
            "typeURI": concernedtype
          }
        ],
        "configuration": {
          "date": dateforwebservice,
          "sensor": sensor
        },
        "fileInfo": {
          "checksum": checksum,
          "extension": extension
        }
        }]

    json_data = json.dumps(data).encode('utf-8')

    response = requests.post(urlimagemetadata, headers=headersimagemetadata, data=json_data)
    #print(response.text)
    fileuploadurl = json.loads(response.text)['metadata']['datafiles'][0]
    print fileuploadurl, "\n"
  
    #send file to webservice
    response = requests.post(fileuploadurl, headers=headersimageupload, data=imagetosend)
    #print(response.text)
  
    imagetosend.close()
  
csvfile.close() 