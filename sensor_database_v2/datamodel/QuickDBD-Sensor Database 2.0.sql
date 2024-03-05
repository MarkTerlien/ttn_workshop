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

parameter
-
parameter_name text PK
parameter_description text NULL
parameter_unit text NULL
model_id text FK >- model.model_id
*/

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
        "parameter_name"
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
AS SELECT t2.fieldlab_name,
    t2.sensor_tag,
    t2.end_dev_eui,
    t1.parameter_name,
    t1.time_stamp,
    t1.value
   FROM observation t1,
    ( SELECT sensor.end_dev_eui_id AS end_dev_eui,
            sensor.parameter_name,
            sensor_tag.start_date AS start_datum,
            sensor_tag.end_date AS eind_datum,
            sensor_tag.tag_id AS sensor_tag,
            fieldlab.fieldlab_name
           FROM fieldlab,
            device,
            sensor,
            sensor_tag
          WHERE fieldlab.fieldlab_id = device.fieldlab_id 
		  AND device.end_dev_eui::text = sensor.end_dev_eui_id::text 
		  AND sensor_tag.sensor_id = sensor.id) t2
  WHERE t1.end_dev_eui = t2.end_dev_eui::text 
  AND t1.parameter_name = t2.parameter_name::text 
  AND t1.time_stamp > t2.start_datum
  AND t1.time_stamp < COALESCE(t2.eind_datum::timestamp with time zone, now());
