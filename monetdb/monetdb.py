# monetdb.py
# Copyright (C) 2005, 2006, 2007 Michael Bayer mike_mp@zzzcomputing.com
# Monetdb module by Pradeep Gowda pradeep.gowda@gmail.comm
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime, string, types, re, random, warnings

from sqlalchemy import util, sql, schema, ansisql, exceptions
from sqlalchemy.engine import base, default
import sqlalchemy.types as sqltypes
from sqlalchemy.databases import information_schema as ischema

try:
    import mx.DateTime.DateTime as mxDateTime
except:
    mxDateTime = None

    
class MonetInet(sqltypes.TypeEngine):
    def get_col_spec(self):
        return "INET"

class MonetNumeric(sqltypes.Numeric):
    def get_col_spec(self):
        if not self.precision:
            return "NUMERIC"
        else:
            return "NUMERIC(%(precision)s, %(length)s)" % {'precision': self.precision, 'length' : self.length}

class MonetFloat(sqltypes.Float):
    def get_col_spec(self):
        if not self.precision:
            return "FLOAT"
        else:
            return "FLOAT(%(precision)s)" % {'precision': self.precision}

class MonetInteger(sqltypes.Integer):
    def get_col_spec(self):
        return "INTEGER"

class MonetSmallInteger(sqltypes.Smallinteger):
    def get_col_spec(self):
        return "SMALLINT"

class MonetBigInteger(MonetInteger):
    def get_col_spec(self):
        return "BIGINT"

class MonetDateTime(sqltypes.DateTime):
    def get_col_spec(self):
        return "TIMESTAMP " + (self.timezone and "WITH" or "WITHOUT") + " TIME ZONE"

class MonetDate(sqltypes.Date):
    def get_col_spec(self):
        return "DATE"

class MonetTime(sqltypes.Time):
    def get_col_spec(self):
        return "TIME " + (self.timezone and "WITH" or "WITHOUT") + " TIME ZONE"

class MonetInterval(sqltypes.TypeEngine):
    def get_col_spec(self):
        return "INTERVAL"

class MonetText(sqltypes.TEXT):
    def get_col_spec(self):
        return "TEXT"

class MonetString(sqltypes.String):
    def get_col_spec(self):
        return "VARCHAR(%(length)s)" % {'length' : self.length}

class MonetChar(sqltypes.CHAR):
    def get_col_spec(self):
        return "CHAR(%(length)s)" % {'length' : self.length}

class MonetBinary(sqltypes.Binary):
    def get_col_spec(self):
        return "BYTEA"

class MonetBoolean(sqltypes.Boolean):
    def get_col_spec(self):
        return "BOOLEAN"

monet_colspecs = {
    sqltypes.Integer : MonetInteger,
    sqltypes.Smallinteger : MonetSmallInteger,
    sqltypes.Numeric : MonetNumeric,
    sqltypes.Float : MonetFloat,
    sqltypes.DateTime : MonetDateTime,
    sqltypes.Date : MonetDate,
    sqltypes.Time : MonetTime,
    sqltypes.String : MonetString,
    sqltypes.Binary : MonetBinary,
    sqltypes.Boolean : MonetBoolean,
    sqltypes.TEXT : MonetText,
    sqltypes.CHAR: MonetChar,
}

monet_ischema_names = {
    'integer' : MonetInteger,
    'bigint' : MonetBigInteger,
    'smallint' : MonetSmallInteger,
    'character varying' : MonetString,
    'character' : MonetChar,
    'text' : MonetText,
    'numeric' : MonetNumeric,
    'float' : MonetFloat,
    'real' : MonetFloat,
    'inet': MonetInet,
    'double precision' : MonetFloat,
    'timestamp' : MonetDateTime,
    'timestamp with time zone' : MonetDateTime,
    'timestamp without time zone' : MonetDateTime,
    'time with time zone' : MonetTime,
    'time without time zone' : MonetTime,
    'date' : MonetDate,
    'time': MonetTime,
    'bytea' : MonetBinary,
    'boolean' : MonetBoolean,
    'interval':MonetInterval,
}

def descriptor():
    return {'name':'monetdb',
    'description':'MonetDB',
    'arguments':[
        ('username',"Database Username",None),
        ('password',"Database Password",None),
        ('database',"Database Name",None),
        ('host',"Hostname", None),
    ]}

