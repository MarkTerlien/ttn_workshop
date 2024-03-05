import os, sys
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, date
import easygui

# Definition of database class
class DbConnection:

    # Constructor
    def __init__(self):

        # Set constante
        self.SRID = 4326

        # Open database connection
        try:
            path = os.path.dirname(os.path.abspath(sys.argv[0]))
            db_file = open(path + '/db.txt','r')
            delimiter = ':'
            for row in db_file:
                db_host = row.split(delimiter)[0]
                db_port = row.split(delimiter)[1]
                db_name = row.split(delimiter)[2]
                db_user = row.split(delimiter)[3]
                db_password = row.split(delimiter)[4]
            db_file.close()
            db_connect = "dbname='" + str(db_name) + "' " 
            db_connect = db_connect + "user='" + str(db_user) + "' " 
            db_connect = db_connect + "host='" + str(db_host) + "' " 
            db_connect = db_connect + "port='" + str(db_port) + "' " 
            db_connect = db_connect + "password='" + str(db_password) + "'"
            self.db_connect = db_connect

            # Definition of device types
            self.LSE01 = 'LSE01'
            self.sensecaps2120_8_in_1 = 'sensecaps2120-8-in-1'
            self.lsn50v2_s31 = 'lsn50v2-s31'
            self.device_type_list = [self.LSE01, self.sensecaps2120_8_in_1, self.lsn50v2_s31]

            # Dictionary with documentation URLs
            self.documentation = {}

            # Dictionary with parameters per model
            self.device_type_parameters = {}

            # Measured parameters model LSE01 and link to description
            parameters_lse01 = {}
            parameters_lse01['Bat'] = 5
            parameters_lse01['TempC_DS18B20'] = 1
            parameters_lse01['conduct_SOIL'] = 2
            parameters_lse01['temp_SOIL'] = 1
            parameters_lse01['water_SOIL'] = 3
            self.documentation[self.LSE01] = 'http://wiki.dragino.com/xwiki/bin/view/Main/User%20Manual%20for%20LoRaWAN%20End%20Nodes/LSE01-LoRaWAN%20Soil%20Moisture%20%26%20EC%20Sensor%20User%20Manual/'

            # Measured parameters model weatherstation sensecap-s1210-1 and link to description
            parameters_sensecap_s1210_1 = {}
            parameters_sensecap_s1210_1['Battery(%)'] = 5
            parameters_sensecap_s1210_1['Air Temperature'] = 1
            parameters_sensecap_s1210_1['Air Humidity'] = 4
            parameters_sensecap_s1210_1['Light Intensity'] = 16 
            parameters_sensecap_s1210_1['UV Index'] = 26 
            parameters_sensecap_s1210_1['Wind Speed'] = 8
            parameters_sensecap_s1210_1['Wind Direction Sensor'] = 9
            parameters_sensecap_s1210_1['Rain Gauge'] = 6
            parameters_sensecap_s1210_1['Barometric Pressure'] = 15
            self.documentation[self.sensecaps2120_8_in_1] = 'https://www.kiwi-electronics.com/nl/sensecap-s2120-8-in-1-lorawan-weerstation-11233'

            # Parameters humidity sensor external sensor shuttle
            parameters_lsn50v2 = {}
            parameters_lsn50v2['BatV'] = 5
            parameters_lsn50v2['Hum_SHT'] = 4 
            parameters_lsn50v2['TempC_SHT'] = 1
            self.documentation[self.lsn50v2_s31] = 'https://www.dragino.com/products/temperature-humidity-sensor/item/169-lsn50v2-s31.html'

            # Add to parameters per model
            self.device_type_parameters[self.LSE01] = parameters_lse01 
            self.device_type_parameters[self.sensecaps2120_8_in_1] = parameters_sensecap_s1210_1 
            self.device_type_parameters[self.lsn50v2_s31] = parameters_lsn50v2  

        except :
            raise

    # Open connection
    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db_connect)
            self.cur = self.conn.cursor()
            return True
        except :
            return False

    # Plot sensordata
    def get_sensordata(self, input_parameters):
        try:
            # SQL query to select data
            sql = 'SELECT end_dev_eui, parameter_name, time_stamp, value FROM public.observation '
            sql = sql + ' where end_dev_eui = %s and parameter_name = %s '
            sql = sql + ' and time_stamp >= %s and time_stamp <= %s order by time_stamp desc'

            # Definieer arrays voor x,y
            times = []
            values = []

            # Execute SQL
            self.cur.execute(sql,(input_parameters['DEV_EUI'], input_parameters['PARAMETER'], input_parameters['MINIMUM_DATE'], input_parameters['MAXIMUM_DATE']))
            for row in self.cur.fetchall() :
                phenomenom_time =  row[2]
                times.append(phenomenom_time)
                result_ = row[3]
                values.append(result_)
            
            # Return waardes voor x en y
            return times, values
            
        except:
            raise

    # Select list of fieldlabs which have already devices
    def get_fieldlabs(self):
        try:

            # Build query
            sql_stmt = 'SELECT distinct description'
            sql_stmt = sql_stmt + ' FROM public.fieldlab_device_sensor_tag' 
                    
            # Execute query
            self.cur.execute(sql_stmt)            
            
            # Build cow list
            result_list = []
            for row in self.cur.fetchall():
                result_list.append(row[0])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting sensor list")
            raise 

    # Select list of fieldlabs which have already devices
    def get_all_fieldlabs(self):
        try:

            # Build query
            sql_stmt = 'SELECT description'
            sql_stmt = sql_stmt + ' FROM public.fieldlab' 
                    
            # Execute query
            self.cur.execute(sql_stmt)            
            
            # Build cow list
            result_list = []
            for row in self.cur.fetchall():
                result_list.append(row[0])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting all fieldlabs")
            raise 

    # Get ID of fieldlab based on description
    def get_fieldlab_id_for_description(self, fieldlab_description):
        try:
            
            # Build query
            sql_stmt = 'SELECT fieldlab_id'
            sql_stmt = sql_stmt + ' FROM public.fieldlab where description = %s' 
                    
            # Execute query
            self.cur.execute(sql_stmt,(fieldlab_description,))            
            
            # Build result list
            result_list = []
            for row in self.cur.fetchall():
                result_list.append(row[0])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting fieldlab id")
            raise

    # Toevoegen fieldlab
    def add_fieldlab(self, input_params):
        try:

            # Build insert statement
            sql_insert = 'insert into public.fieldlab'
            sql_insert = sql_insert + '(description, contactpersoon_naam, contactpersoon_email, contactpersoon_mobiel, contactpersoon_adres, "location", start_date, fieldlab_name)'
            sql_insert = sql_insert + ' values (%s,%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),%s),current_date,%s)'

            # Values to insert
            values = []
            values.append(input_params['description'])
            values.append(input_params['contactpersoon_naam'])
            values.append(input_params['contactpersoon_email'])
            values.append(input_params['contactpersoon_mobiel'])
            values.append(input_params['contactpersoon_adres'])
            values.append(input_params['lengtegraad'])
            values.append(input_params['breedtegraad'])
            values.append(self.SRID)
            values.append(input_params['fieldlab_name'])

            # Execute query
            print(sql_insert)
            self.cur.execute(sql_insert,values) 
 
        except Exception as e:
            print("Exception occurred adding fieldlabs")
            print(e)
            self.rollback()
            raise 

    # Get  device types
    def get_device_types(self):
        try:
            # Return the cow list
            return self.device_type_list
        except :
            print("Exception occurred getting all fieldlabs")
            raise 

    # Toevoegen van een device met sensoren
    def add_device(self, input_parameters):
        try:

            # Insert statement to add device 		
            sql_insert = 'INSERT INTO public.device('
            sql_insert = sql_insert + ' end_dev_eui, fieldlab_id, brand, model, serial_number, '
            sql_insert = sql_insert + ' app_eui, dev_eui, app_key, join_eui, dev_addr,'
            sql_insert = sql_insert + ' documentation, administrator, '
            sql_insert = sql_insert + ' installation_description, start_date,ttn_application)'
            sql_insert = sql_insert + ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
          
            # Get fieldlab_id
            fieldlab_id = self.get_fieldlab_id_for_description(input_parameters['fieldlab'])[0]

            # Make list of device parameters
            device_attributes = []
            device_attributes.append(input_parameters['end_dev_eui'])
            device_attributes.append(fieldlab_id)
            device_attributes.append(input_parameters['brand'])
            device_attributes.append(input_parameters['device_type'])
            device_attributes.append(input_parameters['serial_number'])
            device_attributes.append(input_parameters['app_eui'])
            device_attributes.append(input_parameters['dev_eui'])
            device_attributes.append(input_parameters['app_key'])
            device_attributes.append(input_parameters['join_eui'])
            device_attributes.append(input_parameters['dev_addr'])
            device_attributes.append(self.documentation[input_parameters['device_type']])
            device_attributes.append(input_parameters['administrator'])
            device_attributes.append(input_parameters['installation_description'])
            device_attributes.append(input_parameters['start_date_device'])
            device_attributes.append(input_parameters['ttn_application'])

            # Insert device
            print("Insert device " + str(input_parameters['end_dev_eui']))
            self.cur.execute(sql_insert, device_attributes)
                
            # Voor elke sensor parameter die gemeten wordt
            sensors = self.device_type_parameters[input_parameters['device_type']] 
            for key in sensors:		
                
                # Make list of sensor parameters
                sensor_attributes = []
                sensor_attributes.append(input_parameters['end_dev_eui'])
                sensor_attributes.append(key)
                sensor_attributes.append(sensors[key])
                sensor_attributes.append(input_parameters['sensor_installation_description'])
                sensor_attributes.append(input_parameters['start_date_device'])
                sensor_attributes.append('') # No installation photo
                            
                # Build insert statement
                sql_insert = 'INSERT INTO public.sensor('
                sql_insert = sql_insert + ' end_dev_eui_id, parameter_name, measurand_id_id'
                sql_insert = sql_insert + ' , installation_description, start_date, installation_photo)'
                sql_insert = sql_insert + ' VALUES (%s, %s, %s, %s, %s, %s)'

                # Insert sensor parameter
                print("Insert sensor parameter " + str(key))
                self.cur.execute(sql_insert, sensor_attributes)

        except Exception as e:
            print("Exception occurred adding device")
            print(e)
            self.rollback()
            raise 

    # Function to get list of tags
    def get_tags(self):
        try:
            # Build query
            sql_stmt = 'SELECT tag FROM public.tag'

            # Execute query
            self.cur.execute(sql_stmt)   

            # Build result list
            result_list = []
            for row in self.cur.fetchall():
                result_list.append(row[0])

            # Return the result list
            return result_list

        except Exception as e:
            print("Exception occurred gettting tags")
            print(e)
            self.rollback()
            raise 

    # Toevoegen fieldlab
    def add_tag(self, input_params):
        try:

            # Build insert statement
            sql_insert = 'INSERT INTO public.tag(tag) VALUES(%s)'

            # Values to insert
            values = []
            values.append(input_params['tag'])

            # Execute query
            print(sql_insert)
            self.cur.execute(sql_insert,values) 
 
        except Exception as e:
            print("Exception occurred adding tag")
            print(e)
            self.rollback()
            raise 

    # Select list with sensors
    def get_sensors_for_fieldlab(self, fieldlab):
        try:

            # Build query
            sql_stmt = 'SELECT device.end_dev_eui, parameter_name, tag_id, installation_description'
            sql_stmt = sql_stmt + ' FROM public.fieldlab_device_sensor_tag, device' 
            sql_stmt = sql_stmt + ' where description = %s and device.end_dev_eui = fieldlab_device_sensor_tag.end_dev_eui'
                    
            # Execute query
            self.cur.execute(sql_stmt,(fieldlab,))            
            
            # Build cow list
            result_list = []
            for row in self.cur.fetchall():
                if row[2] is not None : 
                    result_list.append(row[0] + ':' + row[1] + ':' + row[2] + ':' + row[3])
                if row[2] is None : 
                    result_list.append(row[0] + ':' + row[1] + ':' + row[3])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting sensors for fieldlabs")
            raise 

    # Select list with active sensors
    def get_active_sensors_for_fieldlab(self, fieldlab):
        try:

            # Build query
            sql_stmt = 'SELECT end_dev_eui, parameter_name, tag_id'
            sql_stmt = sql_stmt + ' FROM public.fieldlab_device_sensor_tag where description = %s and end_date is null' 
                    
            # Execute query
            self.cur.execute(sql_stmt,(fieldlab,))            
            
            # Build cow list
            result_list = []
            for row in self.cur.fetchall():
                if row[2] is not None : 
                    result_list.append(row[0] + ':' + row[1] + ':' + row[2] )
                if row[2] is None : 
                    result_list.append(row[0] + ':' + row[1])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting active sensors for fieldlabs")
            raise 

    # Select list with cows
    def get_sensors_for_device(self, end_dev_eui):
        try:

            # Build query
            sql_stmt = 'SELECT end_dev_eui, parameter_name, tag_id, installation_description'
            sql_stmt = sql_stmt + ' FROM public.fieldlab_device_sensor_tag where end_dev_eui = %s' 
                    
            # Execute query
            self.cur.execute(sql_stmt,(end_dev_eui,))            
            
            # Build cow list
            result_list = []
            for row in self.cur.fetchall():
                if row[2] is not None : 
                    result_list.append(row[0] + ':' + row[1] + ':' + row[2] + ':' + row[3])
                if row[2] is None : 
                    result_list.append(row[0] + ':' + row[1]+ '::' + row[3])
            
            # Return the cow list
            return result_list
        
        except :
            print("Exception occurred getting sensors for device")
            raise 

    # Function to get start_date from observation table
    def get_start_date_sensor(self, end_dev_eui, parameter_name) :
        try:

            # Build query
            sql = 'SELECT sensor_metadata_summary.start_date '
            sql = sql + ' FROM sensor_metadata_summary' 
            sql = sql + ' where sensor_metadata_summary.end_dev_eui = %s' 
            sql = sql + ' and   sensor_metadata_summary.parameter_name = %s' 

            # Get startdate 
            self.cur.execute(sql, (end_dev_eui, parameter_name))
            sensor_start_date = self.cur.fetchone()[0]
            if self.cur.rowcount == 0 :
                start_date = date.today() + timedelta(days=-1)
            else:
                start_datetime = sensor_start_date
                start_date = start_datetime.date()
            
            # Return result
            return start_date

        except :
            print("Exception occurred getting start date for sensor")
            raise 

    # Function to link tag to sensor
    def link_tag_to_sensor(self, input_params):
        try:

            # Check for each sensor if start_date is set
            new_tag = input_params['tag'] 
            for sensor in input_params['sensors']:

                # Get parameters
                end_dev_eui = sensor.split(':')[0]
                parameter_name = sensor.split(':')[1]

                # Build query
                sql_stmt = 'SELECT sensor_tag.id, sensor_id, tag_id, sensor_tag.start_date, sensor_tag.end_date'
                sql_stmt = sql_stmt + ' FROM public.sensor_tag, public.sensor' 
                sql_stmt = sql_stmt + ' where sensor_tag.sensor_id = sensor.id'
                sql_stmt = sql_stmt + ' and   sensor_tag.end_date is null'
                sql_stmt = sql_stmt + ' and   sensor.end_dev_eui_id = %s'
                sql_stmt = sql_stmt + ' and   sensor.parameter_name = %s'

                # Execute query
                self.cur.execute(sql_stmt,(end_dev_eui, parameter_name))   

                # Er zijn te veel tags gevonden
                if self.cur.rowcount == 2:
                    print('Sensor has 2 tags, no allowed')
                    raise
                # Er is een tag gevonden
                elif self.cur.rowcount == 1:
                    
                    # Get parameters
                    sensor_tag = self.cur.fetchone()  
                    sensor_tag_id = sensor_tag[0] 
                    sensor_id = sensor_tag[1] 
                    old_tag = sensor_tag[2]
                    start_date = sensor_tag[3] 
                        
                    #  Case 1: Bestaande tag zonder start date en geen nieuwe tag
                    if start_date is None and new_tag == old_tag:

                        # Get start date from observation table
                        start_date = self.get_start_date_sensor(end_dev_eui, parameter_name)

                        print('Update for sensor_tag_id is ' + str(sensor_tag_id))
                        update_sql = 'update sensor_tag set start_date = %s where id = %s'
                        self.cur.execute(update_sql,(start_date, sensor_tag_id))
                    
                    # Case 2: Bestaande tag zonder start date en wel nieuwe tag
                    elif start_date is None and new_tag != old_tag:

                        # Zet start date en maak bestaande tag historisch
                        # Get start date from observation table
                        start_date = self.get_start_date_sensor(end_dev_eui, parameter_name)

                        # Zet start date
                        update_sql = 'update sensor_tag set start_date = %s where id = %s'
                        self.cur.execute(update_sql,(start_date, sensor_tag_id))

                        # Zet end date
                        tomorrow = date.today() + timedelta(days=1)
                        update_sql = 'update sensor_tag set end_date = %s where id = %s'
                        self.cur.execute(update_sql,(tomorrow, sensor_tag_id))

                        # Insert nieuwe tag met start_date is tomorrow
                        tomorrow = date.today() + timedelta(days=1)
                        insert_sql = 'INSERT INTO public.sensor_tag'
                        insert_sql = insert_sql + '(sensor_id, tag_id, start_date)' 
                        insert_sql = insert_sql + ' values(%s, %s, %s)'
                        self.cur.execute(insert_sql,(sensor_id, new_tag, tomorrow))

                    # Case 3: Bestaande tag met start_date 
                    elif start_date:
                        
                        # Maak bestaande tag historisch 
                        tomorrow = date.today() + timedelta(days=1)
                        update_sql = 'update sensor_tag set end_date = %s where id = %s'
                        self.cur.execute(update_sql,(tomorrow, sensor_tag_id))

                        # Voer nieuwe tag op met start date is tommorrow
                        tomorrow = date.today() + timedelta(days=1)
                        insert_sql = 'INSERT INTO public.sensor_tag'
                        insert_sql = insert_sql + '(sensor_id, tag_id, start_date)' 
                        insert_sql = insert_sql + ' values(%s, %s, %s)'
                        self.cur.execute(insert_sql,(sensor_id, new_tag, tomorrow))
                
                # Geen tag gevonden voer dan nieuwe tag op
                else:

                    # Build query om ID sensor op te halen
                    sql_stmt = 'SELECT id FROM public.sensor' 
                    sql_stmt = sql_stmt + ' where sensor.end_dev_eui_id = %s'
                    sql_stmt = sql_stmt + ' and   sensor.parameter_name = %s'

                    # Execute query
                    self.cur.execute(sql_stmt,(end_dev_eui, parameter_name))   

                    # Fetch rows
                    sensor_id = self.cur.fetchone()[0]  

                    # Get start date from observation table
                    start_date = self.get_start_date_sensor(end_dev_eui, parameter_name)

                    # Voer nieuwe tag op met start date is tommorrow
                    insert_sql = 'INSERT INTO public.sensor_tag'
                    insert_sql = insert_sql + '(sensor_id, tag_id, start_date)' 
                    insert_sql = insert_sql + ' values(%s, %s, %s)'
                    self.cur.execute(insert_sql,(sensor_id, new_tag, start_date))

        except :
            print("Exception occurred adding tag to sensor")
            raise 

    # Commit
    def commit(self):
        self.conn.commit()
        
    # Close
    def close(self):
        try:
            self.conn.close()
        except:
            print("Exception occurred closing database")
            raise
        
    # Rollback
    def rollback(self):
        self.conn.rollback()
        
    # Commit and close
    def commit_and_close(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("Exception occurred closing database " + str(e))
            raise

# Class with gui elements
class Gui:

    # Constructor
    def __init__(self):
        self.start_date = None  

        # Open database connection
        self.db = DbConnection()
        self.db.open_connection() 

        # Menu_items (user stories) met functie naam (zonder gui_ en app_logic_)
        self.MENU_ITEM_1 = ['Plot sensor data', 'plot_sensor_data']
        self.MENU_ITEM_2 = ['Toevoegen fieldlab', 'add_fieldlab']
        self.MENU_ITEM_3 = ['Toevoegen tag', 'add_tag']
        self.MENU_ITEM_4 = ['Toevoegen device', 'add_device']
        self.MENU_ITEM_5 = ['Koppelen tag aan sensor', 'link_tag_to_sensor']

    def show_menu_items (self) :

        # Select what you want to do
        msg     = "Selecteer wat je wil doen"
        choices = [ self.MENU_ITEM_1[0], self.MENU_ITEM_2[0], self.MENU_ITEM_3[0], self.MENU_ITEM_4[0], self.MENU_ITEM_5[0]]
        choice  = self.button_box(msg, choices)
        if choice == self.MENU_ITEM_1[0] :
            return self.MENU_ITEM_1[1]
        if choice == self.MENU_ITEM_2[0] :
            return self.MENU_ITEM_2[1]
        if choice == self.MENU_ITEM_3[0] :
            return self.MENU_ITEM_3[1]
        if choice == self.MENU_ITEM_4[0] :
            return self.MENU_ITEM_4[1]
        if choice == self.MENU_ITEM_5[0] :
            return self.MENU_ITEM_5[1]

    # Function to start main program and gui
    def main(self) :

        # Show menu item
        geselecteerd_menu_item = gui.show_menu_items()
        
        # Call correct function
        if geselecteerd_menu_item == 'plot_sensor_data': 
            app_logic.plot_sensor_data(gui.plot_sensor_data())
        if geselecteerd_menu_item == 'add_fieldlab':
            app_logic.add_fieldlab(gui.add_fieldlab())
        if geselecteerd_menu_item == 'add_tag':
            app_logic.add_tag(gui.add_tag())
        if geselecteerd_menu_item == 'add_device':
            app_logic.add_device(gui.add_device())
        if geselecteerd_menu_item == 'link_tag_to_sensor':
            app_logic.link_tag_to_sensor(gui.link_tag_to_sensor())

    def cc_box(self, msg, title ) :
        choices = ("Ja", "Nee")
        return easygui.ccbox(msg, title, choices)

    def integer_box(self, msg, title, lower_bound, upper_bound):
        return easygui.integerbox(msg, title, lowerbound=lower_bound, upperbound=upper_bound)

    def multichoice_box(self, msg, title, choices):
        selection = easygui.multchoicebox(msg, title, choices)
        if selection == None :
            selection = [] 
        return selection
    
    def multenter_box(self,msg,title, fieldNames):
        return easygui.multenterbox(msg,title, fieldNames)
    
    def enter_box(self,msg,title, fieldNames):
        return easygui.enterbox(msg,title, fieldNames)

    def choice_box(self, msg, title, choices):
        return easygui.choicebox(msg, title, choices)

    def diropen_box(self, msg, title, choice) :
        return easygui.diropenbox(msg , title, choice)

    def text_box(self, msg, title, text):
        return easygui.textbox(msg, title, text, codebox=0)

    def msg_box(self, message):
        return easygui.msgbox(message)

    def bool_box(self, msg, title) :
        return easygui.boolbox(msg, title, ["Ja", "Nee"])

    def file_open_box(self, msg, title, default, file_type):
        return easygui.fileopenbox(msg, title, default=default, filetypes=file_type, multiple=False)

    def button_box(self, msg, choices):
        return easygui.buttonbox(msg, image=None, choices=choices)

    def cc_box(self, msg, title):
        return easygui.ccbox(msg, title)
    
    # Gui to ask for input for inserting device
    def add_device(self):

        # Gui input parameters
        gui_input_params = {} 

        # Get fieldlabs
        fieldlab = None
        while fieldlab == None:
            fieldlab = gui.choice_box('Select fieldlab', 'Fieldlab selectie', self.db.get_all_fieldlabs())
        gui_input_params['fieldlab'] = fieldlab

        # Get fieldlabs
        device_type = None
        while device_type == None:
            device_type = gui.choice_box('Select device type', 'Device type selectie', self.db.get_device_types())
        gui_input_params['device_type'] = device_type

        # Opbouwen scherm
        msg = "Voeg eigenschappen device toe"
        title = "Toevoegen device"
        fieldlab_attributes = []
        fieldlab_attributes.append('end_dev_eui')
        fieldlab_attributes.append('brand')
        fieldlab_attributes.append('serial_number')
        fieldlab_attributes.append('app_eui')
        fieldlab_attributes.append('dev_eui')
        fieldlab_attributes.append('app_key')
        fieldlab_attributes.append('join_eui')
        fieldlab_attributes.append('dev_addr')
        fieldlab_attributes.append('administrator')
        fieldlab_attributes.append('installation_description')
        fieldlab_attributes.append('ttn_application')
        fieldlab_attributes.append('jaar')
        fieldlab_attributes.append('maand (1-12)')
        fieldlab_attributes.append('dag (1-31)')
        fieldlab_attributes.append('sensor_installation_description')
        fieldlab_attribute_values = [] 

        # Ask for attributes
        fieldlab_attribute_values = self.multenter_box(msg,title, fieldlab_attributes)

        # Make sure that none of the fields was left blank
        while True:
            errmsg = ''
            for i in range(len(fieldlab_attributes)):
                if fieldlab_attribute_values[i].strip() == '':
                    errmsg = errmsg + ('"%s" is verplicht attribuut.\n\n' % fieldlab_attributes[i])
            if errmsg == '': break 
            fieldlab_attribute_values = self.multenter_box(errmsg ,title, fieldlab_attributes)

        # Write to dict
        gui_input_params['end_dev_eui'] = fieldlab_attribute_values[0] 
        gui_input_params['brand'] = fieldlab_attribute_values[1] 
        gui_input_params['serial_number'] = fieldlab_attribute_values[2] 
        gui_input_params['app_eui'] = fieldlab_attribute_values[3]
        gui_input_params['dev_eui'] = fieldlab_attribute_values[4] 
        gui_input_params['app_key'] = fieldlab_attribute_values[5] 
        gui_input_params['join_eui'] = fieldlab_attribute_values[6]  
        gui_input_params['dev_addr'] = fieldlab_attribute_values[7]  
        gui_input_params['administrator'] = fieldlab_attribute_values[8] 
        gui_input_params['installation_description'] = fieldlab_attribute_values[9] 
        gui_input_params['ttn_application'] = fieldlab_attribute_values[10]  
        gui_input_params['start_date_device'] = datetime(int(fieldlab_attribute_values[11]), int(fieldlab_attribute_values[12]), int(fieldlab_attribute_values[13]))  
        gui_input_params['sensor_installation_description'] = fieldlab_attribute_values[14] 

        # Return
        return gui_input_params

    # Gui to ask input for plotting sensor data
    def plot_sensor_data(self):

            # Dict with input_params
            gui_input_params = {}

            # Get fieldlabs
            fieldlab = None
            while fieldlab == None:
                fieldlab = gui.choice_box('Select fieldlab', 'Fieldlab selectie', self.db.get_fieldlabs())

            # Get sensors
            sensor = None
            while sensor == None:
                sensor = gui.choice_box('Select sensor', 'Sensor selectie', self.db.get_sensors_for_fieldlab(fieldlab))
            gui_input_params['sensor'] = sensor

            # Get tijdsintervallen
            tijdsinterval = None
            while tijdsinterval == None:
                tijdsintervallen = ['Dag', 'Week', 'Maand', 'Jaar']
                tijdsinterval = gui.choice_box('Select sensor', 'Sensor selectie', tijdsintervallen)

            # Dict om tijdrange om te zetten naar dagen
            convert_tijdsinterval = {}
            convert_tijdsinterval['Dag'] = 1
            convert_tijdsinterval['Week'] = 7
            convert_tijdsinterval['Maand'] = 30
            convert_tijdsinterval['Jaar'] = 365
            gui_input_params['tijdsinterval_in_dagen'] = convert_tijdsinterval[tijdsinterval]

            # Return
            return gui_input_params

    def add_fieldlab(self):

        # Gui input parameters
        gui_input_params = {}

        # Opbouwen scherm
        msg = "Voeg eigenschappen fieldlab toe"
        title = "Toevoegen fieldlab"
        fieldlab_attributes = []
        fieldlab_attributes.append('fieldlab_name')
        fieldlab_attributes.append('description')
        fieldlab_attributes.append('contactpersoon_naam'.replace('_',''))
        fieldlab_attributes.append('contactpersoon_email'.replace('_',''))
        fieldlab_attributes.append('contactpersoon_mobiel'.replace('_',''))
        fieldlab_attributes.append('contactpersoon_adres'.replace('_',''))
        fieldlab_attributes.append('lengtegraad (-180,180)')
        fieldlab_attributes.append('breedtegraad (-90,90)')
        fieldlab_attribute_values = []  

        # Ask for attributes
        fieldlab_attribute_values = self.multenter_box(msg,title, fieldlab_attributes)

        # Make sure that none of the fields was left blank
        while True:
            errmsg = ''
            for i in range(len(fieldlab_attributes)):
                if fieldlab_attribute_values[i].strip() == '':
                    errmsg = errmsg + ('"%s" is verplicht attribuut.\n\n' % fieldlab_attributes[i])
            if errmsg == '': break 
            fieldlab_attribute_values = self.multenter_box(errmsg ,title, fieldlab_attributes)

        # Write to dict
        gui_input_params['fieldlab_name'] = fieldlab_attribute_values[0] 
        gui_input_params['description'] = fieldlab_attribute_values[1] 
        gui_input_params['contactpersoon_naam'] = fieldlab_attribute_values[2] 
        gui_input_params['contactpersoon_email'] = fieldlab_attribute_values[3]
        gui_input_params['contactpersoon_mobiel'] = fieldlab_attribute_values[4] 
        gui_input_params['contactpersoon_adres'] = fieldlab_attribute_values[5] 
        gui_input_params['lengtegraad'] = fieldlab_attribute_values[6]  
        gui_input_params['breedtegraad'] = fieldlab_attribute_values[7]  

        # Return
        return gui_input_params
    
    def add_tag(self):

        # Gui input parameters
        gui_input_params = {}

        # Opbouwen scherm
        msg = "Voeg tag toe"
        title = "Toevoegen tag"

        # Ask for attributes
        gui_input_params['tag'] = self.enter_box(msg, title, '')

        # Return
        return gui_input_params

    # Function to link tag to sensor
    def link_tag_to_sensor(self):

        # Dict with input_params
        gui_input_params = {}

        # Get fieldlabs
        fieldlab = None
        while fieldlab == None:
            fieldlab = gui.choice_box('Selecteer fieldlab', 'Fieldlab selectie', self.db.get_all_fieldlabs())

        # Get sensors
        sensors = None
        while sensors == None:
            sensors = gui.multichoice_box('Selecteer sensoren to tag', 'Sensor selectie', self.db.get_active_sensors_for_fieldlab(fieldlab))
        gui_input_params['sensors'] = sensors

        # Get tags
        tag = None
        while tag == None:
            tag = gui.choice_box('Selecteer tag', 'Tag selectie', self.db.get_tags())
        gui_input_params['tag'] = tag

        # Return input
        return gui_input_params 

    def stop(self):

        # Sluiten database
        self.db.close()


# Class with application logic
class AppLogic():

    # Constructor
    def __init__(self):
        # Open database connection
        self.db = DbConnection()
        self.db.open_connection()   

    # Function for x,y plot
    def generate_xy_plot (self, x_list, y_list, x_label, y_label, title):
        """"Generate xy scatterplot.

        Parameters
        ----------
        x_list : list
            List wth x-values
        y_list : list
            List with y-values
        x_label : str
            Label for x-axis
        y_label : str
            Label for y-axis
        title : str
            Title for scatterplot
        """
        try:

            # Converteer naa numpy arrays
            x = np.array(x_list)
            y = np.array(y_list)

            # Plot lijn met kleur blauw
            plt.plot(x, y, color='#0000FF')

            # Plot punten met kleur rood
            # plt.plot(x, y, 'o', color='#FF0000')

            # Toevoegen annotatie
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)

            # Toevoegen van gridlijnen
            plt.grid(b=True, which='major', color='#666666', linestyle='--', alpha=0.5)

            # Plot figuur
            plt.show()

        except Exception as e: 
            print('Error function generate_xy_plot')
            print(e)
            raise

    # Function to plot sensor data
    def plot_sensor_data(self, app_input_params):

        # Input
        db_input_params = {}
        db_input_params['DEV_EUI'] = app_input_params['sensor'].split(':')[0]
        db_input_params['PARAMETER'] = app_input_params['sensor'].split(':')[1]
        db_input_params['MINIMUM_DATE'] = datetime.now() - timedelta(days=app_input_params['tijdsinterval_in_dagen']) 
        db_input_params['MAXIMUM_DATE'] = datetime.now()

        # Ophalen tijd en waardes uit database
        x, y = self.db.get_sensordata(db_input_params)

        # Plot graph
        self.generate_xy_plot(x,y,'Datum/tijd',app_input_params['sensor'].split(':')[0],app_input_params['sensor'].split(':')[1])

    # Functie om fieldlab toe te voegen
    def add_fieldlab(self, app_input_params):
        self.db.add_fieldlab(app_input_params)
        self.db.commit()

    # Functie om fieldlab toe te voegen
    def add_tag(self, app_input_params):
        self.db.add_tag(app_input_params)
        self.db.commit()

    # Functie om device met sensoren toe te voegen
    def add_device(self, app_input_params):
        self.db.add_device(app_input_params)
        self.db.rollback()

    # Function to link tag to sensor
    def link_tag_to_sensor(self, app_input_params):
        self.db.link_tag_to_sensor(app_input_params)
        self.db.commit()

    # Sluiten database
    def stop(self):
        self.db.close()

# Start application 
start_app = True

# Init calls with application logic
app_logic = AppLogic()
    
# Start Gui
gui = Gui()

# Export data
while start_app :
    gui.main()
    start_app = False

# Stop application
gui.stop()
app_logic.stop()


