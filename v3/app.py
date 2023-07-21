#
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |# '.
#                 / \\|||  :  |||# \
#                / _||||| -:- |||||- \
#               |   | \\\  -  #/ |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永无BUG
#
# SovitsBox——让小白也会用SO-VITS-SVC，分为服务端以及用户端
# Sovits3.0服务端

# 先提示一下

import time
print("SovitsBox服务端(版本3.0)\n请提前安装好所有库(具体请查看README)\n将在3s后启动")
time.sleep(3)

# 引用必要库

print("正在加载库")
from flask import Flask, jsonify , request
import json
import wget
import colorama
import os
import io
import logging
from pathlib import Path

import librosa
import numpy as np
import soundfile

from inference import infer_tool
from inference import slicer
from inference.infer_tool import Svc

print('库加载完成，正在启动...')

app=Flask(__name__)

# 状态
# 用法：GET请求
# 无请求参数
@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': '200OK'})

# 下载hubert模型
# 用法：GET请求
# 请求参数
# KEY:download VALUE:是否下载 TYPE:boolean 必须
@app.route('/download_hubert', methods=['GET'])
def download_hubert():
    # 获取参数
    hubert_download = request.args.get('download')
    if hubert_download:
        try:
            print("服务端:正在下载hubert文件,可随时使用ctrl+C退出")
            # 使用wget库下载
            wget.download('https://github.com/bshall/hubert/releases/download/v0.1/hubert-soft-0d54a1f4.pt',
                          out='hubert/hubert-soft-0d54a1f4.pt')
            return jsonify({'download_status': 'OK'})

        except Exception as e:
            # 如果发生错误，返回异常信息
            print("服务端:Python发生错误：" + str(e))
            return jsonify({'PythonError': str(e)})


# 加载模型接口
# 用法：GET请求
# 请求参数
# KEY:model_path VALUE:模型路径 TYPE:string 必须
# KEY:json_path VALUE:config.json路径 TYPE:string 必须
@app.route('/loadmodel', methods=['GET'])
def loadmodel():
    model_path = request.args.get('model_path')
    json_path = request.args.get('json_path')
    try:
        if os.path.isfile(model_path) and model_path.endswith('pth'):  # 验证文件路径以及后缀名
            print("服务端:已导入模型文件 路径:" + model_path)
        else:
            return jsonify({'Error' : '目标文件不存在/非pth文件'})

        if os.path.isfile(json_path) and json_path.endswith('json'): # 验证文件路径以及后缀名
            print('服务端:已导入Config文件' + json_path)
        else:
            return jsonify({'Error' : '目标文件不存在/非json文件'})

        # 加载模型与创建文件夹
        svc_model = Svc(model_path, json_path)
        infer_tool.mkdir(["raw", "results"])
        model_load_status = str(1) # 模型加载后写入变量

        #以下代码为读取说话人列表
        with open(json_path, 'r') as config_json:
            config_json_speaker = json.load(config_json)

        for config_json_speaker_ls in config_json_speaker['spk']:
            print('服务端:从Config.json文件中找到了以下说话人：' + config_json_speaker_ls)

        print('服务端:模型加载已完成')
        return jsonify({'status':'OK','speaker_ls':config_json_speaker_ls})


    except FileNotFoundError:
        # 如果Hubert文件不存在，那就特殊报错（？）
        print("服务端:hubert模型不存在，请访问URL：http://127.0.0.1:65503/download_hubert?download=true 下载")
        return jsonify({'HubertNotFoundError': 'hubert模型不存在，请访问URL：http://127.0.0.1:65503/download_hubert?download=true 下载'})

    except Exception as e:
        # 如果发生错误，返回异常信息
        print("服务端:Python发生错误：" + str(e))
        return jsonify({'PythonError': str(e)})


if __name__=='__main__':
    app.run(host='127.0.0.1', port=65503)  # 默认走65503端口，4.0走65504端口