import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile as zf
import requests, io
import shutil
import html5lib
import plotly.graph_objs as go
import bz2
import xml.etree.cElementTree as et
from collections import defaultdict
import re
import pprint
import csv
import codecs
import cerberus
import sqlite3
from scipy import stats

url="https://s3.amazonaws.com/metro-extracts.mapzen.com/new-york_new-york.osm.bz2"
r=requests.get(url,timeout=1)

def count_tags(filename):
        tags=defaultdict()
        for event, element in et.iterparse(filename,events=("start",)):
            if element.tag not in tags.keys():
                tags[element.tag]=1
            elif element.tag in tags.keys():
                tags[element.tag]+=1
        return tags

with bz2.BZ2File(io.BytesIO(r.content)) as xml:
    tags=count_tags(xml)
    
tags

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')                    #Using Regex to create patterns to recognize potentional
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')            #problems with street names.

def key_type(element, keys):
    if element.tag == "tag":
        if lower.match(element.attrib.get('k')):                        #Adding counts to each of the types in the keys
            keys['lower']+=1                                            #dictionary.
        elif lower_colon.match(element.attrib.get('k')):
            keys['lower_colon']+=1
        elif problemchars.match(element.attrib.get('k')):
            keys['problemchars']+=1
        else:
            keys['other']+=1
        pass
        
    return keys



def process_map_keys(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}     #Returning dictionary with the counts.
    for _, element in et.iterparse(filename):
        keys = key_type(element, keys)

    return keys

with bz2.BZ2File(io.BytesIO(r.content)) as xml:
    keys=process_map_keys(xml)
keys

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) #Regex expression to search for street names at the end of terms.
expected = ["Airport","Alley","Avenue", "Boulevard","Bridge","Building","Circle", \
            "Close","Court","Concourse","Commerce", "Common","Commons","Crescent","Cross","Drive",\
            "Driveway","Expressway","Highway","Lane","Loop","Park","Parkway","Path",\
            "Place","Plaza""Ridge","Road","Route","Run","Slip","Square","Street","Suite",\
            "Terrace","Trace","Trail","Thruway","Turnpike","Walk","Walkway","Way"]
# List of expected names of streets.
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")                      #Function to determine if element has a street name.

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)               #Function to add street names that are not in expected to a list.
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit(osm_file):
    street_types = defaultdict(set)                                #Function to parse the xml document
    for event, elem in et.iterparse(osm_file, events=("start",)):  #And use the other functions in conjuction
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

with bz2.BZ2File(io.BytesIO(r.content)) as osm_file:
    street_type=audit(osm_file)

with open('C://Users/Zohaib/Desktop/Lectures/Udacity/Streets.txt','w') as f:     #Print the street types to a file called 
    pprint.pprint(street_type,f)                                                 #Streets.txt to create the mapping dictionary.

def is_phone_number(elem):
    return (elem.attrib['k'] == "contact:phone")
def audit_phone_number(phone_types, number):
    if re.match("[0-9]{3}-[0-9]{3}-[0-9]{3}",number):
        pass
    else:
        phone_types.append(number)
def audit_phone(osm_file):
    phone_types = []                                               #Function to parse the XMl document
    for event, elem in et.iterparse(osm_file, events=("start",)):  #And use the other functions in conjuction
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_number(tag):
                     audit_phone_number(phone_types, tag.attrib['v'])
    return phone_types

with bz2.BZ2File(io.BytesIO(r.content)) as osm_file:
     phone_type=audit_phone(osm_file)

with open("C://Users/Zohaib/Desktop/Lectures/Udacity/Phones.txt",'w') as f:
    pprint.pprint(phone_type,f)

