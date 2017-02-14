import os
import re
import time
import sys, getopt
import commands
import pexpect
from ftplib import FTP

#self module
import webchat
import wft
from config import SharedParams
from config import KnifeConfig
from config import TargetInfo

#---------------------------------------------------------
# Global parameter
#---------------------------------------------------------
USER_NAME = SharedParams.get_username()

UPLOAD_PROTOCOL = "FTP" # "SMB" / "FTP"
FTP_SERVER = "10.159.216.112" #Beijing Rotta
BJ_ROTTA_PATH = "\\\\beeefsn01.china.nsn-net.net\\DCM_project\\" + USER_NAME + "\\"
SMB_SERVER = "//eseefsn50.emea.nsn-net.net/eefs00011209"
OL_ROTTA_PATH = "\\\\nsn-intra.net\\eefs\\ROTTA\\" + USER_NAME + "\\"
PATH_IN_WFT = BJ_ROTTA_PATH # BJ_ROTTA_PATH when use FTP, OL_ROTTA_PATH when use SMB
KNIFE_FOLDER = "knife_ops/"

KNIFE_PATCH_FILE = "knife.patch"
#Lib location
DSPHWAPI_LIB_PATH = "/C_Platform/DSPHWAPI/Services/lib/Kepler/CGT7323/"
DSPHWAPI_LIB_PATH_3G = DSPHWAPI_LIB_PATH[:-8] + "/CGT738/"
DSPCCS_LIB_PATH = "/C_Platform/CCS_DSP/Services/lib/Kepler/CGT7323/"
DSPCCS_LIB_PATH_3G = DSPCCS_LIB_PATH[:-8] + "/CGT738/"
#CGT7323/" #--LTE
RTHWAPI_LIB_PATH = "/C_Platform/DSPHWAPI_RT/Tar/"
RTCCS_LIB_PATH = "/C_Platform/CCS_RT/Tar/"
#knife.zip structure
KNIFE_HEADER = "Platforms/PS_REL/"

#MODE BIT
RT_CCS_FLAG = 0b0001
DSP_CCS_FLAG = 0b0010
DSPHWAPI_FLAG = 0b0100
RTHWAPI_FLAG = 0b1000

#---------------------------------------------------------
# The links to upload knife.zip to ROTTA
#---------------------------------------------------------
def link_smb(filename):
    username = SharedParams.get_username()
    password = SharedParams.get_password()

    root_dir = username + KNIFE_FOLDER
    prompt = 'smb:'
    linsee = commands.getoutput("uname -a").split()[1]
    index = linsee.find(".")
    env = linsee[:index]

    time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))
    time_dir = "_".join((username, env, time_str))
    smb = pexpect.spawn('smbclient ' + SMB_SERVER)
    smb.expect ("password:")
    smb.sendline (password)
    smb.expect (prompt)
    smb.sendline ("mkdir " + root_dir+time_dir)
    smb.expect (prompt)
    smb.sendline ("cd " + root_dir+time_dir)
    smb.expect (prompt)
    smb.sendline ("put "+filename+' '+filename)
    smb.expect (prompt, timeout=300)
    smb.sendline ("quit")
    return (KNIFE_FOLDER + time_dir).replace("/", "\\")

def link_ftp(filename):
    username = SharedParams.get_username()
    password = SharedParams.get_password()

    root_dir = KNIFE_FOLDER
    linsee = commands.getoutput("uname -a").split()[1]
    index = linsee.find(".")
    env = linsee[:index]

    ftp = FTP()
    ftp.connect(FTP_SERVER, '21')
    ftp.login(username, password)
    print(ftp.getwelcome())

    time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))
    time_dir = "_".join((username, env, time_str))
    ftp.cwd(root_dir)
    ftp.mkd(time_dir)
    ftp.cwd(time_dir)

    file_desc = open(filename, "rb")
    ftp.storbinary("STOR %s" % os.path.basename(filename), file_desc)
    ftp.quit()
    file_desc.close()

    return (root_dir + time_dir).replace("/", "\\")

def upload(filename):
    if UPLOAD_PROTOCOL == "FTP":
        print("---Use FTP to upload knife.zip---")
        return link_ftp(filename)
    elif UPLOAD_PROTOCOL == "SMB":
        print("---Use SMB to upload knife.zip---")
        return link_smb(filename)
    else:
        assert 0, "NO SUCH PROTOCOL !!!"
        sys.exit(-1)
    return

#---------------------------------------------------------
# Libs handlers
#---------------------------------------------------------
def load_libs_common(component_path, libs_dict):
    info_dict = TargetInfo.get_data()
    target = info_dict['target_name']

    knife_zip = KNIFE_HEADER + info_dict['ps_version'] + component_path
    os.system("mkdir -p " + knife_zip)
    if libs_dict[0] == 'RTCCS':
        os.system("cp -r " + target + component_path + "*_LSP" + " " + knife_zip)
    elif libs_dict[0] == 'RTHWAPI':
        os.system("cp -r " + target + component_path + "*_lsp" + " " + knife_zip)
    elif libs_dict[0]:
        for var in libs_dict:
            os.system("cp -r " + target + component_path + var + ".lib " + knife_zip)
        return
    else:
        print("[ERROR] Input libs dict is empty, mode mismatch")
        sys.exit(-1)

    return

