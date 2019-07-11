#!/bin/env python
#
# Looks up members of groups, and individual users in mkprojectnamemapfile.conf
# Generates condor usermap file in form:
#    * <username>  <ProjectName>
#    * <username2> <ProjectName>
#
# based on target it config file. 
#
#
# 

import argparse
from ConfigParser import ConfigParser
import logging
import grp
import pwd

class MapfileHandler(object):
    
    def __init__(self, config, section):
        logging.debug("Using config: %s   " % (config))
        self.config = config
        self.defaulttarget = config.get(section, 'defaulttarget')
        self.mapfile = config.get(section, 'mapfile')
        self.header = config.get('main','header')        
       
        
    def create_mapfile(self):
        filelines = []  # list of strings
        
        filelines.append(self.header)
            
        goptions = self.config.options('groupmappings')
        for go in goptions:
            target=self.config.get('groupmappings',go)
            logging.debug("group is %s target is %s" % (go, target))
            db = grp.getgrnam(go)
            for u in db.gr_mem:
                line = "* %s %s" % (u, target )
                filelines.append(line)
                
        uoptions = self.config.options('usermappings')
        for uo in uoptions:
            logging.debug("user is %s" % uo)
            target = self.config.get('usermappings', uo)
            line = "* %s %s" % (uo, target  )
            logging.debug("Line is %s" % line)
            filelines.append(line)
        
        dt = self.config.get('main','defaulttarget')
        line = "* /.*/ %s" % dt
        filelines.append(line)
        
        self.map = ""
        for line in filelines:
            self.map += "%s\n" % line
        logging.debug("Successfully build map...")
            

    def write_mapfile(self):
        filepath = self.config.get('main','mapfile')
        logging.debug("Writing map to %s" % filepath)
        f = open(filepath, 'w')
        f.write(self.map)
        


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', 
                        action="store", 
                        dest='conffile', 
                        default="/etc/condor/mkmaps.conf",
                        help='configuration file.')
    
    parser.add_argument('-d', '--debug', 
                        action="store_true", 
                        dest='debug', 
                        help='debug logging')
    args= parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = ConfigParser()
    config.read(args.conffile)
     
    mh = MapfileHandler(config)
    mh.create_mapfile()
    logging.debug("Map is : %s" % mh.map)
    mh.write_mapfile()
    

    