#usage
# 1. open the terminal client and switch to your project directory
# 2. input the cmd: python NearMerchantAutoBuild.py -w workspaceName.xcworkspace -s 
#                    schemeName -t NerMerchant -o ipaFilePath(~/Desktop/NearMerchant.ipa)

from optparse import OptionParser
import subprocess
import requests

#iOS build setting
CODE_SIGN_IDENTITY = "iPhone Distribution: Beijing Qfpay Technology Company Limited"
PROVISIONING_PROFILE = "1fa0ccff-c5b7-4312-8c60-ea92fa7e0bbd"
CONFIGURATION = "Release"
SDK = "iphoneos"

#pgyer setting
PGYER_UPLOAD_URL 		= "http://www.pgyer.com/apiv1/app/upload"
PGYER_DOWNLOAD_BASE_URL = "http://www.pgyer.com/testbuild"
PGYER_USER_KEY 			= "9f7e464c5841eed38ef33709d5f8cd8a" #t #"ebdbfa7770bec238a0e9770e79459210" #p
PGYER_API_KEY 			= "3d109b16b9b16a8442eb601956c8f8af" #t #"fb914b7d5b72fc11622cafaa3dfb183f" #p
PGYER_INSTALL_PWD		= ""
PGYER_PUBLISH_RANGE 	= "2"   #2:distribute directly      3:only I install
PGYER_IS_PUBLISH_PUBLIC = "1" #is distribute to public
PGYER_UPDATE_DES     	= ""    #desc for version update

#clean build dir
def cleanBuildDir(buildDir):
	cleanCmd = "rm -r %s" %(buildDir)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print "cleaned buildDir: %s" %(buildDir)

#define upload result log
def parserUploadResult(jsonResult):
	resultCode = jsonResult['code']
	if resultCode == 0:
		downUrl = PGYER_DOWNLOAD_BASE_URL +"/"+jsonResult['data']['appShortcutUrl']
		print "Upload Success"
		print "DownUrl is:" + downUrl
	else:
		print "Upload Fail!"
		print "Reason:"+jsonResult['message']

#upload ipa file to pgyer

def uploadIpaToPgyer(ipaPath):
    print "ipaPath:"+ipaPath
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'uKey':PGYER_USER_KEY,'_api_key':PGYER_API_KEY,'file':ipaPath,'publishRange':PGYER_PUBLISH_RANGE,'isPublishToPublic':PGYER_IS_PUBLISH_PUBLIC, 'password':PGYER_INSTALL_PWD}
    print "uploading...."
    r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
    print r
    if r.status_code == requests.codes.ok:
         result = r.json()
         parserUploadResult(result)
    else:
        print 'HTTPError,Code:'+ str(r.status_code)

#build project ( no pod)
def buildProject(project, target, output):
	buildCmd = 'xcodebuild -project %s -target %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s"' %(project, target, SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE)
	process = subprocess.Popen(buildCmd, shell = True)
	process.wait()

	signApp = "./build/%s-iphoneos/%s.app" %(CONFIGURATION, target)
	signCmd = "xcrun -sdk %s -v PackageApplication %s -o %s" %(SDK, signApp, output)
	process = subprocess.Popen(signCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	uploadIpaToPgyer(output)
	cleanBuildDir("./build")

#build workspace (use pod)
def buildWorkspace(workspace, scheme, output):
	process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
	(stdoutdata, stderrdata) = process.communicate()
	buildDir = stdoutdata.strip() + '/build'
	print "buildDir: " + buildDir
	buildCmd = 'xcodebuild -workspace %s -scheme %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" SYMROOT=%s' %(workspace, scheme, SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE, buildDir)
	process = subprocess.Popen(buildCmd, shell = True)
	process.wait()

	signApp = "./build/%s-iphoneos/%s.app" %(CONFIGURATION, scheme)
	signCmd = "xcrun -sdk %s -v PackageApplication %s -o %s" %(SDK, signApp, output)
	process = subprocess.Popen(signCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	uploadIpaToPgyer(output)
	cleanBuildDir(buildDir)

#start build
def xcbuild(options):
	project = options.project
	workspace = options.workspace
	target = options.target
	scheme = options.scheme
	output = options.output

	if project is None and workspace is None:
		pass
	elif project is not None:
		buildProject(project, target, output)
	elif workspace is not None:
		buildWorkspace(workspace, scheme, output)

def main():
	
	parser = OptionParser()
	parser.add_option("-w", "--workspace", help="Build the workspace name.xcworkspace.", metavar="NearMerchant.xcworkspace")
	parser.add_option("-p", "--project", help="Build the project name.xcodeproj.", metavar="NearMerchant.xcodeproj")
	parser.add_option("-s", "--scheme", help="Build the scheme specified by schemename. Required if building a workspace.", metavar="NearMerchant")
	parser.add_option("-t", "--target", help="Build the target specified by targetname. Required if building a project.", metavar="NearMerchant")
	parser.add_option("-o", "--output", help="specify output filename", metavar="NearMerchant.ipa")

	(options, args) = parser.parse_args()

	print "options: %s, args: %s" % (options, args)

	xcbuild(options)

if __name__ == '__main__':
	main()