mapping = { "Americas\n":"Americas",
            "Ave.":"Avenue",
            "ave":"Avenue",
            "avenue":"Avenue",
            "Ave,":"Avenue",
            "Avene":"Avenue",
            "Aveneu":"Avenue",
            "Ave":"Avenue",
            "AVE.":"Avenue",
            "AVE":"Avenue",
            "AVenue":"Avenue",
            "AVENUE":"Avenue",
            "bl":"Boulevard",
            "bl":"Building",
            "Blv.":"Boulevard",
            "boulevard":"Boulevard",
            "Blvd.":"Boulevard",
            "Blvd":"Boulevard",
            "BLDG":"Building",
            "BLD":"Building",
            "Cir":"Circle",
            "Ct.":"Court",
            "Ct":"Court",
            "Ctr":"Center",
            "Crst":"Cresecent",
            "Cres":"Crescent",
            "Cmn":"Common",
            "Concrs":"Concourse",
            "Cv":"Cove",
            "drive":"Drive",
            "DRIVE":"Drive",
            "Dr.":"Drive",
            "Dr":"Drive",
            "EAST":"East",
            "E":"East",
            "Expy":"Expressway",
            "Grn":"Green",
            "HIGHWAY":"Highway",
            "Hwy":"Highway",
            "LANE":"Lane",
            "lane":"Lane",
            "Ldg":"Landing",
            "Ln":"Lane",
            "N":"North",
            "north":"North",
            "Pky":"Parkway",
            "Pkwy":"Parkway",
            "PLAZA":"Plaza",
            "PARKWAY":"Parkway",
            "Plz":"Plaza",
            "Pl":"Place",
            "Pl":"Place",
            "PLACE":"Place",
            "Pt":"Point",
            "Rd.": "Road",
            "Rd":"Road",
            "ROAD":"Road",
            "Rdg":"Ridge",
            "route":"Route",
            "route":"Route",
            "road":"Road",
            "St.": "Street",
            "St": "Street",
            "st.":"Street",
            "st ":"Street",
            "street":"Street",
            "STREET":"Street",
            "ST":"Street",
            "Ste.":"Suite",
            "Ste":"Suite",
            "STE":"Suite",
            "S":"South",
            "SOUTH":"South",
            "STREET":"Street",
            "Turnlike":"Turnpike",
            "Tunrpike":"Turnpike",
            "Tunpike":"Turnpike",
            "Tpke":"Turnpike",
            "Tirnpike":"Turnpike",
            "Ter":"Terrace",
            "Trce":"Trace",
            "WAY":"Way",
            "W.":"West",
            "W":"West",
            "west":"West",
            "WEST":"West"}                  #Mapping for corrected names.
def update_name(name, mapping):
    mapping.keys()
    for i in mapping.keys():                #Function to replace all instances of the occurrences of the odd street type
        name=re.sub('(?<![a-zA-Z0-9])(?<=''){}(?!\.)(?![a-zA-Z0-9\-])'.format(i),mapping[i],name) #in the street names.
    return name                                                     #Uses the re.sub function to replace the street name
                                                                    #with all instances corrected.
def update_phone(phone):
    """Corrects all of the observed mistakes in phone numbers. Each of these mistakes is isolated into one change."""
    phone=re.sub('(\+01)','',phone)
    phone=re.sub('(\+1-)','',phone)
    phone=re.sub('\.','',phone)
    phone=re.sub('(\+1)','',phone)
    phone=re.sub('\+','',phone)
    phone=re.sub('(?<![0-9])1(?![0-9])','',phone)
    phone=re.sub('\(','',phone)
    phone=re.sub('\)','',phone)
    phone=re.sub(' ','',phone)
    if phone[3]!='-':
        phone=phone[0:3]+'-'+phone[3:]
    if phone[7]!='-':
        phone=phone[0:7]+'-'+phone[7:]
    phone
    return phone
            
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"                               #Name of output files.

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

import sche
SCHEMA = sche.schema                                          #Imports the relevant schema of the relevant elements.

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']                               #All of the fields wanted for each type of tag.

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    list=['id','user','uid','version','lat','lon','timestamp','changeset']
    listw=['id','user','uid','version','timestamp','changeset']
    list1=['id','key','value','type']
    list2=['id','node_id','position']
    if element.tag == 'node':
       node_attribs.update(element.attrib)
       k=node_attribs.keys()
       for i in k:
           if i not in list:
               del node_attribs[i]
       for i in element.iter("tag"):                                   #Takes each element and grabs only the relevant
           temp_dict=defaultdict()                                     #attributes for each type of tag in default dicts/
           if i==None:                                                 #lists.
               continue
           elif ':' in i.attrib.get('k'):
               temp_dict['id']=element.attrib.get('id')
               temp_dict['type']=i.attrib.get('k').partition(':')[0]
               temp_dict['key']=i.attrib.get('k').partition(':')[2]
               temp_dict['value']=i.attrib.get('v')
               tags.append(temp_dict)
           else:
               temp_dict['id']=element.attrib.get('id')
               temp_dict['key']=i.attrib.get('k')
               temp_dict['type']=default_tag_type
               temp_dict['value']=i.attrib.get('v')
               tags.append(temp_dict)
               
            
    elif element.tag == 'way':
        way_attribs.update(element.attrib)
        k=way_attribs.keys()
        for i in k:
            if i not in listw:
                del way_attribs[i]
        for a,i in enumerate(element.iter("nd")):
            temp_dict=defaultdict()
            if i==None:
                continue
            else:
                temp_dict['id']=element.attrib.get('id')
                temp_dict['node_id']=i.attrib.get('ref')
                temp_dict['position']=a
                way_nodes.append(temp_dict)
        for i in element.iter("tag"):
            temp_dict=defaultdict()
            if ':' in i.attrib.get('k'):
                temp_dict['id']=element.attrib.get('id')
                temp_dict['type']=i.attrib.get('k').partition(':')[0]
                temp_dict['key']=i.attrib.get('k').partition(':')[2]
                temp_dict['value']=i.attrib.get('v')
                tags.append(temp_dict)
            else:
                temp_dict['id']=element.attrib.get('id')
                temp_dict['key']=i.attrib.get('k')
                temp_dict['type']=default_tag_type
                temp_dict['value']=i.attrib.get('v')
                tags.append(temp_dict)

    
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':                                  #Returns the relevant lists for the function.
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = et.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:                     #Gets each type of relevant element in the xml file.
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.items())                        #Validates that the elements follow
        message_string = "\nElement of type '{0}' has the following errors:\n{1}" #Schema.
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

