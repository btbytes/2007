#!/usr/bin/env python

# gen-sa.py http://btbytes.googlecode.com/svn/trunk/sqlrecipes/gen-sa.py
# Copyright (C) 2007, Pradeep Kishore Gowda pradeep.gowda@gmail.com
#
# Script to generate SQLAlchemy Table definition from ML Dataset's metadata
#
# This script is released under the 
# MIT License: http://www.opensource.org/licenses/mit-license.php

import sys,os

def read_attrs(lines):
    attrs = []
    for l in lines:
        atype, dvalues, maxlen = 'String', 0.0, 0
        if len(l.split(':')) > 1:
            name, domain =  l.split(':')
        else:
            continue
        if domain.find('continuous.') > -1:
            atype = 'Float'
        else:
            dvalues = domain.split(',')
            maxlen =  max([len(v) for v in dvalues])
            
        dic = {'name' : name.replace('-', '_'),
               'type' : atype,
               'values' : dvalues,
               'maxlen' : maxlen,
            }
        attrs.append(dic)
    return attrs

def main(fname):
    lines = open(fname, 'rb').readlines()
    lines = [l.rstrip() for l in lines if not ( l.startswith('|') or
    l.startswith(' ') or len(l)<2)]
    dclass_domain = lines[0].split(',')    
    attrs = read_attrs(lines)
    tblname = fname.split('/')[-1]
    tblname = tblname.split('.')[0]
    print "#Table Definition"
    txt =  '%(tblname)s = Table("%(tblname)s", metadata,\n' % ({'tblname':tblname})
    for a in attrs:
        txt += '    Column("%s", %s),\n' % (a['name'], a['type'])
    txt = txt[:-2] #remove the trailing comma
    txt += '\n)'
    print txt
    txt = "#Class definition\n"
    txt += """class %s (object):
    def __init__(self):
        pass\n""" % tblname.capitalize()
    
    txt += 'mapper(%s, %s)' % (tblname.capitalize(), tblname)
    print txt
    
    
if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print 'Usage: ',__file__,' datafile.names'
        exit(0)
    else:
        fname = sys.argv[1]        
        main(fname)
