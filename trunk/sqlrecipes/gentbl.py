#!/usr/bin/env python

# tblgen.py http://btbytes.googlecode.com/svn/trunk/sqlrecipes/gentbl.py
# Copyright (C) 2007, Pradeep Kishore Gowda btbytes@gmail.com
#
# Script to create SQL table creation statements from 
# a given UCI Machine Learning repository format 
# data.names format file. 
#
# This script is released under the 
# MIT License: http://www.opensource.org/licenses/mit-license.php


import sys,os

def read_attrs(lines):
    attrs = []
    for l in lines:
        atype, dvalues, maxlen = 'VARCHAR', 0.0, 0
        if len(l.split(':')) > 1:
            name, domain =  l.split(':')
        else:
            continue
        if domain.find('continuous.') > -1:
            atype = 'FLOAT'
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
    #    print attrs
    txt =  'CREATE TABLE %s (' % (fname.split('.')[0])
    for a in attrs:
        txt += '%s %s' % (a['name'], a['type'])
        
        if a['type'] != 'FLOAT':
            txt += '(%s)' %( a['maxlen'],)
        txt += ','
    txt = txt[:-1]
    txt += ');'
    print txt
    
if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print 'Usage: ',__file__,' datafile.names'
        exit(0)
    else:
        fname = sys.argv[1]        
        main(fname)