class MonetExecutionContext(default.DefaultExecutionContext):

    def is_select(self):
        return re.match(r'SELECT', self.statement.lstrip(), re.I) and not re.search(r'FOR UPDATE\s*$', self.statement, re.I)
    
    def create_cursor(self):
        if self.dialect.server_side_cursors and self.is_select():
            # use server-side cursors:
            # http://lists.initd.org/pipermail/psycopg/2007-January/005251.html
            ident = "c" + hex(random.randint(0, 65535))[2:]
            return self.connection.connection.cursor(ident)
        else:
            return self.connection.connection.cursor()

    def get_result_proxy(self):
        if self.dialect.server_side_cursors and self.is_select():
            return base.BufferedRowResultProxy(self)
        else:
            return base.ResultProxy(self)
    
    def post_exec(self):
        if self.compiled.isinsert and self.last_inserted_ids is None:
            if not self.dialect.use_oids:
                pass
                # will raise invalid error when they go to get them
            else:
                table = self.compiled.statement.table
                if self.cursor.lastrowid is not None and table is not None and len(table.primary_key):
                    s = sql.select(table.primary_key, table.oid_column == self.cursor.lastrowid)
                    row = self.connection.execute(s).fetchone()
                self._last_inserted_ids = [v for v in row]
        super(MonetExecutionContext, self).post_exec()
        
