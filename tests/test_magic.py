import pytest
import pandas
import sql_magic

from IPython import get_ipython
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite

ip = get_ipython()
ip.register_magics(sql_magic.SQLConn)
sql_magic.load_ipython_extension(ip)

@pytest.fixture
def sqlite_conn():
    return create_engine('sqlite+pysqlite:///test.db', module=sqlite)

def test_query_1(sqlite_conn):
    conn = sqlite_conn
    ip.all_ns_refs[0]['conn'] = conn
    ip.run_line_magic('config', "SQLConn.conn_object_name = 'conn'")
    ip.run_cell_magic('read_sql', 'df', 'SELECT 1')
    df = ip.all_ns_refs[0]['df']
    assert df.iloc[0,0] == 1

def test_query_1_notify(sqlite_conn):
    conn = sqlite_conn
    ip.all_ns_refs[0]['conn'] = conn
    ip.run_line_magic('config', "SQLConn.conn_object_name = 'conn'")
    ip.run_cell_magic('read_sql', 'df -n', 'SELECT 1')
    df = ip.all_ns_refs[0]['df']
    assert df.iloc[0, 0] == 1

def test_read_sql_create_table_error():
    with pytest.raises(sql_magic.NoReturnValueResult):
        conn = sqlite_conn
        ip.all_ns_refs[0]['conn'] = conn
        ip.run_line_magic('config', "SQLConn.conn_object_name = 'conn'")
        ip.run_cell_magic('read_sql', '', 'DROP TABLE IF EXISTS test')

def test_exec_sql():
    ip.run_cell_magic('exec_sql', '', 'DROP TABLE IF EXISTS test;')
    ip.run_cell_magic('exec_sql', '', 'CREATE TABLE test AS SELECT 2;')
    ip.run_cell_magic('read_sql', 'df2', 'SELECT * FROM test')
    df2 = ip.all_ns_refs[0]['df2']
    ip.run_cell_magic('exec_sql', '', 'DROP TABLE IF EXISTS test;')
    assert df2.iloc[0, 0] == 2
