#!/usr/bin/python
#Build LDAP filters for Prime from a list of CSV data in the following format
#DOMAIN1,SITEID1
#DOMAIN1,SITEID2
#DOMAIN2,SITEID3
#
#Into the following LDAP query format
#DOMAIN1
#(|(SiteID=SITEID1)(SiteID=SITEID2))(objectClass=userProxy)

import sys

#print 'Arg0 ', sys.argv[0]
#print 'Arg1 ', sys.argv[1]

last_domain=''
current_domain=''
current_site=''
domain_index=0
line_index=0
site_list=[]
domain_site_list=[]
domain_list=[]
query_string=''

with open(sys.argv[1]) as f:
    lines = f.readlines()
for line in lines:
    word_list = line.split(',')
    current_domain = word_list[0]
    current_site = word_list[1][:6]
    #print 'Word List: ', word_list
    #print 'Word List [0]:', word_list[0]
    #print 'Word List [1]:', word_list[1]
    #print 'Current Domain: ', current_domain
    #print 'Current Site: ', current_site
    if (current_domain != last_domain):
      #We started a new domain so we should probably dump all the stuff from the last one and start new
      if (line_index > 0):
        domain_site_list.append(site_list)
        #print 'Appending last domain to domain_list: ', last_domain
        #print line_index
        domain_list.append(last_domain)
        domain_index += 1
      #blank out the site list since it has been appended
      site_list = []
      
    #This needs to be done every line no matter what
    #We should really only add a site if it does not yet exist in the site list. Handle duplicates from the input.
    try:
      #Find the index of the current_site in the site_list. Should throw exception if it doesn't exist (is unique)
      #print 'Current Site: ', current_site
      #print 'Index Value of Current Site Duplicate: ', site_list.index(current_site)
      #print 'Duplicate found because this is printed'
      check_dup_index = site_list.index(current_site)
    except ValueError:
      #print 'No duplicate - carry on'
      #Only add this to the list if the value error was thrown, meaning it wasn't found
      site_list.append(current_site)
    last_domain = current_domain
    line_index += 1
    #print 'Current Domain Index: ', domain_index
    #print 'Current Line Index: ', line_index
    #print 'Current site_list[]: ', site_list
    #print 'Current domain_site_list: ', domain_site_list

#Print out the very last line to our 2d array and the very last domain name
#print 'Reached the last line'
domain_site_list.append(site_list)
domain_list.append(current_domain)

#print 'Final Domain Site List:'
#print domain_site_list[3]
#print domain_list[3]

#Now that we've built our data structures we can pretty print them
#Loop through a list of lists to output query
#print len(domain_site_list)
#print len(domain_list)

if (len(domain_site_list) != len(domain_list)):
  #Something went terribly wrong and the number of lists differs from the number of names
  print "Something went wrong and the length of the Domain name list differs from the length of the SiteIDs list"
  sys.exit(1)

for index in range(len(domain_list)):
  #print 'Current Index: ', index
  #print 'Current Index Name: ', domain_list[index]
  query_string = '(|'
  for site_index in range(len(domain_site_list[index])):
    #print 'Current Site Index:', site_index
    #print 'Current Site Index Name: ', domain_site_list[index][site_index]
    current_site = domain_site_list[index][site_index]
    query_string = query_string + '(SiteID=' + current_site + ')'
  #Close out the query and print
  query_string = query_string + ')(objectClass=userProxy)'
  print 'LDAP Query for Domain: ', domain_list[index]
  print query_string
  print