class MonetDialect(ansisql.ANSIDialect):
    def __init__(self, use_oids=False, use_information_schema=False, server_side_cursors=False, **kwargs):
        ansisql.ANSIDialect.__init__(self, default_paramstyle='pyformat', **kwargs)
        self.use_oids = use_oids
        self.server_side_cursors = server_side_cursors
        if self.dbapi is None or not hasattr(self.dbapi, '__version__') or self.dbapi.__version__.startswith('2'):
            self.version = 2
        else:
            self.version = 1
        self.use_information_schema = use_information_schema
        self.paramstyle = 'pyformat'
        
    def dbapi(cls):
        try:
            import MonetSQLdb as monetdb
        except ImportError, e:            
                raise e
        return monetdb
    dbapi = classmethod(dbapi)
    
    def create_connect_args(self, url):
        opts = url.translate_connect_args(['host', 'database', 'user', 'password', 'port'])
        if opts.has_key('port'):
            if self.version == 2:
                opts['port'] = int(opts['port'])
            else:
                opts['port'] = str(opts['port'])
        opts.update(url.query)
        return ([], opts)


    def create_execution_context(self, *args, **kwargs):
        return MonetExecutionContext(self, *args, **kwargs)

    def max_identifier_length(self):
        return 63
        
    def type_descriptor(self, typeobj):        
        return sqltypes.adapt_type(typeobj, monet_colspecs)
        

    def compiler(self, statement, bindparams, **kwargs):
        return MonetCompiler(self, statement, bindparams, **kwargs)

    def schemagenerator(self, *args, **kwargs):
        return MonetSchemaGenerator(self, *args, **kwargs)

    def schemadropper(self, *args, **kwargs):
        return MonetSchemaDropper(self, *args, **kwargs)

    def defaultrunner(self, connection, **kwargs):
        return MonetDefaultRunner(connection, **kwargs)

    def preparer(self):
        return MonetIdentifierPreparer(self)

    def get_default_schema_name(self, connection):
        if not hasattr(self, '_default_schema_name'):
            self._default_schema_name = connection.scalar("select current_schema()", None)
        return self._default_schema_name

    def last_inserted_ids(self):
        if self.context.last_inserted_ids is None:
            raise exceptions.InvalidRequestError("no INSERT executed, or can't use cursor.lastrowid without Postgres OIDs enabled")
        else:
            return self.context.last_inserted_ids

    def oid_column_name(self, column):
        if self.use_oids:
            return "oid"
        else:
            return None

    def do_executemany(self, c, statement, parameters, context=None):
        """We need accurate rowcounts for updates, inserts and deletes."""
        rowcount = 0
        for param in parameters:
            c.execute(statement, param)
            rowcount += c.rowcount
        if context is not None:
            context._rowcount = rowcount

    def has_table(self, connection, table_name, schema=None):
        # seems like case gets folded in pg_class...
        if schema is None:
            cursor = connection.execute("""select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=current_schema() and lower(relname)=%(name)s""", {'name':table_name.lower().encode(self.encoding)});
        else:
            cursor = connection.execute("""select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=%(schema)s and lower(relname)=%(name)s""", {'name':table_name.lower().encode(self.encoding), 'schema':schema});
        return bool( not not cursor.rowcount )

    def has_sequence(self, connection, sequence_name):
        cursor = connection.execute('''SELECT relname FROM pg_class WHERE relkind = 'S' AND relnamespace IN ( SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%%' AND nspname != 'information_schema' AND relname = %(seqname)s);''', {'seqname': sequence_name})
        return bool(not not cursor.rowcount)

    def is_disconnect(self, e):
        if isinstance(e, self.dbapi.OperationalError):
            return 'closed the connection' in str(e) or 'connection not open' in str(e)
        elif isinstance(e, self.dbapi.InterfaceError):
            return 'connection already closed' in str(e)
        elif isinstance(e, self.dbapi.ProgrammingError):
            # yes, it really says "losed", not "closed"
            return "losed the connection unexpectedly" in str(e)
        else:
            return False

    def reflecttable(self, connection, table):        
        ischema_names = monet_ischema_names
        if self.use_information_schema:
            ischema.reflecttable(connection, table, ischema_names)
        else:
            preparer = self.identifier_preparer
            if table.schema is not None:
                schema_where_clause = "n.nspname = :schema"
            else:
                schema_where_clause = "pg_catalog.pg_table_is_visible(c.oid)"

            ## information schema in pg suffers from too many permissions' restrictions
            ## let us find out at the pg way what is needed...

            SQL_COLS = """
                SELECT a.attname,
                  pg_catalog.format_type(a.atttypid, a.atttypmod),
                  (SELECT substring(d.adsrc for 128) FROM pg_catalog.pg_attrdef d
                   WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef)
                  AS DEFAULT,
                  a.attnotnull, a.attnum, a.attrelid as table_oid
                FROM pg_catalog.pg_attribute a
                WHERE a.attrelid = (
                    SELECT c.oid
                    FROM pg_catalog.pg_class c
                         LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                         WHERE (%s)
                         AND c.relname = :table_name AND c.relkind in ('r','v')
                ) AND a.attnum > 0 AND NOT a.attisdropped
                ORDER BY a.attnum
            """ % schema_where_clause

            s = sql.text(SQL_COLS, bindparams=[sql.bindparam('table_name', type=sqltypes.Unicode), sql.bindparam('schema', type=sqltypes.Unicode)], typemap={'attname':sqltypes.Unicode})
            c = connection.execute(s, table_name=table.name,
                                      schema=table.schema)
            rows = c.fetchall()

            if not rows:
                raise exceptions.NoSuchTableError(table.name)

            domains = self._load_domains(connection)
            
            for name, format_type, default, notnull, attnum, table_oid in rows:
                ## strip (30) from character varying(30)
                attype = re.search('([^\(]+)', format_type).group(1)
                nullable = not notnull

                try:
                    charlen = re.search('\(([\d,]+)\)', format_type).group(1)
                except:
                    charlen = False

                numericprec = False
                numericscale = False
                if attype == 'numeric':
                    if charlen is False:
                        numericprec, numericscale = (None, None)
                    else:
                        numericprec, numericscale = charlen.split(',')
                    charlen = False
                if attype == 'double precision':
                    numericprec, numericscale = (53, False)
                    charlen = False
                if attype == 'integer':
                    numericprec, numericscale = (32, 0)
                    charlen = False

                args = []
                for a in (charlen, numericprec, numericscale):
                    if a is None:
                        args.append(None)
                    elif a is not False:
                        args.append(int(a))

                kwargs = {}
                if attype == 'timestamp with time zone':
                    kwargs['timezone'] = True
                elif attype == 'timestamp without time zone':
                    kwargs['timezone'] = False

                if attype in ischema_names:
                    coltype = ischema_names[attype]
                else:
                    if attype in domains:
                        domain = domains[attype]
                        if domain['attype'] in ischema_names:
                            # A table can't override whether the domain is nullable.
                            nullable = domain['nullable']

                            if domain['default'] and not default:
                                # It can, however, override the default value, but can't set it to null.
                                default = domain['default']
                            coltype = ischema_names[domain['attype']]
                    else:
                        coltype=None

                if coltype:
                    coltype = coltype(*args, **kwargs)
                else:
                    warnings.warn(RuntimeWarning("Did not recognize type '%s' of column '%s'" % (attype, name)))
                    coltype = sqltypes.NULLTYPE

                colargs= []
                if default is not None:
                    match = re.search(r"""(nextval\(')([^']+)('.*$)""", default)
                    if match is not None:
                        # the default is related to a Sequence
                        sch = table.schema
                        if '.' not in match.group(2) and sch is not None:
                            default = match.group(1) + sch + '.' + match.group(2) + match.group(3)
                    colargs.append(schema.PassiveDefault(sql.text(default)))
                table.append_column(schema.Column(name, coltype, nullable=nullable, *colargs))


            # Primary keys
            PK_SQL = """
              SELECT attname FROM pg_attribute
              WHERE attrelid = (
                 SELECT indexrelid FROM pg_index i
                 WHERE i.indrelid = :table
                 AND i.indisprimary = 't')
              ORDER BY attnum
            """
            t = sql.text(PK_SQL, typemap={'attname':sqltypes.Unicode})
            c = connection.execute(t, table=table_oid)
            for row in c.fetchall():
                pk = row[0]
                table.primary_key.add(table.c[pk])

            # Foreign keys
            FK_SQL = """
              SELECT conname, pg_catalog.pg_get_constraintdef(oid, true) as condef
              FROM  pg_catalog.pg_constraint r
              WHERE r.conrelid = :table AND r.contype = 'f'
              ORDER BY 1
            """

            t = sql.text(FK_SQL, typemap={'conname':sqltypes.Unicode, 'condef':sqltypes.Unicode})
            c = connection.execute(t, table=table_oid)
            for conname, condef in c.fetchall():
                m = re.search('FOREIGN KEY \((.*?)\) REFERENCES (?:(.*?)\.)?(.*?)\((.*?)\)', condef).groups()
                (constrained_columns, referred_schema, referred_table, referred_columns) = m
                constrained_columns = [preparer._unquote_identifier(x) for x in re.split(r'\s*,\s*', constrained_columns)]
                if referred_schema:
                    referred_schema = preparer._unquote_identifier(referred_schema)
                referred_table = preparer._unquote_identifier(referred_table)
                referred_columns = [preparer._unquote_identifier(x) for x in re.split(r'\s*,\s', referred_columns)]

                refspec = []
                if referred_schema is not None:
                    schema.Table(referred_table, table.metadata, autoload=True, schema=referred_schema,
                                autoload_with=connection)
                    for column in referred_columns:
                        refspec.append(".".join([referred_schema, referred_table, column]))
                else:
                    schema.Table(referred_table, table.metadata, autoload=True, autoload_with=connection)
                    for column in referred_columns:
                        refspec.append(".".join([referred_table, column]))

                table.append_constraint(schema.ForeignKeyConstraint(constrained_columns, refspec, conname))
                
    def _load_domains(self, connection):
            
        ## Load data types for domains:
        SQL_DOMAINS = """
            SELECT t.typname as "name",
                   pg_catalog.format_type(t.typbasetype, t.typtypmod) as "attype",
                   not t.typnotnull as "nullable",
                   t.typdefault as "default",
                   pg_catalog.pg_type_is_visible(t.oid) as "visible",
                   n.nspname as "schema"
            FROM pg_catalog.pg_type t
                 LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                 LEFT JOIN pg_catalog.pg_constraint r ON t.oid = r.contypid
            WHERE t.typtype = 'd'
        """

        s = sql.text(SQL_DOMAINS, typemap={'attname':sqltypes.Unicode})
        c = connection.execute(s)

        domains = {}
        for domain in c.fetchall():
            ## strip (30) from character varying(30)
            attype = re.search('([^\(]+)', domain['attype']).group(1)
            if domain['visible']:
                # 'visible' just means whether or not the domain is in a 
                # schema that's on the search path -- or not overriden by
                # a schema with higher presedence. If it's not visible,
                # it will be prefixed with the schema-name when it's used.
                name = domain['name']
            else:
                name = "%s.%s" % (domain['schema'], domain['name'])

            domains[name] = {'attype':attype, 'nullable': domain['nullable'], 'default': domain['default']}

        return domains
        
        
        
        
