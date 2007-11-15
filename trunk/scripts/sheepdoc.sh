#! /bin/bash
# Sheepdoc is a small script to convert a restructured text file into a PDF document.
# Pradeep Kishore Gowda <pradeep@btbytes.com> 
# 2007.11.15

# The shell script: rst2latex foo.rst > /tmp/foo.tex ; pdflatex /tmp/foo.tex ; evince foo.pdf
# The problem: have to type the intermediate and final output file names
# The solution ...

bname=`basename $1 .rst`
rst2latex $1 > /tmp/$bname.tex 
pdflatex /tmp/$bname.tex
evince $bname.pdf
echo "$1 converted to $bname.pdf"
