-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/UMj3Bs
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).
-- https://app.quickdatabasediagrams.com/

/*
# Modify this code to update the DB schema diagram.
# To reset the sample schema, replace everything with
# two dots ('..' - without quotes).
# https://app.quickdatabasediagrams.com/#/d/UMj3Bs

# Modify this code to update the DB schema diagram.
# To reset the sample schema, replace everything with
# two dots ('..' - without quotes).
# https://app.quickdatabasediagrams.com/#/d/UMj3Bs

fieldlab
-
fieldlab_id serial PK 
fieldlab_name text UNIQUE
fieldlab_description text
location geometry(geometry,4326)

tag
--
tag text PK 

fieldlab_device
-
fieldlab_id int PK FK >- fieldlab.fieldlab_id
end_dev_eui text PK FK >- device.end_dev_eui
tag text FK >- tag.tag
start_date PK date
end_date date NULL

device
-
end_dev_eui text PK
model_id text FK >- model.model_id
installation_description text NULL


observation
-
end_dev_eui text PK FK >- device.end_dev_eui
parameter_name text PK 
time_stamp PK timestamp
value float

model
-
model_id text PK
model_url text
model_description text

parameter
-
parameter_name text PK
parameter_description text NULL
parameter_unit text NULL
model_id text PK FK >- model.model_id
*/


-- Install PostGIS extension
CREATE EXTENSION postgis;

-- Create tables
CREATE TABLE "fieldlab" (
    "fieldlab_id" serial   NOT NULL,
    "fieldlab_name" text   NOT NULL,
    "fieldlab_description" text   NOT NULL,
    "location" geometry(geometry,4326)   NOT NULL,
    CONSTRAINT "pk_fieldlab" PRIMARY KEY (
        "fieldlab_id"
     ),
    CONSTRAINT "uc_fieldlab_fieldlab_name" UNIQUE (
        "fieldlab_name"
    )
);

CREATE TABLE "tag" (
    "tag" text   NOT NULL,
    CONSTRAINT "pk_tag" PRIMARY KEY (
        "tag"
     )
);

CREATE TABLE "fieldlab_device" (
    "fieldlab_id" int   NOT NULL,
    "end_dev_eui" text   NOT NULL,
    "tag" text   NOT NULL,
    "start_date" date   NOT NULL,
    "end_date" date   NULL,
    CONSTRAINT "pk_fieldlab_device" PRIMARY KEY (
        "fieldlab_id","end_dev_eui","start_date"
     )
);

CREATE TABLE "device" (
    "end_dev_eui" text   NOT NULL,
    "model_id" text   NOT NULL,
    "installation_description" text   NULL,
    CONSTRAINT "pk_device" PRIMARY KEY (
        "end_dev_eui"
     )
);

CREATE TABLE "observation" (
    "end_dev_eui" text   NOT NULL,
    "parameter_name" text   NOT NULL,
    "time_stamp" timestamp   NOT NULL,
    "value" float   NOT NULL,
    CONSTRAINT "pk_observation" PRIMARY KEY (
        "end_dev_eui","parameter_name","time_stamp"
     )
);

CREATE TABLE "model" (
    "model_id" text   NOT NULL,
    "model_url" text   NOT NULL,
    "model_description" text   NOT NULL,
    CONSTRAINT "pk_model" PRIMARY KEY (
        "model_id"
     )
);

CREATE TABLE "parameter" (
    "parameter_name" text   NOT NULL,
    "parameter_description" text   NULL,
    "parameter_unit" text   NULL,
    "model_id" text   NOT NULL,
    CONSTRAINT "pk_parameter" PRIMARY KEY (
        "parameter_name","model_id"
     )
);

ALTER TABLE "fieldlab_device" ADD CONSTRAINT "fk_fieldlab_device_fieldlab_id" FOREIGN KEY("fieldlab_id")
REFERENCES "fieldlab" ("fieldlab_id");

ALTER TABLE "fieldlab_device" ADD CONSTRAINT "fk_fieldlab_device_end_dev_eui" FOREIGN KEY("end_dev_eui")
REFERENCES "device" ("end_dev_eui");

ALTER TABLE "fieldlab_device" ADD CONSTRAINT "fk_fieldlab_device_tag" FOREIGN KEY("tag")
REFERENCES "tag" ("tag");

ALTER TABLE "device" ADD CONSTRAINT "fk_device_model_id" FOREIGN KEY("model_id")
REFERENCES "model" ("model_id");

ALTER TABLE "observation" ADD CONSTRAINT "fk_observation_end_dev_eui" FOREIGN KEY("end_dev_eui")
REFERENCES "device" ("end_dev_eui");

ALTER TABLE "parameter" ADD CONSTRAINT "fk_parameter_model_id" FOREIGN KEY("model_id")
REFERENCES "model" ("model_id");

