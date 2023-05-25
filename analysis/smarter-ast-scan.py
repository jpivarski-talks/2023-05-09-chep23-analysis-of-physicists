import ast
import glob
import json
import tarfile
from collections import Counter

import jedi
import jupytext


STDLIB_MODULES = {
    "__main__",
    "string",
    "re",
    "difflib",
    "textwrap",
    "unicodedata",
    "stringprep",
    "readline",
    "rlcompleter",
    "struct",
    "codecs",
    "datetime",
    "calendar",
    "collections",
    "heapq",
    "bisect",
    "array",
    "weakref",
    "types",
    "copy",
    "pprint",
    "reprlib",
    "enum",
    "numbers",
    "math",
    "cmath",
    "decimal",
    "fractions",
    "random",
    "statistics",
    "itertools",
    "functools",
    "operator",
    "pathlib",
    "fileinput",
    "stat",
    "filecmp",
    "tempfile",
    "glob",
    "fnmatch",
    "linecache",
    "shutil",
    "macpath",
    "pickle",
    "copyreg",
    "shelve",
    "marshal",
    "dbm",
    "sqlite3",
    "zlib",
    "gzip",
    "bz2",
    "lzma",
    "zipfile",
    "tarfile",
    "csv",
    "configparser",
    "netrc",
    "xdrlib",
    "plistlib",
    "hashlib",
    "hmac",
    "secrets",
    "os",
    "io",
    "time",
    "argparse",
    "getopt",
    "logging",
    "getpass",
    "curses",
    "platform",
    "errno",
    "ctypes",
    "threading",
    "multiprocessing",
    "concurrent",
    "subprocess",
    "sched",
    "queue",
    "_thread",
    "_dummy_thread",
    "dummy_threading",
    "contextvars",
    "asyncio",
    "socket",
    "ssl",
    "select",
    "selectors",
    "asyncore",
    "asynchat",
    "signal",
    "mmap",
    "email",
    "json",
    "mailcap",
    "mailbox",
    "mimetypes",
    "base64",
    "binhex",
    "binascii",
    "quopri",
    "uu",
    "html",
    "xml",
    "webbrowser",
    "cgi",
    "cgitb",
    "wsgiref",
    "urllib",
    "ftplib",
    "poplib",
    "imaplib",
    "nntplib",
    "smtplib",
    "smtpd",
    "telnetlib",
    "uuid",
    "socketserver",
    "xmlrpc",
    "ipaddress",
    "audioop",
    "aifc",
    "sunau",
    "wave",
    "chunk",
    "colorsys",
    "imghdr",
    "sndhdr",
    "ossaudiodev",
    "gettext",
    "locale",
    "turtle",
    "cmd",
    "shlex",
    "tkinter",
    "typing",
    "pydoc",
    "doctest",
    "unittest",
    "lib2to3",
    "test",
    "bdb",
    "faulthandler",
    "pdb",
    "timeit",
    "trace",
    "tracemalloc",
    "distutils",
    "ensurepip",
    "venv",
    "zipapp",
    "sys",
    "sysconfig",
    "builtins",
    "warnings",
    "dataclasses",
    "contextlib",
    "abc",
    "atexit",
    "traceback",
    "__future__",
    "gc",
    "inspect",
    "site",
    "code",
    "codeop",
    "zipimport",
    "pkgutil",
    "modulefinder",
    "runpy",
    "importlib",
    "parser",
    "ast",
    "symtable",
    "symbol",
    "token",
    "keyword",
    "tokenize",
    "tabnanny",
    "pyclbr",
    "py_compile",
    "compileall",
    "dis",
    "pickletools",
    "formatter",
    "msilib",
    "msvcrt",
    "winreg",
    "winsound",
    "posix",
    "pwd",
    "spwd",
    "grp",
    "crypt",
    "termios",
    "tty",
    "pty",
    "fcntl",
    "pipes",
    "resource",
    "nis",
    "syslog",
    "optparse",
    "imp",
    "posixpath",
    "ntpath",
}


