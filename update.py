import os
import json
import wget
# 更新文件，版本号在update文件夹内的ver.json内
wget.download('https://github.com/Wangs-official/SovitsBox-API/blob/main/update/ver.json',out='update/tmp/ver.json')
# 下载Github上的版本号文件

input('调用系统git pull origin命令，如果仓库不是克隆下来的话，就不要用了。回车继续')

with open('update/tmp/ver.json') as file_object:
    github_ver_code_origin = file_object.read()
    # 将版本号文件（源内容）存储到github_ver_code_origin变量内
github_ver_code = json.loads(github_ver_code_origin)

with open('update/ver.json') as file_object:
    local_ver_code_origin = file_object.read()
    # 将本地版本号文件（源内容）存储到local_ver_code_origin变量内
local_ver_code = json.loads(local_ver_code_origin)

print('Github版本号:' + github_ver_code['ver'] + ' \n 本地版本号:' + local_ver_code['ver'])
print('=======================================')
if github_ver_code == local_ver_code :
    print('版本号一致，无需更新')
else:
    input('Github版本号提前，开始更新，请提前备份raw/results文件夹内所有内容以及hubert模型文件，回车继续')
    os.system('git pull origin')
    print('更新完毕')