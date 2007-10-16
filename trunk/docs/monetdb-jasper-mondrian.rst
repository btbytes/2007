=============================================================================
Open Source Business Intelligence with  MonetDB, Jasper Reports and Mondrian
=============================================================================

:Author: Pradeep Kishore Gowda
:Version: 0.1
:Date: 2007-08-09


Introduction
============

.. Attention:: The setup instructions given here are tested on `Ubuntu Linux  7.04 <http://ubuntulinux.org>`_ 32 bit version.



Installing MonetDB
==================

Monetdb is a fast database based on the Colum oriented database principles. Download it from
http://monetdb.cwi.nl.

Run the bundled installation script::

    $ ./monetdb-install.sh --prefix=$HOME --build=$HOME/tmp \
       --enable-sql --enable-xquery --enable-optimise 


Testing MonetDB installation
============================

The 

Installing Jasper Server 
========================

Download the `jasperserver-x-y-linux-installer.bin` from `<http://jaspersoft.com>`_ website.

Launch the installer::

    $ cp jasperserver-x-y-linux-installer.bin /tmp
    $ cd /tmp
    $ ./jasperserver-x-y-linux-installer.bin
    
This will launch a GUI installer.

 * Click `Forward`. 
 * Accept the license.
 * Choose the installation directory. Accept the default value.
 * Choose `Tomcat` as the app server
 * Select `MySQL` as the database server
 * If you already have a working mysql setup on your system,
   choose `I wish to use an existing mysql database` option. Else, choose the
   default choice of `bundled mysql`. 
 * Choose `use the bundled Tomcat` option.
 * Accept default values for Tomcat ports unless you already have other applications running in that port.

 * [optional] If you had chosen to use your existing mysql, enter `/usr/bin/` in the Mysql binary directory field and click forward. Enter database credentials when prompted.
 * Click `Yes` for sample databases and reports.
 * An administrator user -- `jasperadmin` will be created. Enter the passwords and rememeber them. You will need them later to login to the jasper server.
 * You can skip the mail settings screens, if you do not want to send reports via mail
 * Install iReport. Select 'Yes' and click 'Forward'.
 * Click forward. The installer will copy the files to the selected locations.

Installation Notes
==================

Please refer to the installation guide for complete
information on installation. The document is found at ::

    <install-dir>/docs/JasperServer-Install-Guide.pdf

Once installed, the JasperServer login page URL is ::

    http://<your_host>:<port>/jasperserver

Default Login for Tomcat ::

    http://<your_host>:8080/jasperserver

Default Login for JBoss ::

    http://<your_host>:8080/jasperserver

The default login credentials created during the
installation are ::

    Username: jasperadmin
    Password: <password>

If you installed the sample data, you will also have a
default non-administrative user ::

    Username:  joeuser
    Password:  joeuser


The main application database configuration file for Tomcat is ::

    <tomcat-dir>/webapps/jasperserver/META-INF/context.xml

    

.. Tip:: You can check which ports are in using `nmap localhost` 


Generate a Report Using MonetDB and iReports/Jasper Reports
===========================================================



