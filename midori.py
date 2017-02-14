#!/usr/bin/python
# -*- coding: utf-8 -*-

import webchat
import json

def get_info(target, targetId):
  url = "https://midori.emea.nsn-net.net/api/3/" + target + "/" + targetId
  return webchat.get_jquery_by_url(url)

def get_msg(msgId):
  return get_info("messages_wcdma",msgId)

def get_fault(faultId):
  return get_info("faults",faultId)  

def seek(msgId,faultId):
  if msgId:
    msgId = str(int(msgId,16))
    jquery = get_msg(msgId)
    
    #JSON to dict
    ret_dict = json.loads(jquery)
    print "---Messsage Id Information---"
    print "Id:    %s/%s" %(ret_dict['number'], hex(ret_dict['number'])) 
    print "Name: ", ret_dict['name'];
    print "Stat: ", ret_dict['status'];
    print "SC:   ", ret_dict['system_component'];
    print "File: ", ret_dict['messageid_filename'];
    print "Desp: ", ret_dict['description'];

    #dict to JSON：
    #json_str = json.dumps(dict)

  if faultId:
    jquery = get_fault(faultId)
    ret_dict = json.loads(jquery)
    print "---Fault Id Information---"
    print "Id:   ", ret_dict['number']; 
    print "Name: ", ret_dict['name'];
    print "Stat: ", ret_dict['status'];
    print "SC:   ", ret_dict['related_to_range'];
    print "Desp: ", ret_dict['description'];

  return