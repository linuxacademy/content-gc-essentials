from os import getenv

import pymysql
from pymysql.err import OperationalError

import datetime


# TODO(developer): specify SQL connection details
CONNECTION_NAME = getenv(
  'INSTANCE_CONNECTION_NAME',
  '[CLOUD_SQL_INSTANCE_CONNECTION_NAME]')
DB_USER = getenv('MYSQL_USER', 'root')
DB_PASSWORD = getenv('MYSQL_PASSWORD', 'root')
DB_NAME = getenv('MYSQL_DATABASE', 'la_met_museum')

mysql_config = {
  'user': DB_USER,
  'password': DB_PASSWORD,
  'db': DB_NAME,
  'charset': 'utf8mb4',
  'cursorclass': pymysql.cursors.DictCursor,
  'autocommit': True
}

# Create SQL connection globally to enable reuse
# PyMySQL does not include support for connection pooling
mysql_conn = None


def __get_cursor():
    """
    Helper function to get a cursor
      PyMySQL does NOT automatically reconnect,
      so we must reconnect explicitly using ping()
    """
    try:
        return mysql_conn.cursor()
    except OperationalError:
        mysql_conn.ping(reconnect=True)
        return mysql_conn.cursor()


def get_sql_data(request):
    global mysql_conn

    request_args = request.args
    now = datetime.datetime.now()
    # print now.year, now.month, now.day, now.hour, now.minute, now.second

    if request_args and 'year' in request_args:
        theYear = request_args['year']
    else:
        theYear = now.year

    # Initialize connections lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not mysql_conn:
        try:
            mysql_conn = pymysql.connect(**mysql_config)
        except OperationalError:
            # If production settings fail, use local development ones
            mysql_config['unix_socket'] = f'/cloudsql/{CONNECTION_NAME}'
            mysql_conn = pymysql.connect(**mysql_config)

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. mysql_conn) for later reuse.
    with __get_cursor() as cursor:
        cursor.execute('SELECT Title, Artist_Display_Name, Object_Begin_Date, Object_End_Date, Link_Resource FROM MetObjects WHERE y% = Object_Begin_Date or y% = Object_End_Date LIMIT 10', (theYear))
        row = cursor.fetchone()
        while row is not None:
          print(row)
          row = cursor.fetchone()