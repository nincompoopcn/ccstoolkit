#!/usr/bin/python
# -*- coding: utf-8 -*-

import webchat

def get_info(pronto):
  url = "https://pronto.inside.nsn.com/pronto/problemReport.html?prid=" + pronto
  return webchat.get_jquery_by_url(url)

def get_data_by_title(jquery,title):

  data_start = jquery.find("title=\"" + title + "\"")
  data_start = jquery.find("class=\"breakWD\">",data_start)
  data_end   = jquery.find("</li>",data_start)
  data_str   = jquery[data_start+len("class=\"breakWD\">") : data_end]
  
  return data_str

def seek(pronto,list_flag):
  jquery = get_info(pronto)

  description_start = jquery.find("* Description")
  description_start = jquery.find("<input type=\"hidden\" value=\"", description_start)
  description_end = jquery.find("\" id=\"description\" >", description_start)
  description = jquery[description_start + len("<input type=\"hidden\" value=\""):description_end]
  
  log_start = description.find("[8. Log File Contents]")
  log_end = description.find("[9",log_start)
  log_path = description[log_start+len("[8. Log File Contents]") : log_end]
  log_path = " ".join(log_path.split("\r\n"))
    
  print "------"
  if list_flag:
    print "Description:" 
    print description
  else:
    print "Log Path:" 
    print log_path
  print ""

  author = get_data_by_title(jquery,"Author Name")
  print "------"
  print "Author Info:" 
  print "  " + author

  author_group = get_data_by_title(jquery,"Author Group")
  print "  " + author_group
  print ""

  build = get_data_by_title(jquery,"Build")
  print "------"
  print "Build:"
  print "  " + build
  print ""