class UnicodeDictWriter(csv.DictWriter, object):
    
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if type(v)=='str' else v) for k, v in row.items()  #Extends csvwriter to handle
        })                                                                           #Unicode output.
        
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def process_map(file_in, validate):

    with codecs.open(NODES_PATH, 'w', encoding='utf-8') as nodes_file,\
        codecs.open(NODE_TAGS_PATH,'w', encoding='utf-8') as nodes_tags_file,\
        codecs.open(WAYS_PATH, 'w', encoding='utf-8') as ways_file,\
        codecs.open(WAY_NODES_PATH, 'w', encoding='utf-8') as way_nodes_file,\
        codecs.open(WAY_TAGS_PATH, 'w', encoding='utf-8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)  #Iteratively process each XML element
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)     #and write to csv(s)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


with bz2.BZ2File(io.BytesIO(r.content)) as osm_file:
    process_map(osm_file, validate=True)

db=sqlite3.connect("C://Users/Zohaib/Desktop/Lectures/Udacity/sqlite_windows/New_York.db")
cursor=db.cursor()   #Connects to the database with the data from the XML file.

cursor.execute("select user,count(*) from nodes group by user;")
number_of_posts=[x[1] for x in cursor.fetchall()];

cursor.execute("select user,count(*) from ways group by user;")
number2=[x[1] for x in cursor.fetchall()]
number_of_posts=number_of_posts+number2;                

stats.mstats.mquantiles(number_of_posts,prob=[.25,.5,.75])

posts_reasonable=[]
for i in number_of_posts:
    if i<=28:                                                      #Plots up to the 75th percentile of the results
        posts_reasonable.append(i)                                 #to avoid outliers.
figure=plt.figure(figsize=(12,12))
sns.distplot(posts_reasonable,bins=range(0,29,2),kde=False,color='Red')
plt.xlim(0,28)
plt.title("Number of Posts",fontsize=15)
plt.xlabel("Number of Posts",fontsize=15)
plt.ylabel("Count",fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15);

cursor.execute("select sum1+sum2+sum3+sum4+sum5 from (select count(*) as sum1 from nodes) as sub1,\
                (select count(*) as sum2 from node_tags) as sub2,\
                (select count(*) as sum3 from ways) as sub3,\
                (select count(*) as sum4 from way_tags) as sub4,\
                (select count(*) as sum5 from way_nodes) as sub5;")
cursor.fetchall()[0][0]

cursor.execute("select sum1+sum2 from (select count(*) as sum1 from nodes) as sub1,\
                (select count(*) as sum2 from ways) as sub2")
cursor.fetchall()[0][0]

cursor.execute("select count(*) from (select user from nodes group by user Union\
                select user from ways group by user) as sub;")
cursor.fetchall()[0][0]

cursor.execute("select count(*) from way_tags where key LIKE 'highway';")
cursor.fetchall()[0][0]

cursor.execute("select sub1.value,sub1.count,sub2.count from\
                (select value,count(*) as count from node_tags where key='cuisine' group by value) sub1 left join\
                (select value,count(*) as count from way_tags where key='cuisine' group by value) sub2\
                on sub1.value=sub2.value;")
cuisine1=cursor.fetchall()
cuisine={}
for i in cuisine1:
    if i[2]:
        cuisine[i[0]]=i[1]+i[2]
    else:
        cuisine[i[0]]=i[1]
sorted(cuisine.items(),key=lambda food: food[1],reverse=True)[0]