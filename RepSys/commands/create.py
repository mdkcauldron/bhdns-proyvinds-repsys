#!/usr/bin/python
from RepSys import Error
from RepSys.command import *
from RepSys.rpmutil import create_package
import getopt
import sys

HELP = """\
Usage: repsys create [OPTIONS] URL

Options:
    -h      Show this message

Examples:
    repsys create http://repos/svn/cnc/snapshot/newpkg
"""

def parse_options():
    parser = OptionParser(help=HELP)
    opts, args = parser.parse_args()
    if len(args) != 1:
        raise Error, "invalid arguments"
    opts.pkgdirurl = default_parent(args[0])
    opts.verbose = 1 # Unconfigurable
    return opts

def main():
    do_command(parse_options, create_package)

# vim:et:ts=4:sw=4