class APIVisitor(ast.NodeVisitor):
    def __init__(self, script):
        self.script = script
        self.results = {}

    def _infer(self, node):
        try:
            out = []
            for x in self.script.infer(node.lineno, node.end_col_offset):
                if (
                    not x.in_builtin_module()
                    and x.full_name is not None
                    and x.module_name.split(".")[0] not in STDLIB_MODULES
                ):
                    out.append((x.type, x.full_name))
            return out
        except:
            return []

    def _literal(self, node):
        if node is None:
            return ""

        elif isinstance(node, ast.Constant):
            if node.value in (None, False, True):
                return str(node.value)
            elif isinstance(node.value, int) and not isinstance(node.value, float):
                if -10 <= node.value <= 10:
                    return str(node.value)
                else:
                    return "int"
            else:
                return type(node.value).__name__

        elif isinstance(node, ast.Slice):
            step = self._literal(node.step)
            if step == "":
                return f"{self._literal(node.lower)}:{self._literal(node.upper)}"
            else:
                return f"{self._literal(node.lower)}:{self._literal(node.upper)}:{step}"

        else:
            return "?"

    def visit_Attribute(self, node):
        self.visit(node.value)
        if not isinstance(node.ctx, ast.Store):
            out = []
            base_result = self.results.get(
                (node.value.lineno, node.value.end_col_offset), []
            )
            for kind, match in base_result:
                out.append(("__getattr__", match + "." + node.attr))
            self.results[node.lineno, node.end_col_offset] = out

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        if not isinstance(node.ctx, ast.Store):
            if isinstance(node.slice, ast.Tuple):
                trailer = (
                    "[" + ", ".join(self._literal(x) for x in node.slice.elts) + "]"
                )
            else:
                trailer = "[" + self._literal(node.slice) + "]"

            out = []
            for kind, match in self.results.get(
                (node.value.lineno, node.value.end_col_offset), []
            ):
                out.append(("__getitem__", match + trailer))
            self.results[node.lineno, node.end_col_offset] = out

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Store):
            self.results[node.lineno, node.end_col_offset] = self._infer(node)

    def visit_Call(self, node):
        self.visit(node.func)
        for x in node.args:
            self.visit(x)
        for x in node.keywords:
            self.visit(x)

        args = []
        for x in node.args:
            if not isinstance(x, ast.Starred):
                args.append(self._literal(x))
        for x in sorted(
            [x for x in node.keywords if x.arg is not None], key=lambda x: x.arg
        ):
            args.append(x.arg + "=" + self._literal(x.value))
        if any(isinstance(x, ast.Starred) for x in node.args) or any(
            x.arg is None for x in node.keywords
        ):
            args.append("*whatever")
        trailer = "(" + ", ".join(args) + ")"

        out = []
        for kind, match in self.results.get(
                (node.func.lineno, node.func.end_col_offset), []
        ):
            out.append(("__call__", match + trailer))
        self.results[node.func.lineno, node.func.end_col_offset] = out

        self.results[node.lineno, node.end_col_offset] = self._infer(node)


counter = Counter()

# project = jedi.Project("/Users/jpivarski/irishep/awkward/src/awkward")

output_dir = "/tmp/results"

for index, filename in enumerate(glob.glob(
    "/Users/jpivarski/storage/data/GitHub-CMSSW-user-nonfork-raw-data-1Mcut-awkward/*/*.tgz"
)):
    print(filename)
    with tarfile.open(filename) as tgz:
        for info in tgz:
            if info.name.lower().endswith(".py"):
                print("    " + info.name)

                try:
                    with tgz.extractfile(info) as file:
                        full_text = file.read().decode("utf-8", errors="surrogateescape")
                except:
                    continue

            elif info.name.lower().endswith(".ipynb"):
                print("    " + info.name)

                try:
                    with tgz.extractfile(info) as file:
                        notebook_full_text = file.read().decode("utf-8", errors="surrogateescape")
                    notebook = jupytext.reads(notebook_full_text)
                    full_text = jupytext.writes(notebook, fmt="py:percent")
                except:
                    continue

            else:
                continue

            try:
                syntax_tree = ast.parse(full_text)
            except:
                continue

            script = jedi.Script(full_text)  # , project=project)

            visitor = APIVisitor(script)
            visitor.visit(syntax_tree)

            for (line, column), matches in visitor.results.items():
                for match in matches:
                    counter[match] += 1 / len(matches)

    with open(f"{output_dir}/result-after-{index}.txt", "w") as output:
        for k, v in sorted(counter.items(), key=lambda pair: pair[1]):
            print(f"{v:10.3f} {k}", file=output)
