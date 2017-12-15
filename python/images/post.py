
##**********************************************************************************************
##                                       Accessing PHIS WS with a python api
##
## Author(s): Morgane Vidal, Guilhem HEINRICH, Anne TIREAU
## Copyright - INRA - 2017
## Creation date: December 2017
## Contact: morgane.vidal@inra.fr, anne.tireau@inra.fr, pascal.neveu@inra.fr
## Last modification date:  December, 2017
## Subject: Accessing PHIS's webservice with python API
##**

import requests, json, csv, os.path, hashlib, pytz
from datetime import datetime

host = 'http://127.0.0.1:8084/phisAPI/rest/'

################################################################################
## Token generation
headers = { 'Content-Type': 'application/json',
'accept' : 'application/json',
}
data = {
    'grant_type': 'password',
    'username': 'username',
    'password': 'password',
    'client_id': 'string'
}

json_data = json.dumps(data).encode('utf-8')

url = host + 'brapi/v1/token'
response = requests.post(url, headers = headers, data = json_data)
print(response.text + "\n")

token = response.json()['access_token'];

print (token + "\n")


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

csvfile = open("file.csv","rb")

lecteur = csv.reader(csvfile)

print u"premiere ligne =", lecteur.next(), "\n"

for ligne in lecteur:
    #metadata images
    imagepath = ligne[0]
    concerneduri = ligne[1]
    position = ligne[3]
    date = ligne[4]
    imagetype = ligne[5]
    concernedtype = ligne[6]    
    datetosend = datetime.strptime(date, "%d/%m/%Y %H:%M")
    tz =  pytz.timezone('Europe/Paris')
    datetosend = datetosend.replace(tzinfo = tz)
    dateforwebservice = datetosend.strftime("%Y-%m-%d %I:%M:%S%z")
    
    #file informations (checksum + extension)
    imagetosend = open(imagepath, "r")
    extension = os.path.splitext(imagepath)[1][1:]
    checksum = hashlib.md5(open(imagepath, "r").read()).hexdigest()
    
    #send image metadata to webservice
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
      "position": position
    },
    "fileInfo": {
      "checksum": checksum,
      "extension": extension
    }
    }]
  
    json_data = json.dumps(data).encode('utf-8')

    response = requests.post(urlimagemetadata, headers=headersimagemetadata, data=json_data)
    fileuploadurl = json.loads(response.text)['metadata']['datafiles'][0]
    print fileuploadurl, "\n"
  
      #send file to webservice
    response = requests.post(fileuploadurl, headers=headersimageupload, data=imagetosend)
#    print(response.text)
  
    imagetosend.close()
  
csvfile.close() 