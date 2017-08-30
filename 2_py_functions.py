# The function calls that I had made to do data munging is listed after all the
# functions.  They are grouped by each section.  Please refer to 
# "1_pdf_4P_OSM_FULLERTON_JR.pdf" for more details on the processes

# After all the py functions, there are list of function calls made at each section
# to run them, please uncomment them.  If you prefer, you can uncomment all at 
# the same time and it will just run sequentially.


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
from scipy import stats
import re
import csv
import codecs

OSM_FILE = "fullerton_ca.osm"  # Replace this with your osm file

#-----------------------------------------------------------------------------#
def cut_sample_file(k, filename):
    # cut sample_file size by k
    # Parameter: take every k-th top level element
    # code provided by Udacity

    def get_element(osm_file, tags=('node', 'way', 'relation')):
        """Yield element if it is the right type of tag
    
        Reference:
        http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
        """
        context = iter(ET.iterparse(osm_file, events=('start', 'end')))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()


    with open(filename, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(OSM_FILE)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')

#-----------------------------------------------------------------------------#
def update_dict_str_count(in_dict, key):
    # update count in dictionary in_dict
    # increment the count by 1 for in_dict[key] if key already exists
    # if not create a new 'key' and set value to 1
    if key in in_dict:
        in_dict[key] += 1
    else:
        in_dict[key] = 1

    return in_dict

#-----------------------------------------------------------------------------#
def get_tags(filename):
    # prints the dictionary of tag and number of times it appear in filename
    
    tag_dict = {}
    tree = ET.ElementTree(file=filename)
    
    for elem in tree.iter():
        tag_dict = update_dict_str_count(tag_dict, elem.tag)
            
    print 'dictionary of tag and counts'    
    pprint.pprint(tag_dict)
            
    return None

#-----------------------------------------------------------------------------#
def get_tag_keys(filename):
    # prints dictionary tag_key_list, which holds all the keys 
    # in the 'tag' node of xml filename, and the number of times they appear
    
    tag_key_list = {}
    
    tree = ET.ElementTree(file=filename)
    
    for elem in tree.iter():
        if elem.tag == 'tag':
            key = elem.attrib['k']
            tag_key_list = update_dict_str_count(tag_key_list, key)
        
    print '\nkeys in \'tag\' nodes and counts'
    pprint.pprint(tag_key_list)
            
    return None


#-----------------------------------------------------------------------------#
def str_is_int(number):
    # this function returns True if 'number' can be converted to an integer
    # or else returns False.
    try:
        number = int(number)
        return True
    except ValueError:
        return False
    
#-----------------------------------------------------------------------------#
def str_is_float(number):
    # this function returns True if 'number' can be converted to a float
    # or else returns False.
    try:
        number = float(number)
        return True
    except ValueError:
        return False


#-----------------------------------------------------------------------------#
def check_lat_lon(filename):
    # find the 'node' tag in filename and 
    # get 'lat' and 'lon' values
    # returns the stat for 'lat' and 'lon' and number of non-float values
    # in 'lat' and 'lon'    
    lat = []
    lon = []
    lat_not_float = []
    lon_not_float = []
    
    tree = ET.ElementTree(file=filename)
    
    for elem in tree.iter():
        if elem.tag == 'node':

            if str_is_float(elem.attrib['lat']):
                lat.append(float(elem.attrib['lat']))
            else:
                lat_not_float.append(elem.attrib['lat'])
                
            if str_is_float(elem.attrib['lon']):
                lon.append(float(elem.attrib['lon']))
            else:
                lon_not_float.append(elem.attrib['lon'])
                
    print 'Stats for latitude'
    print stats.describe(lat)
    print '\nStats for longitude'
    print stats.describe(lon)
    print '\n# of non-float latitude'
    print len(lat_not_float)
    print '\n# of non-float longitude'
    print len(lon_not_float)
    
    return None


#-----------------------------------------------------------------------------#
def check_tag_attrib_is_int(filename, in_key):
    # prints two dataset: one with value of integer and another that is not integer
    # it first check if a node of a 'filename' has a tag of 'tag'
    # if it is, checks whether the attrib['k'] equals 'in_key' 
    # it then checks if the value is integer or not and put in to a respective list
    # and then prints the list
    
    data_int = set()
    data_not_int = set()
    
    tree = ET.ElementTree(file=filename)

    for elem in tree.iter():
        if elem.tag == 'tag':
            if (elem.attrib['k'] == in_key):
                value = elem.attrib['v']
                if str_is_int(value):
                    data_int.add(int(value))
                else:
                    data_not_int.add(value)
                    
    print 'data which are integer'
    print data_int
    print '\ndata which are not integer'
    print data_not_int
    
    return None

#-----------------------------------------------------------------------------#
def check_tag_attrib_is_str(filename, in_key):
    # prints a dictionary of a value and its count
    # it first check if a node of a 'filename' has a tag of 'tag'
    # if it is, it checks whether the attrib['k'] equals 'in_key' 
    # if it is, it puts in a list 
    # and then prints the final list
        
    str_dict = {}
    
    tree = ET.ElementTree(file=filename)

    for elem in tree.iter():
        if elem.tag == 'tag':
            if (elem.attrib['k'] == in_key):
                str_dict = update_dict_str_count(str_dict, elem.attrib['v'])
                    
    print 'data strings for ', in_key
    pprint.pprint(str_dict)

    return None


#-----------------------------------------------------------------------------#
def get_street_types(filename):
    # print the street type from the 'filename' and number of times they occur
    # it first check if a node of a 'filename' has a tag of 'tag'
    # if it is, it checks whether the attrib['k'] equals 'addr:street' 
    # if it is, it splits by ' ' and put the value in the last index into 'data_str'
    # and keep track of counts
    # and then prints the final list and the count
    
    data_str = {}
    
    tree = ET.ElementTree(file=filename)

    for elem in tree.iter():
        if elem.tag == 'tag':
            if (elem.attrib['k'] == 'addr:street'):
                stype = elem.attrib['v'].split(' ')[-1]
                data_str = update_dict_str_count(data_str, stype)
                if stype in data_str:
                    data_str[stype] += 1
                else:
                    data_str[stype] = 1

    print 'list of street types and counts'
    pprint.pprint(data_str)

    return None


#-----------------------------------------------------------------------------#
def replace_tag_value(elem, newvalue):
    # replaces 'elem.attrib['v']' value to 'newvalue'
    # and prints the change       
                
    print elem.attrib
    elem.attrib['v'] = newvalue
    print 'replaced with'
    print elem.attrib
    print '------\n'
    
    return elem
    
#-----------------------------------------------------------------------------#
def edit_tag_error_value_old(filename):
    # edit the values in 'filename' 
    # using the map dictionaries declared below to edit old to new
    
    map_postcode = {'CA 90638': '90638','Disneyland':'92802'}
    map_state = {'ca':'CA'}
    map_city = {'la habra':'La Habra'}
    map_street = {'E La Palma Ave #G':'East La Palma Avenue',' stephens':'North Euclid Street','stephens':'North Euclid Street'}
    map_street_type = {'Blv':'Boulevard','Blvd':'Boulevard','Blvd.':'Boulevard','Dive':'Drive','Wy':'Way'}
    map_street_card_dir = {'E':'East','E.':'East','W':'West','W.':'West','N':'North','N.':'North','S':'South','S.':'South'}
    
    tree = ET.ElementTree(file=filename)

    for elem in tree.iter():
        if elem.tag == 'tag':
            # edit addr:postcode
            if (elem.attrib['k'] == 'addr:postcode'):
                if elem.attrib['v'] in map_postcode:
                    elem = replace_tag_value(elem, map_postcode[elem.attrib['v']])
                    
            # edit addr:state
            elif (elem.attrib['k'] == 'addr:state'):
                if elem.attrib['v'] in map_state:
                    elem = replace_tag_value(elem, map_state[elem.attrib['v']])
                
            # edit addr:city
            elif (elem.attrib['k'] == 'addr:city'):
                if elem.attrib['v'] in map_city:
                    elem = replace_tag_value(elem, map_city[elem.attrib['v']])

            # edit addr:street
            elif (elem.attrib['k'] == 'addr:street'):
                if elem.attrib['v'] in map_street:
                    elem = replace_tag_value(elem, map_street[elem.attrib['v']])
                else:
                    street_in_list = elem.attrib['v'].split(' ')
                    if (street_in_list[-1]) in map_street_type:
                        print elem.attrib
                        street_in_list[-1] = map_street_type[street_in_list[-1]]
                        elem.attrib['v'] = ' '.join(street_in_list)
                        print 'replaced with'
                        print elem.attrib
                        print '-------------\n'
                    if (street_in_list[0]) in map_street_card_dir:
                        print elem.attrib
                        street_in_list[0] = map_street_card_dir[street_in_list[0]]
                        elem.attrib['v'] = ' '.join(street_in_list)
                        print 'replaced with'
                        print elem.attrib
                        print '-------------\n'

    return None
    
#-----------------------------------------------------------------------------#
def remove_bad_children(tree):
    # manually remove the child node with bad data
        
    for pnode in tree.findall('way'):
        if pnode.attrib['id'] == '127846553':
            for child in pnode:
                if child.get('k') == 'addr:housenumber':
                    pnode.remove(child)
    
    return tree
   
#-----------------------------------------------------------------------------#
def edit_tag_error_value(currfile, newfile):
    # edit the values in 'filename' 
    # by first calling remove_bad_children(tree) and then
    # using the map dictionaries declared below to edit old to new
    
    # edit errors in 'currfile' and write to 'newfile'
    map_postcode = {'722A':'92821', 'CA 90638':'90638','Disneyland':'92802', 'CA 92870':'92870', 
                    'CA 90630':'90630','CA 90631':'90631', '92832-2095':'92832', 
                    'CA 90680':'90680','92870-5615':'92870'}
    map_state = {'ca':'CA', 'California':'CA'}
    map_city = {'la habra':'La Habra','Anahiem':'Anaheim','Cyprus':'Cypress','Diamon Bar':'Diamond Bar',
                'fullerton':'Fullerton','whittier':'Whittier'}
    map_street = {'E La Palma Ave #G':'East La Palma Avenue',' stephens':'North Euclid Street',
                  'S State College Blvd #101':'S State College Blvd','503':'Disneyland Drive',
                  'East Miraloma Avenue Unit 6':'East Miraloma Avenue','7':'Disneyland Drive',
                  'Sr-57 @ Lambert Rd Ne Cnr':'Lambert Road', 'Greenbriar':'Greenbriar Lane',
                  'N Brea Blvd #245':'North Brea Boulevard'}
    map_street_type = {'Av':'Avenue','Ave':'Avenue','Ave,':'Avenue','Ave.':'Avenue',
                       'Aven':'Avenue',u'Ave\u200e':'Avenue','Blv':'Boulevard','Blvd':'Boulevard',
                       'Blvd.':'Boulevard','Boulvard':'Boulevard','Cnr':'Courner',
                       'Dive':'Drive','Dr.':'Drive','Rd':'Road','Rd.':'Road','St':'Street',
                       'St.':'Street','Sttreet':'Street','street':'Street','Wy':'Way'}
    map_street_card_dir = {'E':'East','E.':'East','W':'West','W.':'West','N':'North','N.':'North','S':'South','S.':'South'}
    
    tree = ET.ElementTree(file=currfile)
    
    # manual removal of bad children data
    tree = remove_bad_children(tree)

    # use mapping to edit errors
    for elem in tree.iter():
        if elem.tag == 'tag':
            # edit addr:postcode
            if (elem.attrib['k'] == 'addr:postcode'):
                if elem.attrib['v'] in map_postcode:
                    elem = replace_tag_value(elem, map_postcode[elem.attrib['v']])
                    
            # edit addr:state
            elif (elem.attrib['k'] == 'addr:state'):
                if elem.attrib['v'] in map_state:
                    elem = replace_tag_value(elem, map_state[elem.attrib['v']])
                
            # edit addr:city
            elif (elem.attrib['k'] == 'addr:city'):
                if elem.attrib['v'] in map_city:
                    elem = replace_tag_value(elem, map_city[elem.attrib['v']])

            # edit addr:street
            elif (elem.attrib['k'] == 'addr:street'):
                if elem.attrib['v'] in map_street:
                    elem = replace_tag_value(elem, map_street[elem.attrib['v']])
                else:
                    street_in_list = elem.attrib['v'].split(' ')
                    if (street_in_list[-1]) in map_street_type:
                        print elem.attrib
                        street_in_list[-1] = map_street_type[street_in_list[-1]]
                        elem.attrib['v'] = ' '.join(street_in_list)
                        print 'replaced with'
                        print elem.attrib
                        print '-------------\n'
                    if (street_in_list[0]) in map_street_card_dir:
                        print elem.attrib
                        street_in_list[0] = map_street_card_dir[street_in_list[0]]
                        elem.attrib['v'] = ' '.join(street_in_list)
                        print 'replaced with'
                        print elem.attrib
                        print '-------------\n'

    tree.write(newfile)
                            
    return None
    
  
#-----------------------------------------------------------------------------#
# This is an edited version of code provided in the Udacity lesson        
def create_clean_csv(OSM_FILE_CLEAN):
    # create clean csv files from 'OSM_FILE_CLEAN'
    
    NODES_PATH = "nodes.csv"
    NODE_TAGS_PATH = "nodes_tags.csv"
    WAYS_PATH = "ways.csv"
    WAY_NODES_PATH = "ways_nodes.csv"
    WAY_TAGS_PATH = "ways_tags.csv"

    LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
    PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

    # Make sure the fields order in the csvs matches the column order in the sql table schema
    NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
    NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
    WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_NODES_FIELDS = ['id', 'node_id', 'position']

    def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                      problem_chars=PROBLEMCHARS, default_tag_type='regular'):
        """Clean and shape node or way XML element to Python dict"""

        node_attribs = {}
        way_attribs = {}
        way_nodes = []
        tags = []  # Handle secondary tags the same way for both node and way elements

        if element.tag == 'node':
            for fld in NODE_FIELDS:
                node_attribs[fld] = element.get(fld)

            for child in element:
                if child.tag == 'tag':
                    if (PROBLEMCHARS.search(child.attrib['k']) == None):
                        ctag = {}
                        ctag['id'] = element.get('id')
                        ctag['value'] = child.attrib['v']
                        if child.attrib['k'].find(':') > 0:
                            colonidx = child.attrib['k'].find(':')
                            ctag['key'] = child.attrib['k'][colonidx + 1:]
                            ctag['type'] = child.attrib['k'][:colonidx]
                        else:
                            ctag['key'] = child.attrib['k']
                            ctag['type'] = default_tag_type
                        tags.append(ctag)        
            return {'node': node_attribs, 'node_tags': tags}

        elif element.tag == 'way':
            for fld in WAY_FIELDS:
                way_attribs[fld] = element.get(fld)
            wayid = element.get('id')
            pos_count = 0
            for child in element:
                if child.tag=='nd':
                    wn = {}
                    wn['id'] = wayid
                    wn['node_id'] = child.get('ref')
                    wn['position'] = pos_count
                    pos_count += 1
                    way_nodes.append(wn)
                elif child.tag=='tag':
                    if (PROBLEMCHARS.search(child.attrib['k']) == None):
                        ctag = {}
                        ctag['id'] = element.get('id')
                        ctag['value'] = child.attrib['v']
                        if child.attrib['k'].find(':') > 0:
                            colonidx = child.attrib['k'].find(':')
                            ctag['key'] = child.attrib['k'][colonidx + 1:]
                            ctag['type'] = child.attrib['k'][:colonidx]
                        else:
                            ctag['key'] = child.attrib['k']
                            ctag['type'] = default_tag_type
                        tags.append(ctag)
            return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        
    # ================================================== #
    #               Helper Functions                     #
    # ================================================== #
    def get_element(osm_file, tags=('node', 'way', 'relation')):
        """Yield element if it is the right type of tag"""

        context = ET.iterparse(osm_file, events=('start', 'end'))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()

    class UnicodeDictWriter(csv.DictWriter, object):
        """Extend csv.DictWriter to handle Unicode input"""

        def writerow(self, row):
            super(UnicodeDictWriter, self).writerow({
                k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
            })

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)


    # ================================================== #
    #               Main Function                        #
    # ================================================== #
    def process_map(file_in, validate):
        """Iteratively process each XML element and write to csv(s)"""

        with codecs.open(NODES_PATH, 'wb') as nodes_file, \
             codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
             codecs.open(WAYS_PATH, 'wb') as ways_file, \
             codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
             codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

            nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
            node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
            ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
            way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
            way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

            for element in get_element(file_in, tags=('node', 'way')):
                el = shape_element(element)
                if el:
                    if element.tag == 'node':
                        nodes_writer.writerow(el['node'])
                        node_tags_writer.writerows(el['node_tags'])
                    elif element.tag == 'way':
                        ways_writer.writerow(el['way'])
                        way_nodes_writer.writerows(el['way_nodes'])
                        way_tags_writer.writerows(el['way_tags'])


    if __name__ == '__main__':
        # Note: Validation is ~ 10X slower. For the project consider using a small
        # sample of the map when validating.
        process_map(OSM_FILE_CLEAN, validate=False)              
                    
                                
