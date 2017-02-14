#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import midori
import pronto
import knife
import wft
import test
from config import SharedParams

USAGE_EXAMPLE = "make knife: \n" \
              "     1. ./toolkit.py mk -t MB1609009/ -rc -dc AaSysLog -rh -dh Startup\n" \
              "        //normal usage with input lib parameters\n" \
              "     2. ./toolkit.py mk -t FB1512063 -a\n" \
              "        //AUTO make according to diff (knife.diff)\n" \
              "     3. ./toolkit.py mk -q\n" \
              "        //QUICK make according your last usage, last parameter store in .knife.config\n" \
              "\n" \
              "check out codes: \n" \
              "     1. ./toolkit.py co -b DNH0.0_ENB_94160820_20097\n" \
              "     2. ./toolkit.py co -b MBLRC_PS_REL_2016_08_013\n" \
              "     3. ./toolkit.py co -b MBLRC_PS_DSPHWAPI_SW_2016_08_007\n" \
              "\n" \
              "update codes in trunk: \n" \
              "     1. ./toolkit.py up -t FB1512 -v 81933 \n" \
              "        //Update trunk to paticular version, 81933 is svn commit revision\n" \
              "\n" \
              "search pronto information/enb version/fault/messageid\n" \
              "     1. ./toolkit.py sk -pr PR063228\n" \
              "     2. ./toolkit.py sk -pr PR063228 -l //list the whole description\n" \
              "     3. ./toolkit.py sk -b MBLRC_PS_DSPHWAPI_SW_2016_09_009\n" \
              "     5. ./toolkit.py sk -m FDD\n" \
              "     6. ./toolkit.py sk -f 4234\n"

def seek(params):
    assert params.pronto or params.baseline \
         or params.msgId or params.faultId, "[ERROR] Missing parameters!"

    """
    if params.reversion:
        if params.target:
            psline = ci_seek(params.branch,params.reversion)
            baseline_seek(psline)
    """

    SharedParams.set_password()

    if params.baseline:
        wft.seek(params.baseline)

    if params.pronto:
        pronto.seek(params.pronto, params.list)

    if params.msgId or params.faultId:
        midori.seek(params.msgId, params.faultId)

def extract():
    """parse the argument from cmdline"""

    parser = argparse.ArgumentParser(description=\
             "This is an easy tool kit for knife making and information searching !")

    parser.add_argument('action', nargs='?', help='co mk up sk test')

    parser.add_argument('-b', nargs="?", metavar="baseline", dest="baseline", \
                              help='ENB/PS/UP Baseline, e.g. DNH3.0_ENB...')
    parser.add_argument('-t', nargs="?", metavar="target", dest="target", \
                              help='Codes target folder, e.g. FB1512023')

    parser.add_argument('-rc', dest="rtccs", action="store_true", help='RTCCS changed')
    parser.add_argument('-dc', nargs="+", metavar="LibName1", dest="dspccs", \
                               help='DSPCCS changed Libs')
    parser.add_argument('-dh', nargs="+", metavar="LibName1", dest="dsphwapi", \
                               help='DSPHWAPI changed Libs Name')
    parser.add_argument('-rh', dest="rthwapi", action="store_true", help='RTHWAPI changed')
    parser.add_argument('-3g', dest="mode3g", action="store_true", \
                                help='Use 3g mode? A required arg when make DSP related knife')

    parser.add_argument('-q', dest="quick", action="store_true", \
                              help='Quick Make, get parameters from .knife.config')
    parser.add_argument('-a', dest="auto", action="store_true", \
                              help='Auto Make, get parameters from branch/knife.patch')

    parser.add_argument('-m', nargs="?", metavar="msgId", dest="msgId", \
                              help='Message Id, e.g. 0xFDD')
    parser.add_argument('-f', nargs="?", metavar="faultId", dest="faultId", \
                              help='Fault Id, e.g. 4234')

    parser.add_argument('-pr', nargs='?', metavar='pronto', dest='pronto', \
                               help='Pronto ID, e.g. PR193948')
    parser.add_argument('-l', dest="list", action="store_true", help='If need list description ?')

    parser.add_argument('-v', nargs="?", metavar="reversion", dest="reversion", \
                              help='svn reversion, e.g. 89131')

    params = parser.parse_args()
    if not params.action:
        parser.print_help()
        sys.exit(0)

    return params

def action(parsed_args):
    """handle action for work"""

    action_map = {
        'co': knife.checkout,
        'mk': knife.make,
        'up': knife.update,
        'sk': seek,
        'test': test.handler
    }

    action_map[parsed_args.action](parsed_args)
    return
