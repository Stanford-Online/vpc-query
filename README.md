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

1. You need an ssh key on the gateway to access anything in the VPC.
   Generate an ssh key (or use an exsisting one) and send us the
   **public half** of your key -- we definintely don't want to see the
   public half.

2. (optional) set up a virtual environment, or switch to an existing one

3. Install requirements: ``pip install -r requirements.txt``


Operation
---------

1. Make sure your ssh key is in an ssh agent. From your shell, use this
   command to see: ``ssh-add -l``.  Make sure this includes the private
   lalf of the ssh key that you had Ops put on the gateway

2. Run the script, capturing the output: ``python query.py -v > output.txt``



Example Output
-------------------

Stderr:

     ./query.py -v
    database password: 
    INFO: testing SSH with command: ssh -o "BatchMode yes" sef@jump-prod "exit 0"
    INFO: starting ssh tunnel: ssh -o BatchMode yes -N -L 15606:edx-prod-ro.cn2cujs3bplc.us-west-1.rds.amazonaws.com:3306 sef@jump-prod
    INFO: query = 
    select au.email, sm.created, sm.grade, sm.max_grade
    from auth_user au, courseware_studentmodule sm
    where sm.student_id = au.id
    and course_id = 'Carnegie/2013/Fores

    INFO: stopping ssh tunneljjjjk
    INFO: Success! rows = 260

An example of what gets written to stdout can be seen [here](example_output.html). Email addresses have been redacted.