-- Create view for retrieval of observations
CREATE OR REPLACE VIEW public.sensor_observations_view
AS 
SELECT t2.fieldlab_name
,      t2.tag
,      t2.end_dev_eui
,      t1.parameter_name
,      t1.time_stamp
,      t1.value
FROM observation t1
,	 ( 
	  SELECT fieldlab.fieldlab_name
	  ,      device.end_dev_eui         AS end_dev_eui
	  ,      parameter.parameter_name   AS parameter_naam
	  ,      fieldlab_device.start_date AS start_datum
	  ,      fieldlab_device.end_date   AS eind_datum
	  ,      fieldlab_device.tag        AS tag
	  FROM  fieldlab
	  ,     device
	  ,     fieldlab_device
	  ,     model
	  ,     parameter
	  WHERE fieldlab.fieldlab_id        = fieldlab_device.fieldlab_id 
	  AND   fieldlab_device.end_dev_eui = device.end_dev_eui 
	  AND   device.model_id             = model.model_id
	  and   model.model_id              = parameter.model_id
	 ) t2
 WHERE t1.end_dev_eui    = t2.end_dev_eui
 AND   t1.parameter_name = t2.parameter_naam
 AND   t1.time_stamp     > t2.start_datum 
 AND   t1.time_stamp     < COALESCE(t2.eind_datum, now());

 -- Insert models
 INSERT INTO model (model_id,model_url,model_description) VALUES
	 ('LSE01','http://wiki.dragino.com/xwiki/bin/view/Main/User%20Manual%20for%20LoRaWAN%20End%20Nodes/LSE01-LoRaWAN%20Soil%20Moisture%20%26%20EC%20Sensor%20User%20Manual/
','Bodemvocht, bodemtemperatuur en bodemgeleidbaarheid'),
	 ('sensecaps2120-8-in-1','https://www.kiwi-electronics.com/nl/sensecap-s2120-8-in-1-lorawan-weerstation-11233
','Weerstation (temperatuur, luchtvochtigheid, wind, regen, luchtdruk)'),
	 ('lsn50v2-s31','https://www.dragino.com/products/temperature-humidity-sensor/item/169-lsn50v2-s31.html
','Temperatuur en luchtvochtigheid'),
	 ('MCF-LW12TERPM','https://delmation.nl/product/mfc88-mcf-lw12terpm/','Fijnstof (PM2.5, PM10), temperatuur, vochtigheid, luchtdruk'),
	 ('LHT65','https://www.dragino.com/products/temperature-humidity-sensor/item/151-lht65.html','Luchtemperatuur, luchtvochtigheid en temperatuur via externe sensor');

-- Insert parameters
INSERT INTO parameter (parameter_name,parameter_description,parameter_unit,model_id) VALUES
	 ('Bat','Batterij','','LSE01'),
	 ('conduct_SOIL','Bodemgeleiding','uS/cm','LSE01'),
	 ('water_SOIL','Bodemvochtigheid','%','LSE01'),
	 ('Battery(%)','Batterij','%','sensecaps2120-8-in-1'),
	 ('Light Intensity','Licht intensiteit','lux','sensecaps2120-8-in-1'),
	 ('UV Index','UV Index','','sensecaps2120-8-in-1'),
	 ('Wind Speed','Windsnelheid','m/s','sensecaps2120-8-in-1'),
	 ('Rain Gauge','Regenval','mm/h','sensecaps2120-8-in-1'),
	 ('Barometric Pressure','Luchtdruk','hPa','sensecaps2120-8-in-1'),
	 ('BatV','Batterij','Volt','lsn50v2-s31');
INSERT INTO parameter (parameter_name,parameter_description,parameter_unit,model_id) VALUES
	 ('Hum_SHT','Vochtigheid','%RH','lsn50v2-s31'),
	 ('battery','Batterij','','MCF-LW12TERPM'),
	 ('date','Datum','','MCF-LW12TERPM'),
	 ('humidity','Vochtigheid','%RH','MCF-LW12TERPM'),
	 ('pressure','Luchtdruk','hPa','MCF-LW12TERPM'),
	 ('BatV','Batterij','Volt','LHT65'),
	 ('Bat_status','Batterij',NULL,'LHT65'),
	 ('Hum_SHT','Luchtvochtigheid','%RH','LHT65'),
	 ('TempC_DS','Temperatuur','°C','LHT65'),
	 ('TempC_DS18B20','Temperatuur','°C','LSE01');
INSERT INTO parameter (parameter_name,parameter_description,parameter_unit,model_id) VALUES
	 ('temp_SOIL','Bodemtemperatuur','°C','LSE01'),
	 ('Air Temperature','Luchttemperatuur','°C','sensecaps2120-8-in-1'),
	 ('Air Humidity','Luchtvochtigheid','%RH','sensecaps2120-8-in-1'),
	 ('Wind Direction Sensor','Windrichting','°','sensecaps2120-8-in-1'),
	 ('TempC_SHT','Temperatuur','°C','lsn50v2-s31'),
	 ('TempC_SHT','Luchttemperatuur','°C','LHT65'),
	 ('pm1','Fijnstof kleiner dan 10 µm','µg/m3','MCF-LW12TERPM'),
	 ('pm10','Fijnstof kleiner dan 10 µm','µg/m3','MCF-LW12TERPM'),
	 ('pm25','Fijnstof kleiner dan 25 µm','µg/m3','MCF-LW12TERPM'),
	 ('temperature','Temperatuur','°C','MCF-LW12TERPM');

	 
