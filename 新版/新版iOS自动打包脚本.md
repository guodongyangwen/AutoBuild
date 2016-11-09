# 新版iOS自动打包脚本
###1、相关参数配置
####1、项目配置
    1、相关配置
        1、项目名称：project_name 
         2、scheme_name(和项目名称一致）
        3、ProvisioningProfile(证书名称，就是XCode里面选择的名称）
        4、Project_path （项目所在路径）
        5、targetIPA_path（IPA打包后的路径，绝对路径而且必须存在）
    2、主要配置
        1、Project_path
        2、targetIPA_path

####2、蒲公英配置
    1、相关配置
        1、API_Key
        2、User_Key
        3、pgyDownloadUrl
        4、pgyUploadUrl
    2、主要配置
        1、API_Key
        2、User_Key
    
####3、邮箱配置


###2、使用

    终端 切换到autobuild.py的目录下，直接调用 python autobuild.py

