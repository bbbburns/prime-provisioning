#!/usr/bin/python
# Modify a BAT export file from Prime Provisioning to enter the proper domain
# Input:
#	1. An Export from Prime Provisioning of Unassociated Phones (tab delimeted txt)
#	2. An Export from CUCM database of all publishers of the following SQL query
#	2a. run sql select d.name, p.name from device as d, devicepool as p where d.fkdevicepool = p.pkid
# 2b. Put this output into CSV format
#
# Usage:
#	./assign-domain-to-unassociated-phones.py <CUCM SQL Query Export File> <Prime Provisioning Export Input> <Output File Name>

import sys
import csv
import re

device_mapping = {}
lines = ''
mapping_line = []
dev_name = ''
domain = ''
export_domain = ''
export_mac_addr = ''
search_key = ''
line_count = 0
error_count = 0
bad_list = []

#Open the SQL output and build a dictionary from it so we have all devices and device pools
with open(sys.argv[1]) as sql_output:
  lines = sql_output.readlines()
for line in lines:
  #break line apart
  mapping_line = line.split(',')
  dev_name = mapping_line[0]
  domain = mapping_line[1][:6]
  #Create dictionary entry
  device_mapping[dev_name] = domain
#print the dictionary
#print device_mapping

# Now that we've built a device to domain mapping file we need to check the exported batch file against it
# read in the batch export file
with open(sys.argv[2]) as prime_export:
  csv_reader = csv.DictReader(prime_export, dialect='excel-tab')
  #open a file to write the modified output
  with open(sys.argv[3], 'w') as output:
    csv_writer = csv.writer(output, dialect='excel-tab')
    header = ['OrderType', 'Domain', 'ServiceArea', 'Processor Name', 'ProductName',
              'UserID', 'NewUserID', 'NewFirstName', 'NewLastName', 'MAC Address',
              'Subscriber Type']
    csv_writer.writerow(header)

    for csv_line in csv_reader:
      line_count += 1
      #set all the non interesting variables from the export
      export_order_type = csv_line['OrderType']
      export_service_area = csv_line['ServiceArea']
      export_processor_name = csv_line['Processor Name']
      export_product_name = csv_line['ProductName']
      export_user_id = csv_line['UserID']
      export_new_user_id = csv_line['NewUserID']
      export_new_last_name = csv_line['NewLastName']
      export_device_description = csv_line['Device Description']
      #Deleting A Line Number so don't include it
      export_subscriber_type = csv_line['Subscriber Type']
      
      #find the exported domain and the MAC
      #for this MAC if the domain in the export and the domain in the mapping file differ - then increment count
      export_domain = csv_line['Domain']
      export_mac_addr = csv_line['MAC Address']
      #print 'Line in CSV:     ' + export_domain + ', ' + export_mac_addr
      
      #find the actual domain value for this MAC
      # device_mapping[dev_name] is SEP<MAC> or Device Name if CUCI
      # export_mac_addr is <MAC> or Device Name if CUCI
      
      #if the export_mac_addr really is a MAC then prepend with SEP
      #it will be 12 chars long and not contain letters larger than F
      
      if (len(export_mac_addr) == 12 and not re.search( r'[g-z]', export_mac_addr, re.I)):
        #This was 12 characters long with only hex vals. Call it a MAC
        search_key = 'SEP' + export_mac_addr
      else:
        #This was probably some other device name
        search_key = export_mac_addr
      
      try:
        #Look up the current export row in the dictionary
        actual_domain = device_mapping[search_key]
        print 'Actual Domain Value: ', actual_domain
        if (export_domain != actual_domain):
          error_count += 1
          print 'Found mismatch #: ', error_count
        #Build the output file now that we know the correct domain
        actual_user_id = 'Pseudo' + actual_domain + export_new_user_id[-4:]
        current_row = [export_order_type, actual_domain, '', export_processor_name, 
                       export_product_name, '', actual_user_id, '', export_device_description, 
                       export_mac_addr, export_subscriber_type]
        csv_writer.writerow(current_row)
      except KeyError:
        #This will error out if the device wasn't found
        #We should handle these cases manually
        print 'The following device could not be mapped. Handle manually: ', export_mac_addr
        bad_list.append(export_mac_addr)
      
      
#Tell the user how many devices were in the wrong domain, and what we couldn't fix.
print 'Corrected ' + str(error_count) + ' devices out of ' + str(line_count) + ' in the export file!'
print 'Output available in file: ', sys.argv[3]
print 'The following devices could not be mapped:'
print bad_list