#-----------------------------------------------------------------------------#
def peek_csv(filename, fld):
    # print the first 5 lines of csv 'filename' w,th fieldnames = 'fld'
    # and print the number of rows of data
    n = 0
    with open(filename,'rb') as f:
        r = csv.DictReader(f, fieldnames = fld)
        for line in r:
            if n < 5:
                print line
            n += 1
        print '\nnumber of rows: ', n
    return None            
                    
                    
                    
#-----------------------------------------------------------------------------#
# CODES CALLED IN 
# 1. Clean and observe the smaller dataset which took every 50-th top elements               
#-----------------------------------------------------------------------------#

#print '-------------------------------------------------------------------'
#print '1. Clean and observe the smaller dataset which took every 50-th top elements'
#SAMPLE_FILE_50 = "fullerton_sample_k_50.osm"
#cut_sample_file(50, SAMPLE_FILE_50)
#get_tags(SAMPLE_FILE_50)
#get_tag_keys(SAMPLE_FILE_50)
#check_lat_lon(SAMPLE_FILE_50)
#check_tag_attrib_is_int(SAMPLE_FILE_50, 'addr:housenumber')
#check_tag_attrib_is_int(SAMPLE_FILE_50, 'addr:postcode')
#check_tag_attrib_is_str(SAMPLE_FILE_50, 'addr:state')
#check_tag_attrib_is_str(SAMPLE_FILE_50, 'addr:city')
#check_tag_attrib_is_str(SAMPLE_FILE_50, 'addr:street')
#get_street_types(SAMPLE_FILE_50)
            
