# Import libraries
import requests # HTTP interface
import json     # JSON interface

# Aurorisatie
AUTORISATIE = 'NNSXS.WCODVFI7XZZZDWYRQXT5R6PUD7KMTX7PTZRWT5Y.H4JNXDPJAITC2NAGETL7F6FN2CM33YEI5YQIBBXERVVMR4NHQKUQ'

# Geef applicatie, device en sensor
APPLICATION = 'demo-lth65'
DEVICE_EUI = 'eui-a84041ef7186a50f'
SENSOR = 'TempC_DS'

# Naam van csv-bestand
OUTPUT_CSV_FILE = 'c:/temp/ttn_sensor_output.csv'

# HTTP headers
headers = {
    'Accept': 'application/json',
    'Authorization': 'bearer ' + AUTORISATIE,
    "User-Agent": "curl/7.61.0" 
}

# Opstellen URL
url = 'https://eu1.cloud.thethings.network/api/v3/as/applications/' + APPLICATION + '/devices/' + DEVICE_EUI + '/packages/storage/uplink_message'

# Uitvoeren HTTP request
response = requests.get(url, headers=headers)

# Verwerk resultaat
if response.status_code == 200 :

    # Request gaat goed
    print ('Request OK')

    # Open het csv-bestand en schrijf header
    fOut = open(OUTPUT_CSV_FILE, 'w')
    fOut.write('Timestamp;Waarde\n')

    # Verwerken van response en resultaten opslaan in bestand
    i = 0
    for line in response.text.splitlines():

        # Ophalen van datum en waarde
        json_new = json.loads(line)
        received_at = parser.parse(json_new['result']['received_at'])
        value = json_new['result']['uplink_message']['decoded_payload'][SENSOR]

        # Schrijf regel in csv-bestand
        i = i + 1
        fOut.write(received + ';' + value + '\n')

    # Sluit csv-bestand
    print(str(i) + ' rijen in bestand ' + OUTPUT_CSV_FILE)
    fOut.close()

else :

    # Response geeft foutmelding
    print('Request failed with response code ' +str(response.status_code))  

# End of script
print('Script is klaar')
