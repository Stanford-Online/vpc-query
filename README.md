vpc-query
===============

Simple script to run a SQL Query against a database that is in an Amazon
Virtual Private Cloud (VPC). Because hosts in a VPC aren't reachable
from the general internet, you have to access them via an SSH
gateway. This script sets up a localhost port forward to get to the
database, and executes the query.  

Output is written to stdout, info messages printed to stderr when
the -v option is used.  Many command line options (use -h to see),
but *password* is not one of them.  Please be careful with our
passwords, even read-only ones.

The script runs ssh in a subprocess for the tunnel. Generally you want
an ssh-agent running with your key loaded.

It is expected that you'll fork this script and use as a starting place
for your own data access script.  To that end look for the "TODO's" in
the code pointing you to things you'll likely have to change.


Setup
-----

1. **SSH Key**. You need an ssh key on the gateway to access anything
   in the VPC. Generate an ssh key (or use an existing one) and
   send us the **public half** of your key -- we definitely don't
   want to see the private half.  Since this is a public key, you
   can send to in a regular email, as an attachment or just copy/paste.
   Send to <openedx-courseops@lists.stanford.edu> and we can install
   to our SSH gateway pretty quickly.

2. **Database Account**.  We have per-user (or per organization) 
   database accounts.  Again the courseops team can create
   an account for you and give you the password, contact
   <openedx-courseops@lists.stanford.edu> to get one.

3. **Virtual Environment**. (optional) set up a virtual environment 
   using ``mkvirtualenv`` or switch to an existing one with ``workon``. 

4. **Requirements**.  Install them with ``pip install -r requirements.txt``


Operation
---------

1. **SSH Agent**. Make sure your ssh key is in an ssh agent. From your shell, use this
   command to see: ``ssh-add -l``.  Make sure this includes the private
   half of the ssh key that you had Ops put on the gateway

2. **Execute**. Run the script, capturing the output.  Generally
   you'll want to run with something like this:

       `python query.py -v --user=carnegie --dbuser=carnegie > output.txt`



Example Output
-------------------

**Stderr**

    ./query.py -v --dbuser=carnegie
    database password: 
    INFO: testing SSH with command: ssh -o "BatchMode yes" sef@jump-prod "exit 0"
    INFO: starting ssh tunnel: ssh -o BatchMode yes -N -L 15606:edx-prod-ro.cn2cujs3bplc.us-west-1.rds.amazonaws.com:3306 sef@jump-prod
    INFO: query = 
    select au.email, sm.created, sm.grade, sm.max_grade
    from auth_user au, courseware_studentmodule sm
    where sm.student_id = au.id
    and course_id = 'Carnegie/2013/Forest_Monitoring_with_CLASlite'
    and sm.module_type = 'problem'

    INFO: stopping ssh tunnel
    INFO: Success! rows = 260

**Stdout**

An example of what gets written is in the `example_output.html`
file checked into this repo (with email addresses redacted).  An
excerpt here:

    redacted@stanford.edu,2013-06-15 00:18:11,0.0,1.0
    redacted@stanford.edu,2013-06-15 00:18:12,None,None
    redacted@stanford.edu,2013-06-15 00:18:12,None,None
    redacted@stanford.edu,2013-06-15 00:18:12,None,None
    redacted@stanford.edu,2013-06-15 00:46:39,1.0,1.0


DEPRECATED
==========

This is no longer supported. It should not be used.
