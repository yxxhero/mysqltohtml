#!/usr/bin/python
#coding:utf-8
from __future__ import unicode_literals
import re
import os
import six
import uuid
import json
import time
import logging
import tempfile
import sys
import MySQLdb
from datetime import datetime
from io import open

from jinja2 import Environment, FileSystemLoader, select_autoescape
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./debug.log',
                filemode='a')


package_path = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(package_path, "templates")

try:
    conn=MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='root',
            passwd='chinatt_1347',
            db ='darkinfo',
            )
    conn.ping(True)
    conn.autocommit(True)
except Exception,e:
    logging.error(str(e))
    sys.exit(1)
else:
    logging.info("数据库连接成功")
    cur = conn.cursor()

class DateTimeEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self,o)


# Initialize Jinja 2 env
env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml", "j2"])
)
template = env.get_template("template.j2")

# Regex to match src property in script tags
js_src_pattern = re.compile(r'<script.*?src=\"(.*?)\".*?<\/script>',
                            re.IGNORECASE | re.MULTILINE)
# Path to JS files inside templates
js_files_path = os.path.join(package_path, templates_dir)


def convert(db_name,table_name, **kwargs):
    header_sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s' and table_schema = '%s';" %(table_name,db_name)
    cur.execute(header_sql)
    header_result=cur.fetchall()
    csv_headers =[heads[0] for heads in header_result if heads] 
    
    rows_sql="select * from %s" %(table_name)
    cur.execute(rows_sql)
    rows_result=cur.fetchall()
    csv_rows = [row for row in rows_result if row]

    html = render_template(csv_headers, csv_rows, **kwargs)

    # Freeze all JS files in template
    return freeze_js(html)


def render_template(table_headers, table_items, **options):
    """
    Render Jinja2 template
    """
    caption = options.get("caption") or "Table"
    display_length = options.get("display_length") or -1
    height = options.get("height") or "70vh"
    default_length_menu = [-1, 10, 25, 50]
    pagination = options.get("pagination") or True
    virtual_scroll_limit = options.get("virtual_scroll") or 1000

    # Change % to vh
    height = height.replace("%", "vh")

    # Header columns
    columns = []
    for header in table_headers:
        columns.append({"title": header})

    # Data table options
    datatable_options = {
        "columns": columns,
        "data": table_items,
        "iDisplayLength": display_length,
        "sScrollX": "100%",
        "sScrollXInner": "100%"
    }

    # Enable virtual scroll for rows bigger than 1000 rows
    is_paging = pagination
    virtual_scroll = False
    scroll_y = height

    if virtual_scroll_limit != -1 and len(table_items) > virtual_scroll_limit:
        virtual_scroll = True
        display_length = -1

        fmt = ("\nVirtual scroll is enabled since number of rows exceeds {limit}."
               " You can set custom row limit by setting flag -vs, --virtual-scroll."
               " Virtual scroll can be disabled by setting the value to -1 and set it to 0 to always enable.")
        logger.warn(fmt.format(limit=virtual_scroll_limit))

        if not is_paging:
            fmt = "\nPagination can not be disabled in virtual scroll mode."
            logger.warn(fmt)

        is_paging = True

    if is_paging and not virtual_scroll:
        # Add display length to the default display length menu
        length_menu = []
        if display_length != -1:
            length_menu = sorted(default_length_menu + [display_length])
        else:
            length_menu = default_length_menu

        # Set label as "All" it display length is -1
        length_menu_label = [str("All") if i == -1 else i for i in length_menu]
        datatable_options["lengthMenu"] = [length_menu, length_menu_label]
        datatable_options["iDisplayLength"] = display_length

    if is_paging:
        datatable_options["paging"] = True
    else:
        datatable_options["paging"] = False

    if scroll_y:
        datatable_options["scrollY"] = scroll_y

    if virtual_scroll:
        datatable_options["scroller"] = True
        datatable_options["bPaginate"] = False
        datatable_options["deferRender"] = True
        datatable_options["bLengthChange"] = False

    enable_export = True 
    options["export_options"]=["copy", "csv", "json", "print"]
    if enable_export:
        if options["export_options"]:
            allowed = list(options["export_options"])
        else:
            allowed = ["copy", "csv", "json", "print"]

        datatable_options["dom"] = "Bfrtip"
        datatable_options["buttons"] = allowed

    datatable_options_json = json.dumps(datatable_options,
                                        separators=(",", ":"),cls=DateTimeEncoder)

    return template.render(title=caption or "Table",
                           caption=caption,
                           datatable_options=datatable_options_json,
                           virtual_scroll=virtual_scroll,
                           enable_export=enable_export)


def freeze_js(html):
    """
    Freeze all JS assets to the rendered html itself.
    """
    matches = js_src_pattern.finditer(html)

    if not matches:
        return html

    # Reverse regex matches to replace match string with respective JS content
    for match in reversed(tuple(matches)):
        # JS file name
        file_name = match.group(1)
        file_path = os.path.join(js_files_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        # Replace matched string with inline JS
        fmt = '<script type="text/javascript">{}</script>'
        js_content = fmt.format(file_content)
        html = html[:match.start()] + js_content + html[match.end():]

    return html

with open("test.html","a") as fe:
    fe.write(convert("darkinfo","dark_status"))
