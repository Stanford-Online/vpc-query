#!/usr/bin/env python

import sys
import os
import optparse
import subprocess
import MySQLdb
import getpass
import time
from contextlib import contextmanager
from multiprocessing import Process

DEFAULT_LOCAL_PORT = 15606
DEFAULT_GATEWAY_HOST = "jump-prod"
DEFAULT_DB_USER = "readonly"
DEFAULT_DB_HOST = "edx-prod-ro.cn2cujs3bplc.us-west-1.rds.amazonaws.com"
DEFAULT_DB_PORT = 3306
DEFAULT_DATABASE = "edxprod"

SQL_QUERY = """
select au.email, sm.created, sm.grade, sm.max_grade
from auth_user au, courseware_studentmodule sm
where sm.student_id = au.id
and course_id = 'Carnegie/2013/Forest_Monitoring_with_CLASlite'
and sm.module_type = 'problem'
"""


def main():
    parse_command_line()
    ssh_test()
    with ssh_tunnel():
        result = query()
    if result == None:
        sys.exit(1)
    log_info("Success! rows = %d" % len(result))
    for row in result:
        rowstr = (str(col) for col in row)
        print ",".join(rowstr)


def ssh_test():
    test_cmd = 'ssh -o "BatchMode yes" %s@%s "exit 0"' \
               % (options.gateway_user, options.gateway_host)
    log_info("testing SSH with command: %s" % test_cmd)
    try:
        rc = subprocess.call(test_cmd, shell=True)
    except OSError as e:
        sys.exit("ERROR: cannot open test ssh tunnel: %s" % str(e))
    if rc != 0:
        sys.exit("ERROR: test ssh tunnel unexpected result: %d" % rc)


@contextmanager
def ssh_tunnel():
    """
    Responsible for setup and teardown of the SSH tunnel we rely on
    to make the database request.  Context manager ensures teardown
    happens when inner scope terminates.
    """

    tunnel_cmd = ['ssh', '-o', 'BatchMode yes', '-N', '-L',
        str(options.local_port) + ":" + options.db_host + ":" +  str(options.db_port),
        options.gateway_user + "@" + options.gateway_host]

    # Setup
    log_info("starting ssh tunnel: %s" % ' '.join(tunnel_cmd))
    tunnel_proc = subprocess.Popen(tunnel_cmd)
    time.sleep(3)  # hack: tunnel needs a few seconds to work
    yield

    # Teardown 
    log_info("stopping ssh tunnel")
    tunnel_proc.kill()


def query():
    """
    Use the established ssh tunnel to query the remote mysql database.
    Assumes that the tunnel is accessible through a localhost port.

    Returns None if there is a problem, or a list of the results of the
    query. An empty list is a valid result.
    """
    log_info("query = %s" % SQL_QUERY)
    result = None
    conn = None
    try:
        conn = MySQLdb.connect(host='127.0.0.1', 
                port=options.local_port,
                user=options.db_user, 
                passwd=options.db_password, 
                db=options.db_name);
        cur = conn.cursor()
        cur.execute(SQL_QUERY)
        result = cur.fetchall()
    except MySQLdb.Error as e:
        sys.stderr.write("Database error %d: %s\n" % (e.args[0],e.args[1]))
    if conn:
        conn.close()
    return result


def parse_command_line():
    usage = """usage: %prog [options]
    
    Run a query on remote MySQL database, assumed to be readonly, via
    an ssh tunnel.  Runs the ssh tunnel as a subprocess so that it can
    take advantage of an ssh agent if you have one running.
    """
    default_user = os.getlogin()
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-u", "--user", dest="gateway_user", 
        default=default_user,
        help="User name on the gateway. If not specified, " \
             "use current user (\"%s\")" % default_user)
    parser.add_option("-g", "--gateway", dest="gateway_host", 
        default=DEFAULT_GATEWAY_HOST,
        help="Hostname of the ssh gateway. Can either be a FQDN or " \
             "a host configured in your ssh client configuration file " \
             "(usually ~/.ssh/config) (default=\"%s\")" \
             % DEFAULT_GATEWAY_HOST)
    parser.add_option("-l", "--localport", dest="local_port", 
        default=DEFAULT_LOCAL_PORT,
        help="Local port for ssh tunnel (default=%s)" \
             % DEFAULT_LOCAL_PORT)
    parser.add_option("--host", dest="db_host", 
        default=DEFAULT_DB_HOST,
        help="Database host (default=\"%s\"" % DEFAULT_DB_HOST)
    parser.add_option("--dbport", dest="db_port", 
        default=DEFAULT_DB_PORT,
        help="Database port (default=%d)" % DEFAULT_DB_PORT)
    parser.add_option("--dbuser", dest="db_user", 
        default=DEFAULT_DB_USER,
        help="Database user (default=%s)" % DEFAULT_DB_USER)
    parser.add_option("-d", "--db", dest="db_name", 
        default=DEFAULT_DATABASE,
        help="Database name to query on the host (default=\"%s\")" \
             % DEFAULT_DATABASE)
    parser.add_option("-v", dest="verbose", action="store_true",
        help="Print info messages to stderr")

    global options
    (options, args) = parser.parse_args()

    if not hasattr(options, 'db_password'):
        options.db_password = getpass.getpass("database password: ")


def log_info(msg):
    if options.verbose:
        sys.stderr.write("INFO: %s\n" % msg)
    

if __name__ == '__main__':
    main()


