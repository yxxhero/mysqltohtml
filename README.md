# mysqltohtml
Web page display mysql data, and support for sorting, searching
用法简介：
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
  快速启动：
  python myqsltohtml.py --password password --database passwd --tablename tablename
  打开浏览器访问8080端口即可
