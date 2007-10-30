==================================
 Installing MonetDB on Ubuntu 7.04
==================================

:Author: Pradeep Kishore Gowda
:address: pradeep.gowda@gmail.com
    http://www.btbytes.com

:revision: 1.0
:date: Jul. 12, 2007

:copyright: Copyright (c) 2007 Pradeep Kishore Gowda.  All Rights Reserved.

:abstract: This document attempts to help you to install MonetDB on your Ubuntu system.

.. contents::

.. sectnum::


Introduction
============

Monetdb is a fast database based on the Colum oriented database principles. Download it from
`<http://monetdb.cwi.nl>`_.
Install some dependencies first::

.. code-block:: bash

    $ sudo apt-get install autoconf automake libtool gawk 
    $ sudo apt-get install libxml1 libxml2 libxml2-dev libxml-dev

Run the bundled installation script::

    $ ./monetdb-install.sh --prefix=$HOME --build=$HOME/tmp \
      --enable-sql --enable-xquery --enable-optimise 