#-----------------------------------------------------------------------------#
# CODES CALLED IN 
# 2. Re-running the checks by using dataset which took every 10-th top level element  
#-----------------------------------------------------------------------------#

#print '-------------------------------------------------------------------'
#print '2. Re-running the checks by using dataset which took every 10-th top level element '
#SAMPLE_FILE_10 = "fullerton_sample_k_10.osm"
#cut_sample_file(10, SAMPLE_FILE_10)
#get_tags(SAMPLE_FILE_10)
#get_tag_keys(SAMPLE_FILE_10)
#check_lat_lon(SAMPLE_FILE_10)
#check_tag_attrib_is_int(SAMPLE_FILE_10, 'addr:housenumber')
#check_tag_attrib_is_int(SAMPLE_FILE_10, 'addr:postcode')
#check_tag_attrib_is_str(SAMPLE_FILE_10, 'addr:state')
#check_tag_attrib_is_str(SAMPLE_FILE_10, 'addr:city')
#check_tag_attrib_is_str(SAMPLE_FILE_10, 'addr:street')
#get_street_types(SAMPLE_FILE_10)
#edit_tag_error_value_old(SAMPLE_FILE_10)


#-----------------------------------------------------------------------------#
# CODES CALLED IN 
# 3. Clean and observe the full data set  
#-----------------------------------------------------------------------------#

