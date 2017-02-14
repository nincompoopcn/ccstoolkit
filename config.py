#!/usr/bin/env python
#-*- coding: utf-8 -*-

import commands
import getpass
import json
import os
import sys

USER_NAME = commands.getoutput("whoami")

TARGET_INFO_FILE = "target.info"
KNIFE_CONFIG_FILE = ".knife.config"
LAB_USER_PATH = "/var/fpwork1/"+USER_NAME
KNIFE_CONFIG_FILE = LAB_USER_PATH + "/" + KNIFE_CONFIG_FILE

class SharedParams:
    user_name = USER_NAME
    password = "password"

    @staticmethod
    def get_username():
        return SharedParams.user_name
    @staticmethod
    def set_username():
        SharedParams.user_name = commands.getoutput("whoami")
    @staticmethod
    def get_password():
        return SharedParams.password
    @staticmethod
    def set_password():
        SharedParams.password = getpass.getpass("password for " + USER_NAME + ": ")

class KnifeConfig:
    config_data = {
        'target' : "FB1512",
        'mode' : '1',
        '3g_mode' : 'lte',
        'rtccs' : True,
        'dspccs_lib' : ["AaMem", "AaSysLog"],
        'dsphwapi_lib' : [''],
        'rthwapi' : False
    }

    @staticmethod
    def get_data_from_file():
        file_desc = open(KNIFE_CONFIG_FILE, "r")
        dict_str = json.load(file_desc)
        file_desc.close()

        KnifeConfig.config_data.update(dict_str)
        return dict_str

    @staticmethod
    def get_data():
        return KnifeConfig.config_data

    @staticmethod
    def set_data(newconfig):
        json_str = json.dumps(newconfig, indent=2)
        file_desc = open(KNIFE_CONFIG_FILE, "w")
        file_desc.write(json_str)
        file_desc.close()
        #update class data
        KnifeConfig.config_data.update(newconfig)

    @staticmethod
    def check():
        target = KnifeConfig.config_data['target']
        assert int(KnifeConfig.config_data['mode']) != 0, "[ERROR] mode == 0 !"
        assert os.path.exists(target), "[ERROR] " + target + " not exist"
        assert os.path.exists(target + "/" + TARGET_INFO_FILE), \
               "[ERROR] " + target + "/" + TARGET_INFO_FILE + " not exist"
        assert os.path.exists(KNIFE_CONFIG_FILE), "[ERROR] " + KNIFE_CONFIG_FILE + " not exist"
        return

    @staticmethod
    def data_print():
        print("Begin to make knife:")
        print("------")
        print("target: %s" % KnifeConfig.config_data['target'])
        print("mode: %s" % KnifeConfig.config_data['mode'])
        print("3g_mode: %s" % KnifeConfig.config_data['3g_mode'])
        print("dsphwapi_libs: %s" % KnifeConfig.config_data['dsphwapi_lib'])
        print("dspccs_libs: %s" % KnifeConfig.config_data['dspccs_lib'])
        print("rtccs_libs: %s" % KnifeConfig.config_data['rtccs'])
        print("rthwapi_libs: %s" % KnifeConfig.config_data['rthwapi'])
        print("------")

class TargetInfo:
    info = {
        "baseline": 'baseline',
        "ps_version": 'ps_rel',
        "dsphwapi_version": 'dashwapi_sw',
        "target_name": 'target',
        "svn_addr": 'svn_addr'
    }

    @staticmethod
    def get_data_from_file():
        file_desc = open(TARGET_INFO_FILE, "r")
        info_dict = json.load(file_desc)
        file_desc.close()

        TargetInfo.info.update(info_dict)
        return info_dict

    @staticmethod
    def get_data():
        return TargetInfo.info

    @staticmethod
    def set_data(newinfo):
        json_str = json.dumps(newinfo, indent=2)
        file_desc = open(TARGET_INFO_FILE, "w")
        file_desc.write(json_str)
        file_desc.close()
        #update class data
        TargetInfo.info.update(newinfo)

    @staticmethod
    def check(info_dict):
        target = info_dict['target_name']
        if os.path.exists(target):
            print("[INFO] target exist, check config file")
            os.chdir(target)

            if os.path.exists("C_Platform"):
                if os.path.exists(TARGET_INFO_FILE):
                    print("[INFO] Update configuration file !")
                else:
                    print("[WARNING] target existed without configuration file ! Create one !")
                #update config file anyway
                TargetInfo.set_data(info_dict)
                sys.exit(0)
            else:
                os.chdir("..")
                os.system("rm " + target + " -rf")
                print("[INFO] Remove empty target,continue... !")
                print("------")
        return

class TestConfig:
    var_a = 1230
    #@staticmethod
    def get_data(KnifeConfig):
        print(str(TestConfig.var_a))
        return TestConfig.var_a
    #@staticmethod
    def set_data(KnifeConfig, new_value):
        TestConfig.var_a = new_value