class MonetCompiler(ansisql.ANSICompiler):
    def visit_insert_column(self, column, parameters):
        # all column primary key inserts must be explicitly present
        if column.primary_key:
            parameters[column.key] = None

    def visit_insert_sequence(self, column, sequence, parameters):
        """this is the 'sequence' equivalent to ANSICompiler's 'visit_insert_column_default' which ensures
        that the column is present in the generated column list"""
        parameters.setdefault(column.key, None)

    def limit_clause(self, select):
        text = ""
        if select.limit is not None:
            text +=  " \n LIMIT " + str(select.limit)
        if select.offset is not None:
            if select.limit is None:
                text += " \n LIMIT ALL"
            text += " OFFSET " + str(select.offset)
        return text

    def visit_select_precolumns(self, select):
        if select.distinct:
            if type(select.distinct) == bool:
                return "DISTINCT "
            if type(select.distinct) == list:
                dist_set = "DISTINCT ON ("
                for col in select.distinct:
                    dist_set += self.strings[col] + ", "
                    dist_set = dist_set[:-2] + ") "
                return dist_set
            return "DISTINCT ON (" + str(select.distinct) + ") "
        else:
            return ""

    def binary_operator_string(self, binary):
        if isinstance(binary.type, sqltypes.String) and binary.operator == '+':
            return '||'
        elif binary.operator == '%':
            return '%%'
        else:
            return ansisql.ANSICompiler.binary_operator_string(self, binary)

