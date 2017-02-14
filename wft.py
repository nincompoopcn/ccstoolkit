#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib

import webchat
from config import SharedParams

USER_NAME = SharedParams.get_username()

BJ_ROTTA_PATH = "\\\\beeefsn01.china.nsn-net.net\\DCM_project\\" + USER_NAME + "\\"
OL_ROTTA_PATH = "\\\\nsn-intra.net\\eefs\\ROTTA\\" + USER_NAME + "\\"
PATH_IN_WFT = BJ_ROTTA_PATH # BJ_ROTTA_PATH when use FTP, OL_ROTTA_PATH when use SMB

def get_item(build, item_name):
    url = "https://wft.inside.nokiasiemensnetworks.com:8000/builds/" + build + "/partial.js?partial=" + item_name
    return webchat.get_jquery_by_url(url)

def get_baseline(build):
    return get_item(build, "baselines")

def get_download(build):
    return get_item(build, "download")

def get_assignments(build):
    return get_item(build, "assignments")

def request_knife(baseline, dir):
    print("Submit knife request to WFT")

    url = "https://wam.inside.nsn.com/siteminderagent/forms/login.fcc"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,et;q=0.4,zh-TW;q=0.2"
    }

    data = urllib.urlencode({
        "SMENC": "ISO-8859-1", 
        "SMLOCALE": "US-EN", 
        "USER": SharedParams.get_username(), 
        "PASSWORD": SharedParams.get_password(), 
        "target": "https://wft.inside.nsn.com/ALL/knife_requests/new", 
        "smauthreason": 0, 
        "postpreservationdata": ""
    })

    res = webchat.post(url, header, data)
    mail_line = res.rfind('name="knife_request[result_receiver]"')
    mail_end = res.rfind('"', 0, mail_line)
    mail_start = res.rfind('"', 0, mail_end)
    receiver_mail = res[mail_start+1:mail_end]

    url = "https://wft.inside.nsn.com/ALL/knife_requests"

    data = urllib.urlencode({
        "knife_request[knife_type]": "trunk" if 'DNH0.0' in baseline else "fb",
        "knife_request[request_type]": "baseline",
        "knife_request[baseline]": baseline,
        "knife_request[module]": "hdbde",
        "knife_request[knife_dir]": PATH_IN_WFT + dir,
        "knife_request[force_knife_dir]": 1,
        "knife_request[version_number]": 99,
        "knife_request[dcm_knife]": 0,
        "knife_request[server]": "http://beling18.china.nsn-net.net:8080",
        "knife_request[edit_config]": 0,
        "knife_request[rebuild_sc][]":"PS_REL" if 'DNH0.0' in baseline else "PS",
        "knife_request[flags][]": "bts",
        "knife_request[no_reference]": 1,
        "knife_request[purpose]":"debug",
        "use_knife_package": 1,
        "knife_request[result_receiver]": receiver_mail
    })

    data += '&' + urllib.urlencode({
        "knife_request[flags][]": "map"
    })

    webchat.post(url, header, data)

    return 

def baseline_search(line):
    jquery = get_assignments(line)
    """
    branch_start = jquery.find("Branch")
    branch_start = jquery.find("<td>", branch_start)
    branch_end = jquery.find("<\/td>", branch_start)
    branch = jquery[branch_start + len("<td>"):branch_end]

    print "---Branch---"
    print branch
    """
    #print "---Baseline---"
    baseline_end = jquery.find("assignments")
    baseline = []
    while jquery.find("/ALL/builds/",baseline_end) > 0:
        baseline_start = jquery.find("/ALL/builds/",baseline_end)
        baseline_end = jquery.find("\\\">", baseline_start)
        baseline_temp = jquery[baseline_start + len("/ALL/builds/"):baseline_end]
        #if "PS_REL" in baseline_temp:
        baseline.append(baseline_temp)
    #print baseline
    
    return baseline

def seek(xline):
    psline_array = []

    if -1 != xline.find('DSPHWAPI'):
        psline_array = baseline_search(xline)
    elif -1 != xline.find('PS'):
        psline_array.append(xline)
    else:
        print("[ERROR] " + line + " is neither PS line nor DSP line")
        sys.exit(-1)

    for psline in psline_array:
        baseline = baseline_search(psline)
        if baseline:
            print("------")
            print(psline)
            print("------")
            print(baseline)
            print("-------------")
            print("")

    return

#---------------------------------------------------------
# Searching line functions(baseline, ps_line, uphwapi_line)
# 1. get_line_with_key_word
# 2. get_psline_from_baseline
# 3. get_upline_from_psline
#---------------------------------------------------------
def get_line_with_key_word(basedline,key):
  print basedline
  print "------"

  jquery = get_baseline(basedline)
  #print jquery
  ret_line_index = jquery.rfind("<td>" + key + "<\/td>")
  start_index = jquery.find("/ALL/builds/", ret_line_index)
  end_index = jquery.find("\\\">", start_index)
  ret_line = jquery[start_index + len("/ALL/builds/"):end_index]
  
  return ret_line

def get_psline_by(baseline):
  return get_line_with_key_word(baseline, "PS")

def get_upline_by(psline):
  return get_line_with_key_word(psline, "PS_DSPHWAPI_SW")
  
def get_svn_number_by(psline):
  jquery = get_baseline_by(psline)
  # print jquery
  ret_line_index = jquery.find("/isource/svnroot/BTS_SC_DSPHWAPI/")
  start_index = jquery.find("@", ret_line_index)
  end_index = jquery.find(r'\n', start_index)
  svn_number = jquery[start_index + len("@") : end_index]
  
  return svn_number

def get_target_by(upline):
    # get my code folder name; e.g: FB1512022
    if upline[0] != 'R' and upline[0] != 'D':
        target = ''.join((''.join(upline.split('LRC_PS_DSPHWAPI_SW_20'))).split('_'))
    else:
        key_word = upline.split('_')[0]
        target = key_word + '_' + ''.join((upline.split('PS_DSPHWAPI_SW_20')[1]).split('_'))

    print target
    print "------"

    return target

def get_svn_by(upline):

    jquery = get_download(upline)
    
    #Change to beijing since main linsee change to hzling
    print "Find from HZ BTS_SC_DSPHWAPI!"
    svn_start_index = jquery.rfind("https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SC_DSPHWAPI")
    if -1 == svn_start_index:
        print "Find from OL BTS_SC_DSPHWAPI!"
        svn_start_index = jquery.rfind("https://svne1.access.nsn.com/isource/svnroot/BTS_SC_DSPHWAPI/")

    if -1 == svn_start_index:
        print "Find from HZ LRC_SC_UPHWAPI!"
        svn_start_index = jquery.rfind("https://beisop60.china.nsn-net.net/isource/svnroot/LRC_SC_UPHWAPI/")

    if -1 == svn_start_index:
        print "ERROR: Cannot find the line from svn, mostly the code is frozen!"
        print jquery
        sys.exit()

    svn_end_index = jquery.find("<\/a>", svn_start_index)
    svn_url = jquery[svn_start_index:svn_end_index]

    print "------"
    
    return svn_url