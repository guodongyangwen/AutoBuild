# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
import requests
import subprocess
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from optparse import OptionParser
import smtplib

#===============================================参数配置begin==================================================================================
# 项目是否使用cocoaPods:1-是 0-不是
userCocoaPods = 1
# 项目工程文件名字:比如：Test.xcodeproj（非cocoaPods） 或者 Test.xcworkspace（cocoaPods）
project_name = "xxxx"
# 项目scheme名字：比如：Test（一般和项目名称一致）
scheme_name = "xxx"
# 归档类型：Release版或者Debug版
configuration = "Release"
# 证书概要文件：(就是通过Xcode选取的provisioningProfile的名字）
ProvisioningProfile = "xxx"
#===============================================
# 项目根目录:xcodebuild命令必须进入的项目目录   绝对目录
project_path = "/Users/xxx/Desktop/xxx"
# 编译后项目的app根目录：即build的.app所在的根目录
build_root_path = project_path
# 编译成功后.app所在目录
build_app_path = "%s/build/Build/Products/Release-iphoneos/%s.app" %(build_root_path,scheme_name)
# 指定项目下编译目录
#build_path = "build"
build_path = "%s/build" %(build_root_path)
#===============================================
# 打包后ipa存储目录
targetIPA_path = "/Users/xxx/Desktop/ipas"
#===============================================
#蒲公英网站的两个key和上传路径
API_Key             = "API_KEY"   #"3d109b16b9b16a8442eb601956c8f8af"  hjsht
User_Key            = "USER_KEY"#"9f7e464c5841eed38ef33709d5f8cd8a"
pgyUploadUrl        = "https://www.pgyer.com/apiv1/app/upload"
pgyDownloadUrl      = "http://www.pgyer.com/xxx"  #对应的下载地址
pgyInstallPwd       = ""
pgyPublishRange     = "2"#2:distribute directly      3:only I install
pgyIsPublishPublic  = "1"#is distribute to public
pgyUpdateDes        = ""#desc for version update
#===============================================
#邮件参数配置
from_addr = "xxx@xxx.com"
password = "您的邮箱密码"
smtp_server = "smtp.126.com"
to_addr = ''
#==============================================参数配置end===================================================================================


#==============================================具体操作的方法begin===================================================================================
# 清理项目 创建build目录*****************************************************************
def clean_project_mkdir_build():
    if userCocoaPods == 1 :#使用cocoaPods，才需要创建目录
        os.system('cd %s;xcodebuild clean -workspace %s.xcworkspace -configuration %s -target %s' % (project_path,project_name,configuration,scheme_name)) # clean 项目
        os.system('cd %s;mkdir build' % project_path) # 创建build目录
    else:
        #xcodebuild clean -project ${PROJECT_NAME}.xcodeproj -configuration ${CONFIGURATION} -alltargets
        os.system('cd %s;xcodebuild clean -project %s.xcodeproj -configuration %s  -target %s' % (project_path,project_name,configuration,scheme_name)) # clean 项目

# 编译工程为.app或者.xcarchive*****************************************************************
def build_project():
    print("build %s start"%(configuration))
    os.system ('xcodebuild -list')
    
    if userCocoaPods == 1 :#使用cocoaPods
#        build_string = "cd %s;xcodebuild -workspace %s.xcworkspace  -scheme %s -configuration %s -derivedDataPath %s ONLY_ACTIVE_ARCH=NO || exit" % (project_path,project_name,scheme_name,configuration,build_path)
        build_string = "cd %s;xcodebuild -workspace %s.xcworkspace -scheme %s -configuration %s -archivePath build/%s.xcarchive archive" % (project_path,project_name,scheme_name,configuration,scheme_name)
        print("使用cocoaPods：编译命令：%s" %(build_string));
        os.system (build_string)
    else:#使用非cocoaPods
#        build_string = "cd %s;xcodebuild -project %s.xcodeproj  -scheme %s -configuration %s -derivedDataPath %s ONLY_ACTIVE_ARCH=NO || exit" % (project_path,project_name,scheme_name,configuration,build_path)
        build_string = "cd %s;xcodebuild  -scheme %s -configuration %s -archivePath build/%s.xcarchive archive" % (project_path,scheme_name,configuration,scheme_name)
        print("不使用cocoaPods：编译命令：%s" %(build_string));
        os.system (build_string)

# 打包ipa 并且保存在桌面*****************************************************************
def build_ipa():
    global ipa_filename
    ipaName = scheme_name;
    ipa_filename = ipaName + "_" + configuration + time.strftime('_%Y-%m-%d-%H-%M-%S.ipa',time.localtime(time.time()))
#    os.system ('xcrun -sdk iphoneos PackageApplication -v %s -o %s/%s'%(build_app_path,targetIPA_path,ipa_filename))
#    os.system ('xcrun -sdk iphoneos xcodebuild -exportArchive  %s  %s/%s'%(build_app_path,targetIPA_path,ipa_filename))

    build_ipa_string = "xcodebuild  -exportArchive -exportFormat IPA -archivePath %s/%s.xcarchive -exportPath %s/%s -exportProvisioningProfile %s" % (build_path,scheme_name,targetIPA_path,ipa_filename,ProvisioningProfile)
    print("编译ipa包命令：%s" %(build_ipa_string));
    os.system (build_ipa_string)


#define upload result log
def parserUploadResult(jsonResult):
    resultCode = jsonResult['code']
    if resultCode == 0:
        downUrl = pgyDownloadUrl +"/"+jsonResult['data']['appShortcutUrl']
        print "Upload Success"
        print "DownUrl is:" + downUrl
    else:
        print "Upload Fail!"
        print "Reason:"+jsonResult['message']

# 上传ipa包到蒲公英服务器*****************************************************************
def upload_pgy():
    if os.path.exists("%s/%s" % (targetIPA_path,ipa_filename)):
        print('watting...')
        
        ipaFilePath = "%s/%s" % (targetIPA_path,ipa_filename)
        
        files = {'file': open(ipaFilePath, 'rb')}
        headers = {'enctype':'multipart/form-data'}
        payload = {'uKey':User_Key,'_api_key':API_Key,'file':ipaFilePath,'publishRange':pgyPublishRange,'isPublishToPublic':pgyIsPublishPublic, 'password':pgyInstallPwd}
        print "uploading...."
        r = requests.post(pgyUploadUrl, data = payload ,files=files,headers=headers)
        print r
        if r.status_code == requests.codes.ok:
            result = r.json()
            parserUploadResult(result)
        else:
            print 'HTTPError,Code:'+ str(r.status_code)
# 发邮件
def send_mail():
    msg = MIMEText('xx iOS测试项目已经打包完毕，请前往 http://fir.im/xxxxx 下载测试！', 'plain', 'utf-8')
    msg['From'] = _format_addr('自动打包系统 <%s>' % from_addr)
    msg['To'] = _format_addr('xx测试人员 <%s>' % to_addr)
    msg['Subject'] = Header('xx iOS客户端打包程序', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

#main方法，依次调用上面的几个方法
def main():
    # 清理并创建build目录
    clean_project_mkdir_build()
    # 编译coocaPods项目文件并 执行编译目录
    build_project()
    # 打包ipa 并制定到桌面
    build_ipa()
    #上传到蒲公英服务器
    upload_pgy()
    #发送邮件
    #send_mail()
#==============================================具体操作的方法end===================================================================================


# 执行
main()