class MonetSchemaGenerator(ansisql.ANSISchemaGenerator):
    def get_column_specification(self, column, **kwargs):
        colspec = self.preparer.format_column(column)
        if column.primary_key and len(column.foreign_keys)==0 and column.autoincrement and isinstance(column.type, sqltypes.Integer) and not isinstance(column.type, sqltypes.SmallInteger) and (column.default is None or (isinstance(column.default, schema.Sequence) and column.default.optional)):
            if isinstance(column.type, MonetBigInteger):
                colspec += " BIGSERIAL"
            else:
                colspec += " SERIAL"
        else:
            colspec += " " + column.type.dialect_impl(self.dialect).get_col_spec()
            default = self.get_column_default_string(column)
            if default is not None:
                colspec += " DEFAULT " + default

        if not column.nullable:
            colspec += " NOT NULL"
        return colspec

    def visit_sequence(self, sequence):
        if not sequence.optional and (not self.dialect.has_sequence(self.connection, sequence.name)):
            self.append("CREATE SEQUENCE %s" % self.preparer.format_sequence(sequence))
            self.execute()

class MonetSchemaDropper(ansisql.ANSISchemaDropper):
    def visit_sequence(self, sequence):
        if not sequence.optional and (self.dialect.has_sequence(self.connection, sequence.name)):
            self.append("DROP SEQUENCE %s" % sequence.name)
            self.execute()

class MonetDefaultRunner(ansisql.ANSIDefaultRunner):
    def get_column_default(self, column, isinsert=True):
        if column.primary_key:
            # passive defaults on primary keys have to be overridden
            if isinstance(column.default, schema.PassiveDefault):
                return self.connection.execute_text("select %s" % column.default.arg).scalar()
            elif (isinstance(column.type, sqltypes.Integer) and column.autoincrement) and (column.default is None or (isinstance(column.default, schema.Sequence) and column.default.optional)):
                sch = column.table.schema
                # TODO: this has to build into the Sequence object so we can get the quoting
                # logic from it
                if sch is not None:
                    exc = "select nextval('\"%s\".\"%s_%s_seq\"')" % (sch, column.table.name, column.name)
                else:
                    exc = "select nextval('\"%s_%s_seq\"')" % (column.table.name, column.name)
                return self.connection.execute_text(exc).scalar()

        return super(ansisql.ANSIDefaultRunner, self).get_column_default(column)

    def visit_sequence(self, seq):
        if not seq.optional:
            return self.connection.execute("select nextval('%s')" % self.dialect.identifier_preparer.format_sequence(seq)).scalar()
        else:
            return None

class MonetIdentifierPreparer(ansisql.ANSIIdentifierPreparer):
    def _fold_identifier_case(self, value):
        return value.lower()

    def _unquote_identifier(self, value):
        if value[0] == self.initial_quote:
            value = value[1:-1].replace('""','"')
        return value

dialect = MonetDialect
