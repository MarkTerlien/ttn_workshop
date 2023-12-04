# Import libraries
import requests # HTTP interface
import json     # JSON interface
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import pandas as pd

# Aurorisatie
AUTORISATIE = 'NNSXS.WCODVFI7XZZZDWYRQXT5R6PUD7KMTX7PTZRWT5Y.H4JNXDPJAITC2NAGETL7F6FN2CM33YEI5YQIBBXERVVMR4NHQKUQ'

# Geef applicatie, device en sensor
APPLICATION = 'demo-lth65'
DEVICE_EUI = 'eui-a84041ef7186a50f'
SENSOR = 'TempC_DS'
#BatV
#Ext_sensor
#Hum_SHT
#TempC_DS
#TempC_SHT

# Output file
OUTPUT_CSV_FILE = 'sensor_output.csv'

# Definieer lijseten
timestamps = []
values = []

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

# Get result
if response.status_code == 200 :

    # Verwerken van response en resultaten opslaan in lijsten
    print ('Request OK')
    for line in response.text.splitlines():
        json_new = json.loads(line)
        received_at = parser.parse(json_new['result']['received_at'])
        timestamps.append(received_at)
        value = json_new['result']['uplink_message']['decoded_payload'][SENSOR]
        values.append(value)

    # Plot grafiek
    print('Maak grafiek')
    ax = plt.axes()
    ax.plot(timestamps, values)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.grid(True)
    ax.set_title('Metingen')
    ax.set_ylabel(SENSOR)
    ax.set_xlabel('Datum/tijd')   
    plt.savefig('test.png')
    plt.show() 

else :

    # Response geeft foutmelding
    print('Request failed with response code ' +str(response.status_code))   

# End of script
print('Script is klaar')