#print '-------------------------------------------------------------------'
#print '3. Clean and observe the full data set '

## <CHECKING THE FULL FILE>
#get_tags(OSM_FILE)
#get_tag_keys(OSM_FILE)
#check_lat_lon(OSM_FILE)
#check_tag_attrib_is_int(OSM_FILE, 'addr:housenumber')
#check_tag_attrib_is_int(OSM_FILE, 'addr:postcode')
#check_tag_attrib_is_str(OSM_FILE, 'addr:state')
#check_tag_attrib_is_str(OSM_FILE, 'addr:city')
#check_tag_attrib_is_str(OSM_FILE, 'addr:street')
#get_street_types(OSM_FILE)
#edit_tag_error_value_old(OSM_FILE)

## <CREATING A NEW CLEAN FILE>
#OSM_FILE_CLEAN = "fullerton_ca_clean.osm"
#edit_tag_error_value(OSM_FILE, OSM_FILE_CLEAN)

## <CHECKING THE NEW CLEAN FILE>
#check_tag_attrib_is_int(OSM_FILE_CLEAN, 'addr:housenumber')
#check_tag_attrib_is_int(OSM_FILE_CLEAN, 'addr:postcode')
#check_tag_attrib_is_str(OSM_FILE_CLEAN, 'addr:state')
#check_tag_attrib_is_str(OSM_FILE_CLEAN, 'addr:city')
#check_tag_attrib_is_str(OSM_FILE_CLEAN, 'addr:street')
#get_street_types(OSM_FILE_CLEAN)


#-----------------------------------------------------------------------------#
# CODES CALLED IN 
# 4.  Create csv files, create sql tables, and insert csv files into sql
#-----------------------------------------------------------------------------#

#print '-------------------------------------------------------------------'
#print '4.  Create csv files, create sql tables, and insert csv files into sql'
#OSM_FILE_CLEAN = "fullerton_ca_clean.osm"
#NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
#NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
#WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
#WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
#WAY_NODES_FIELDS = ['id', 'node_id', 'position']
#create_clean_csv(OSM_FILE_CLEAN)
#peek_csv('nodes.csv', NODE_FIELDS)
#peek_csv('nodes_tags.csv', NODE_TAGS_FIELDS)
#peek_csv('ways_nodes.csv', WAY_TAGS_FIELDS)
#peek_csv('ways_tags.csv', WAY_NODES_FIELDS)