def load_rtccs():
    return load_libs_common(RTCCS_LIB_PATH, ['RTCCS'])

def load_rthwapi():
    return load_libs_common(RTHWAPI_LIB_PATH, ['RTHWAPI'])

def load_dspccs(libs, is3Gmode):
    if is3Gmode:
        return load_libs_common(DSPCCS_LIB_PATH_3G, libs)
    else:
        return load_libs_common(DSPCCS_LIB_PATH, libs)

def load_dsphwapi(libs, is3Gmode):
    if is3Gmode:
        return load_libs_common(DSPHWAPI_LIB_PATH_3G, libs)
    else:
        return load_libs_common(DSPHWAPI_LIB_PATH, libs)

def get_build_cmd(mode):
    if mode == 1:
        make_cmd = "make DSP_RT_TAR -j128 > log.txt"
    else:
        make_cmd = "make DSP_KEP_LTE_TAR DSP_RT_LSP_TAR -j128 > log.txt"
        #make_cmd = "make DSP_ALL_TAR -j128 > log.txt"

    print(make_cmd)
    print("------")

    return make_cmd

def update_mode_in_dict(knife_config):
    mode = 0
    #1111
    if knife_config['rthwapi']:
        mode = mode | RTHWAPI_FLAG
    if knife_config['dsphwapi_lib'] and knife_config['dsphwapi_lib'][0]:
        mode = mode | DSPHWAPI_FLAG
    if knife_config['dspccs_lib'] and knife_config['dspccs_lib'][0]:
        mode = mode | DSP_CCS_FLAG
    if knife_config['rtccs']:
        mode = mode | RT_CCS_FLAG

    assert mode != 0, "ERROR: mode == 0 !"

    knife_config['mode'] = mode

    return mode

def get_lib_from_patch(keyword):
    return commands.getoutput("cat " + KNIFE_PATCH_FILE + " | grep +++ | grep " + keyword + \
                              " | awk -F ' ' '{print $2}' \
                                | awk -F '/' '{print $4}' \
                                | awk 'a!=$0{a=$0;print}' ").split('\n')

def package_libs_with_mode():
    if os.path.exists("Platforms"):
        os.system("rm -rf Platforms")
    if os.path.exists("knife.zip"):
        os.system("rm -f knife.zip")

    knife_dict = KnifeConfig.get_data()
    mode = knife_dict['mode']

    if mode & RT_CCS_FLAG:
        load_rtccs()
    if mode & DSP_CCS_FLAG:
        load_dspccs(knife_dict['dspccs_lib'], knife_dict['3g_mode'])
    if mode & DSPHWAPI_FLAG:
        load_dsphwapi(knife_dict['dsphwapi_lib'], knife_dict['3g_mode'])
    if mode & RTHWAPI_FLAG:
        load_rthwapi()

    print("Compress knife")
    os.system("zip -r knife.zip Platforms")
    os.system("rm -rf Platforms")

    return

def build_target(target, mode):
    os.chdir(target)#>>>>>>>>>>>>>Below actions in Branch folder, eg: FB1512

    info_dict = TargetInfo.get_data_from_file()
    baseline = info_dict["baseline"]
    ps_rel = info_dict["ps_version"]
    assert baseline, "[ERROR] baseline missing, need to update target.info !"
    assert ps_rel, "[ERROR] psline missing, need to update target.info !"

    make_cmd = get_build_cmd(mode)
    os.system(make_cmd)
    ###some time even build successfully, but return value is not 0
    #make_ret=commands.getstatusoutput(make_cmd)
    #assert  make_ret[0] == 0,"make Error(" + str(make_ret[0]) + ") !!!"

    os.chdir("..")#>>>>>>>>>>>>>Above actions in Branch folder, eg: FB1512

    return

def auto_get_knife_config(knife_config):
    print("[Info] get knife information from knife.patch!")
    print("------")
    os.chdir(knife_config['target'])
    os.system("svn diff > " + KNIFE_PATCH_FILE)
    knife_config['rtccs'] = True if get_lib_from_patch("CCS_RT")[0]  else False
    knife_config['dspccs_lib'] = get_lib_from_patch("CCS_DSP")
    knife_config['dsphwapi_lib'] = get_lib_from_patch("DSPHWAPI")
    knife_config['rthwapi'] = True if get_lib_from_patch("DSPHWAPI_RT")[0] else False
    print(commands.getoutput("cat " + KNIFE_PATCH_FILE + " | grep +++ "))
    print("")
    os.chdir("..")
    return knife_config

