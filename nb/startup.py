from pathlib import Path
import site

BASEDIR = Path.home() / 'Development/hw-4.2.0'
site.addsitedir(str(BASEDIR / BASEDIR.stem.split('-')[0]))

from imports import *

import IPython
from IPython.display import HTML, Image, Markdown, SVG

HILITE_ME = "http://hilite.me/api"

cd(BASEDIR)
print(f'Current working directory: {cwd()}')

def hilite_src_lines(obj):
    codeStr = inspect.getsource(obj)
    hilite_params = { "code": codeStr }
    return requests.post(HILITE_ME, hilite_params).text

def get_desc(s):
    """ Return the first line of the docstring of the object named by `s`.
    """
    print(s)
    print()
    print(f"{vars().keys()=}")
    return inspect.getdoc(vars()[s]).split('\n')[0]

def describe(p: Path) -> str:
    """ Return a HTML table of function names and their descriptions.

        Get the description of each function from the first line of its docstring.
    """
    rowData = list()
    desc = ''
    for s in get_all(Path("startup.py")):
        if not s[0].isupper():
            desc = inspect.getdoc(globals()[s])
            if desc:
                desc = desc.split('\n')[0] if desc else ''
            rowData.append((s, desc))
    doc = Document()
    table = doc.createElement("table")
#     doc.appendChild(table)
    for d in rowData:
        row = doc.createElement("tr")
        cell = doc.createElement("td")
        tag = doc.createElement("code")
        link = doc.createElement("a")
        text = doc.createTextNode(d[0])
        p2 = Path("d[0]")
        tag.appendChild(text)
        cell.appendChild(tag)
        row.appendChild(cell)
        cell = doc.createElement("td")
        tag = doc.createElement("p")
        text = doc.createTextNode(d[1] if d[1] else '')
        tag.appendChild(text)
        cell.appendChild(tag)
        row.appendChild(cell)
        table.appendChild(row)
    return table.toxml()

def hilite_definition(obj):
    if not type(obj) is str: obj = obj.__name__
    src = grep(obj + " = ", files='*.py', quiet=True)
    for k, v in src.items():
        if k.name in FILES:
            line = v[1]
            hilite_params = {'code': line}
            LOCATION = f"<p><code>{obj}</code> is defined in <code>{k.name}</code>.</p>\n"
            return LOCATION + requests.post(HILITE_ME, hilite_params).text
    return None

def get_class_names(p:Path)->list:
    return [s for s in get_all(p) if s[0].isupper() and not s[1].isupper()]

def highlight(obj):
    display(HTML(hilite_definition(obj) if type(obj) is str else hilite_src_lines(obj)))
