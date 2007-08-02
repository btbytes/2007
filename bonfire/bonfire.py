#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bonfire website builder
======================

Generate HTML documents out of .rst files 
and Mako templates.

Derived from Georg Brandl's Pocoo projects www site builder - sphinx.py

:copyright: 2006 by Georg Brandl, 2007 Pradeep Gowda
:license: GNU GPL.
"""

import sys, os
import os.path as path
import time
import getopt
import shutil
import string
from email.Utils import formatdate

from docutils import nodes
from docutils.core import publish_parts
from docutils.writers import html4css1
from docutils.parsers import rst
from docutils.parsers.rst import directives

from mako.template import Template
from mako.runtime import Context
from mako.lookup import TemplateLookup
from StringIO import StringIO

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

pygments_formatter = HtmlFormatter()

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = get_lexer_by_name('text')
    parsed = highlight(u'\n'.join(content), lexer, pygments_formatter)
    return [nodes.raw('', parsed, format='html')]

pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
directives.register_directive('sourcecode', pygments_directive)


__version__ = '2'

slur_chars = string.letters + string.digits + "_-"


def mkdir(dir):
    try:
        os.makedirs(dir)
    except:
        if not path.isdir(dir):
            raise

def rmtree(dir):
    try:
        shutil.rmtree(dir)
    except:
        if path.isdir(dir):
            raise


def slurify(text):
    return ''.join(let.lower() for let in text.replace(' ', '-') if let in slur_chars)


def ingroups(iterable, count):
    l = []
    for item in iterable:
        l.append(item)
        if len(l) == count+1:
            yield l[:count], True
            l = l[count:]
    yield l, False


def writefile(text, *fnparts):
    filename = path.join(*fnparts[:-1])
    mkdir(filename)
    filename = path.join(filename, fnparts[-1])
    fp = open(filename, 'w')
    fp.write(text)
    fp.close()


class PageTranslator(html4css1.HTMLTranslator):
    commentfields = {'template': ('template', 'default'),
                     'navbar-order': ('navbar_order', ''),
                     'title': ('pagetitle', '')}

    def visit_comment(self, node):
        text = node.astext()
        if ':' in text:
            name, val = text.split(':', 1)
            if name in self.commentfields:
                setattr(self, self.commentfields[name][0], val.strip())
        raise nodes.SkipNode

    def visit_reference(self, node):
        uri = node.get('refuri', 'http://')
        if not (uri.startswith('http://') or uri.startswith('mailto:')):
            # stupid but it works.
            node['refuri'] = '##base##/' + node['refuri']
        return html4css1.HTMLTranslator.visit_reference(self, node)


class BlogPageTranslator(PageTranslator):
    commentfields = {'posted': ('posted', ''),
                     'author': ('author', 'Anonymous')}


class PageWriter(html4css1.Writer):
    def __init__(self, translator):
        html4css1.Writer.__init__(self)
        self.translator_class = translator

    def assemble_parts(self):
        html4css1.Writer.assemble_parts(self)
        for field, default in self.translator_class.commentfields.values():
            self.parts[field] = getattr(self.visitor, field, default)


class SiteBuilder(object):
    def __init__(self, rootdir, outdir):
        self.rootdir = rootdir
        self.outdir = outdir
        mkdir(self.outdir)
        self.tmpl = path.join(os.path.realpath(self.rootdir), 'templates')
        print "TEMPLATE PATH", self.tmpl
        self.lookup = TemplateLookup(directories=[self.tmpl])
        self.buf = StringIO()
        self.sources = {}
        srcdir = rootdir
        for fn in os.listdir(srcdir):
            if not fn.endswith('.rst'):
                continue
            basename = path.splitext(fn)[0]
            self.sources[basename] = path.join(srcdir, fn)

    def start(self):
        writer = PageWriter(PageTranslator)

        contexts = []
        navitems = []

        # two passes:
        # first, render all ReST content to HTML, gathering navitems
        for docname, sourcefile in self.sources.iteritems():
            parts = publish_parts(
                file(sourcefile).read(),
                source_path=sourcefile,
                writer=writer,
                settings_overrides={'initial_header_level': 2}
            )
            if not parts['pagetitle']:
                parts['pagetitle'] = parts['title']
            base = (docname == 'index' and '.' or '..')
            contexts.append({
                'docname': docname,
                'template': parts['template'],
                'title': parts['title'],
                'pagetitle': parts['pagetitle'],
                'content': parts['body'].replace('##base##', base),
                'base': base,
                'navitems': navitems,
                'sphinxver': __version__,
            })
            if parts['navbar_order'] != '0' and parts['navbar_order'].strip():
                navitems.append({
                    'docname': docname,
                    'name': parts['pagetitle'],
                    'link': (docname != 'index' and docname or ''),
                    'navbar_order': parts['navbar_order'],
                })

        # second, render all HTML in the Mako templates
        for ctx in contexts:
            context = Context(self.buf, **ctx)
            tmpl = os.path.join(self.tmpl, ctx['template']+'.html')
            tmpl = Template(filename=tmpl).render_context(context)
            text = self.buf.getvalue()
            docname = ctx['docname'] or 'default'
            writefile(text, self.outdir, docname+'.html')


def main(argv):
    usage = "Usage: %s [-o outputdir] [srcdir]" % argv[0]

    try:
        gopts, args = getopt.getopt(argv[1:], "o:")
    except getopt.GetoptError:
        print usage
        return 2
    opts = dict(gopts)

    if len(args) == 0:
        dir = '.'
    elif len(args) == 1:
        dir = args[0]
    else:
        print usage
        return 2

    builder = SiteBuilder(dir, opts.get('-o', path.join(dir, 'build')))
    builder.start()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