def get_config_dict(params):
    if params.quick:
        knife_config = KnifeConfig.get_data_from_file()
    else:
        assert params.target, "[ERROR] Target missing!"

        knife_config = {
            "target" : params.target,
            "mode" : '',
            "3g_mode" : params.mode3g,
            "rtccs" : params.rtccs,
            "dspccs_lib" : params.dspccs,
            "dsphwapi_lib" : params.dsphwapi,
            "rthwapi" : params.rthwapi
        }

        if params.auto:
            auto_get_knife_config(knife_config)
            knife_config['3g_mode'] = params.mode3g

        update_mode_in_dict(knife_config)
        #update .knife.config
        KnifeConfig.set_data(knife_config)

    KnifeConfig.check()

    return knife_config

def get_target_info(xline):
    print("try to get specific version")
    print("------")

    baseline = ''
    ps_rel = ''
    dshwapi_sw = ''

    if -1 != xline.find('DSPHWAPI'):
        dshwapi_sw = xline
    else:
        if -1 != xline.find('PS'):
            ps_rel = xline
        else:
            baseline = xline
            ps_rel = wft.get_psline_by(baseline)

        dshwapi_sw = wft.get_upline_by(ps_rel)

    assert dshwapi_sw, "[ERROR] cannot find upline !"
    print(dshwapi_sw)
    print("------")

    target = wft.get_target_by(dshwapi_sw)
    svn_addr = wft.get_svn_by(dshwapi_sw)

    info_dict = {
        "baseline": baseline,
        "ps_version": ps_rel,
        "dsphwapi_version": dshwapi_sw,
        "target_name": target,
        "svn_addr": svn_addr
    }

    return info_dict

#---------------------------------------------------------
# SVN related
# 1. mknife
# 2. checkout
#---------------------------------------------------------
def check_and_get_ecl(svn_addr):
    if os.path.exists("ECL"):
        return

    svn_log = commands.getoutput("svn log -v -l 3")
    revision_start_index = svn_log.rfind("trunk:")
    revision_end_index = svn_log.find(")", revision_start_index)
    revision_num = svn_log[revision_start_index + len("trunk:"):revision_end_index]
    print("ECL revision: " + revision_num)

    trunk_index = svn_addr.rfind("/tags/")
    svn_addr = svn_addr[:trunk_index] + "/trunk@" + revision_num
    os.system("svn switch " + svn_addr)

    return

def svn_upgrade_to_reversion(svn_number):
    svn_reversion = commands.getoutput("svn info | grep Revision")[len("Revision: ") : ]
    if svn_reversion != svn_number:
        os.system("svn update -r " + svn_number)
        os.system("python ECL.py")
        svn_reversion = commands.getoutput("svn info | grep Revision")[len("Revision: ") : ]
        assert svn_reversion == svn_number, "[ERROR] Revision update failed!"
    else:
        print("Revision is right, no need to update")
        print("------")

    return
#---------------------------------------------------------
# Two knife actions:
# 1. checkout
# 2. make
# 3. update
#---------------------------------------------------------
def checkout(params):
    assert params.baseline, "[ERROR] Baseline missing!"

    SharedParams.set_password()

    info_dict = get_target_info(params.baseline)

    #if check sccessfully, it means the code already exist
    TargetInfo.check(info_dict)

    os.system("mkdir " + info_dict['target_name'])
    os.chdir(info_dict['target_name'])#>>>>>>>>>>>>>Below actions in Target folder, eg: FB1512

    TargetInfo.set_data(info_dict)

    print("ready to checkout: " + info_dict['svn_addr'])
    os.system("svn co " + info_dict['svn_addr'] + ' .')
    print("-------")

    check_and_get_ecl(info_dict['svn_addr'])
    os.system("python ECL.py")

    os.chdir("..")#>>>>>>>>>>>>>Above actions in Target folder, eg: FB1512

    return

def make(params):
    knife_config = get_config_dict(params)

    KnifeConfig.data_print()

    build_target(knife_config['target'], knife_config['mode'])
    print("-------")

    package_libs_with_mode()
    print("-------")

    SharedParams.set_password()
    print("-------")

    rotta_dir = upload("knife.zip")
    print("-------")

    wft.request_knife(TargetInfo.get_data()['baseline'], rotta_dir)
    print("--END--")

    return

def update(params):
    assert params.target, "[ERROR]Missing!"
    assert params.baseline or params.reversion, "[ERROR]Line missing!"

    if params.reversion:
        svn_number = params.reversion
    else:
        info_dict = get_target_info(params.baseline)
        svn_number = wft.get_svn_number_by(info_dict['ps_version'])

    print("svn reversion : " + svn_number)
    print("------")

    os.chdir(params.target)

    svn_upgrade_to_reversion(svn_number)

    os.chdir("..")

    return
