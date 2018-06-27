#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      thaynes
#
# Created:     15/03/2018
# Copyright:   (c) thaynes 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#===============================================================================
# Import required modules
#===============================================================================

import os
import os.path
import arcpy, csv, xlrd, pprint
from arcpy import env
from arcpy.sa import *
from datetime import datetime
from collections import defaultdict

#===============================================================================
# Get start time (allows script runtime to be tracked)
#===============================================================================
startTime = datetime.now()

#===============================================================================
# Assign input variables
#===============================================================================

lui_fc_gdb = r'M:\thaynes\CRD_ALUI2018\geodatabase\LUI_FC_keep.gdb'

# data path, output intersect name, fc to intersect
intersect_lyrs_csv = r'M:\thaynes\Python\SurveyPrep\ReferenceDataList_v4_Best.csv'

epsg_spatial_ref = 3005


#===============================================================================
# Set up environment
#===============================================================================

arcpy.env.workspace = os.path.dirname(lui_fc_gdb)
arcpy.env.overwriteOutput = True

outSR = arcpy.SpatialReference(epsg_spatial_ref)

today_date = datetime.now().strftime("%Y-%m-%d").replace("-","")

lot_fc = str(lui_fc_gdb) + "\\LNK\\LOT"

#cov_fc = str(lui_fc_gdb) + "\\LNK\\COV"

output_folder = os.path.dirname(lui_fc_gdb)

#===============================================================================
# Define functions
#===============================================================================

def GetTime(in_string):
    print in_string + " - " + str(datetime.now() - startTime)


def ListSources(in_CSV):
    file_paths = []
    file_reader = csv.reader(open(in_CSV,'rb'))
    n = 0
    for line in file_reader:
        if n > 0:
            file_detail = str(line[0]),str(line[1]),str(line[2]),str(line[3])
            file_paths.append(file_detail)
        n = n + 1

    missing_files = []
    for path,name,cov,lot in file_paths:
        if not arcpy.Exists(str(path)):
            missing_files.append(path)

    if missing_files:
        print "Files not found:"
        print missing_files
        print "Exiting script."
        exit()
    else:
        print "All files found."

    return file_paths


def CreateIntersects(in_fc,int_lyr,out_name,out_mdb):

    base_name = os.path.basename(in_fc)
    int_name = os.path.basename(int_lyr)

    if arcpy.Exists(str(out_mdb) + "\\" + str(out_name)):

        pass

    else:

        fc_flyr = arcpy.MakeFeatureLayer_management(in_fc,base_name + "_FL", "",out_mdb)

        if arcpy.Describe(int_lyr).dataType == "FeatureClass":

            int_flyr = arcpy.MakeFeatureLayer_management(int_lyr,out_name + "_FL","",out_mdb)

            lyr_intersects = arcpy.Intersect_analysis([fc_flyr,int_flyr],out_name,"ALL")

            del int_flyr

        elif arcpy.Describe(int_lyr).dataType == "Table":

            pass

        else:

            print "Error - Data Type '" + str(arcpy.Describe(int_lyr).dataType) + "' not recognized for layer: " + str(int_name) + ". DataType must be FeatureClass or Table."



#===============================================================================
# Initialize functions
#===============================================================================

print "Initializing functions..."

GetTime("Creating FC_Export.mdb")

try:
    #fc_export = arcpy.CreateFileGDB_management(output_folder,"FC_Export" + str(today_date))
    fc_export = arcpy.CreatePersonalGDB_management(output_folder,"FC_Export" + str(today_date))
except Exception as e:
    #fc_export = str(output_folder) + "FC_Export" + str(today_date) + ".gdb"
    fc_export = str(output_folder) + "//FC_Export" + str(today_date) + ".mdb"

print fc_export

workSpace = str(fc_export)

arcpy.env.workspace = workSpace
arcpy.env.overwriteOutput = True

GetTime("FC_Export created, checking intersect files")

int_files = ListSources(intersect_lyrs_csv)

GetTime("Check complete, intersecting files with feature classes")

for lyr,name,cov,lot in int_files:
    if str(cov).upper() == "ON":
        print "Working on: " + str(lyr)
        try:
            fc_path = str(lui_fc_gdb) + "\\LNK\\COV"
            CreateIntersects(fc_path,lyr,name,fc_export)
            GetTime(str(name) + " + intersect with COV complete.")
        except Exception as e:
            print "Error in " + str(lyr)
            print e

    if str(lot).upper() == "ON":
        print "Working on: " + str(lyr)
        try:
            fc_path = str(lui_fc_gdb) + "\\LNK\\LOT"
            CreateIntersects(fc_path,lyr,name,fc_export)
            GetTime(str(name) + " + intersect with LOT complete.")
        except Exception as e:
            print "Error in " + str(lyr)
            print e

GetTime("Intersects complete, MD has script for LICENCE_PID work.")

##for lyr,name,fc in int_files:
##    if "LICENCE_PID" in str(lyr):
##        for wlyr,wname,wfc in int_files:
##            if "WLS_POD" in str(wlyr):
##                try:
##                    water_table = arcpy.JoinField_management(str(fc_export) + "\\" + str(wname),"LICENCE_NO",str(lyr),"LICENCE_NO")
##                    fields = arcpy.ListFields(water_table)
##                    fieldinfo = arcpy.FieldInfo()
##                    for field in fields:
##                        if field.name == "TPOD_TAG":
##                            fieldinfo.addField(field.name,field.name,"VISIBLE","")
##                        elif field.name == "LICENCE_NO":
##                            fieldinfo.addField(field.name,field.name,"VISIBLE","")
##                        elif field.name == "PID":
##                            fieldinfo.addField(field.name,field.name,"VISIBLE","")
##                        else:
##                            fieldinfo.addField(field.name,field.name,"HIDDEN","")
##                    water_tv = arcpy.MakeTableView_management(water_table,str(name),"",fc_export,fieldinfo)
##                    water_lic = arcpy.TableToTable_conversion(water_tv,fc_export,str(name))
##                except Exception as e:
##                    print "ERROR JOINING LICENCE_PID TO WLS_POD"
##                    print e
##            else:
##                print "WLS_POD layer not found, cannot join LICENCE_PID."


#GetTime("Moving export to .mdb")

GetTime("Script finished")