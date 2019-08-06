#!/bin/env python
#
# -- Looks up members of UNIX groups, and individual users for attributes.  
# -- Generates condor usermap(s) file in form:
#    * <username>  <attrname>
#    * <username2> <attrname>
# -- Sets map(s) active in /etc/condor/config.d/attrmaps.conf
# 

import argparse
from ConfigParser import ConfigParser
import logging
import grp
import pwd
import subprocess

class MakeMaps(object):
    
    def __init__(self, config):
        logging.debug("Using config: %s " % (config))
        self.config = config
        self.condorconfigdir = config.get('main','condorconfigdir')
        self.condorconfigname = config.get('main','condorconfigname')
        self.header = config.get('main','header')
        self.postrun = config.get('main','postrun')
        mlist = config.get('main','maps').split(',')
        self.maps = [  m.strip().lower() for m in mlist ]
        self.handlers = []
        for section in self.maps:
             mh = MapfileHandler(config, section)
             self.handlers.append(mh)

    def handle_all(self):
        self.make_all_maps()
        self.make_condorconfig()
        self.write_condorconfig()
        self.do_postrun()

    def make_all_maps(self):
        logging.debug("Making all maps... ")
        for handler in self.handlers:
            handler.create_mapfile()
            handler.write_mapfile()

    def make_condorconfig(self):
        logging.debug("Creating Condor config file. ")
        filelines = []  # list of strings
        filelines.append(self.header)
        for handler in self.handlers:
            line = handler.getcondorconfline()
            filelines.append(line)
        self.condorconfig = ""
        for line in filelines:
            self.condorconfig += "%s\n" % line
        logging.debug("Condor config: %s" % self.condorconfig)
    
    def write_condorconfig(self):
        filepath = "%s/%s" % (self.condorconfigdir, self.condorconfigname)
        logging.debug("Writing map to %s" % filepath)
        f = open(filepath, 'w')
        f.write(self.condorconfig)
        logging.debug("Successfully wrote config to %s" % filepath )    

    def do_postrun(self):
        logging.debug("Running post command...")
        cmd = self.config.get('main','postrun')
        return_code = subprocess.call(cmd, shell=True)
        logging.debug("Postrun return code is %s" % return_code) 

class MapfileHandler(object):
    
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.header = config.get('main','header')  
        self.mapfile = config.get(self.section, 'mapfile')
        self.attrname = config.get(self.section, 'attrname')
        self.defaulttarget = config.get(self.section, 'defaulttarget')
        self.gmsection = "%s-groupmappings" % section
        self.umsection = "%s-usermappings" % section
          
        
    def create_mapfile(self):
        logging.debug("Creating map...")
        filelines = []  # list of strings
        filelines.append(self.header)
            
        goptions = self.config.options(self.gmsection)
        for go in goptions:
            target=self.config.get(self.gmsection,go)
            logging.debug("group is %s target is %s" % (go, target))
            db = grp.getgrnam(go)
            for u in db.gr_mem:
                line = "* %s %s" % (u, target )
                filelines.append(line)
                
        uoptions = self.config.options(self.umsection)
        for uo in uoptions:
            logging.debug("user is %s" % uo)
            target = self.config.get(self.umsection, uo)
            line = "* %s %s" % (uo, target  )
            logging.debug("Line is %s" % line)
            filelines.append(line)
        
        dt = self.config.get(self.section,'defaulttarget')
        line = "* /.*/ %s" % dt
        filelines.append(line)
        
        self.map = ""
        for line in filelines:
            self.map += "%s\n" % line
        logging.debug("Successfully built map...")
            

    def write_mapfile(self):
        filepath = self.config.get(self.section,'mapfile')
        logging.debug("Writing map to %s" % filepath)
        f = open(filepath, 'w')
        f.write(self.map)
        logging.debug("Successfully wrote map to %s" % filepath )

    def getcondorconfline(self):
        logging.debug("Making config line...")
        #use FEATURE : SetJobAttrFromUsermap(projectName, Owner, ProjectNameMap, /etc/condor/projectname.usermap)
        cline = "use FEATURE : SetJobAttrFromUsermap(%s, Owner, %sMap, %s)" % (self.attrname,
                                                                                       self.attrname,
                                                                                       self.mapfile)
        logging.debug("Condor config line: %s" % cline)
        return cline
    

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s (UTC) [%(levelname)s] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s')
    
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
    
    mm = MakeMaps(config)
    mm.handle_all()

       
    

    