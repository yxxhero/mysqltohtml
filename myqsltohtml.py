#!/usr/bin/env python
#coding:utf-8
"""
Usage:
  cli.py (-h | --help)
  cli.py [--host HOST] [--port PORT] [--user USER] [--http-port HTTPPORT] --password PASSWORD --database DATABASE --tablename TABLENAME

Process FILE and optionally apply correction to either left-hand side or
right-hand side.

Options:
  -h --help             Show this screen.
  --version             Show version.
  --host HOST           define mysql host [default: 127.0.0.1].
  --port PORT           define mysql port [default: 3306 ].
  --user USER           define mysql user [default: root].
  --http-port HTTPPORT  define http port [default: 8080] 
  --password PASSWORD   define mysql password.
  --database DATABASE   define mysql database.
  --tablename DATABASE  define mysql tablename.
"""

from docopt import docopt

from convert import convert
from flask import Flask
app = Flask(__name__)


@app.route("/")
def mysqltohtml():
    global host
    global port
    global user
    global password
    global database 
    global tablename 
    print host,port,user,password,database,tablename
    return convert(host,port,user,password,database,tablename)


if __name__=="__main__":
    arguments = docopt(__doc__, version='mysqltohtml 0.1.0')
    host=arguments["--host"]
    port=arguments["--port"]
    user=arguments["--user"]
    password=arguments["--password"]
    database=arguments["--database"]
    tablename=arguments["--tablename"]
    httpport=int(arguments["--http-port"])

    app.run(debug=True,host="0.0.0.0",port=httpport)
