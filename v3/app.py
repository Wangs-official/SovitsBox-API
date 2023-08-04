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
from flask import Flask, jsonify, request
import werkzeug
import shutil
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


# 自定义HTTP错误子类
class InsufficientStorage(werkzeug.exceptions.HTTPException):
    code = 800
    description = 'exception return'


# 变量提前定义

model_load_status = str(0)  # 模型加载状态，参考下方加载模型接口


class InsufficientStorage(werkzeug.exceptions.HTTPException):
    code = 801
    description = 'parametric error'


print('库加载完成，正在启动...')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': '200OK'})


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
            return jsonify({'PythonError': str(e)}), 800


@app.route('/delete_file', methods=['GET'])
def delete_file():
    try:
        delete_file_path = request.args.get('del')
        if delete_file_path == str('raw'):
            # 删除raw文件夹
            shutil.rmtree('raw', ignore_errors=True)
            infer_tool.mkdir(["raw"])
            print('服务端:文件夹 raw 内的文件已被删除')
            return jsonify({'status': 'OK', 'del_path': 'raw'})
        elif delete_file_path == str('results'):
            # 删除results文件夹
            shutil.rmtree('results', ignore_errors=True)
            infer_tool.mkdir(["results"])
            print('服务端:文件夹 results 内的文件已被删除')
            return jsonify({'status': 'OK', 'del_path': 'results'})
        else:
            return jsonify({'Error': '不是有效的参数'}), 801

    except Exception as e:
        # 如果发生错误，返回异常信息
        print("服务端:Python发生错误：" + str(e))
        return jsonify({'PythonError': str(e)}), 800


@app.route('/upload_wav', methods=['get,post'])
def upload_wav():
    try:
        wav_path_upload = request.args.get('wav_path')
        if not wav_path_upload is None:
            if os.path.isfile(wav_path_upload) and wav_path_upload.endswith('wav'):
                shutil.copy(wav_path_upload, 'raw')
                return jsonify({'status': 'OK', 'upload_file_path': wav_path_upload})
            else:
                return jsonify({'FileError': '目标文件不存在/非wav文件'}), 800
        else:
            return jsonify({'Error': '不是有效的参数'}), 801

    except Exception as e:
        # 如果发生错误，返回异常信息
        print("服务端:Python发生错误：" + str(e))
        return jsonify({'PythonError': str(e)}), 800


@app.route('/inference', methods=['post'])
def inference():
    try:
        # 获取参数
        clean_names_ls = request.args.get('clean_names_ls')
        trans_num = request.args.get('trans_num')  # int
        spk_list_ls = request.args.get('spk_list_ls')
        slice_db_num = request.args.get('slice_db')  # int
        output_file_type = request.args.get('output_file_type')
        model_path = request.args.get('model_path')
        json_path = request.args.get('json_path')
        # 加载svc模型
        if not model_path is None:
            if not json_path is None:
                if os.path.isfile(model_path) and model_path.endswith('pth'):  # 验证文件路径以及后缀名
                    print("服务端:已导入模型文件 路径:" + model_path)
                else:
                    return jsonify({'PthFileError': '目标文件不存在/非pth文件'}), 800

                if os.path.isfile(json_path) and json_path.endswith('json'):  # 验证文件路径以及后缀名
                    print('服务端:已导入Config文件' + json_path)
                else:
                    return jsonify({'JsonFileError': '目标文件不存在/非json文件'}), 800
            else:
                return jsonify({'Error': '不是有效的参数'}), 801
        else:
            return jsonify({'Error': '不是有效的参数'}), 801

        # 加载模型与创建文件夹
        svc_model = Svc(model_path, json_path)  # 存入到G变量中
        infer_tool.mkdir(["raw", "results"])

        # 以下代码为读取说话人列表
        with open(json_path, 'r') as config_json:
            config_json_speaker = json.load(config_json)

            for config_json_speaker_ls in config_json_speaker['spk']:
                print('服务端:从Config.json文件中找到了以下说话人：' + config_json_speaker_ls)

        print('服务端:模型加载已完成')
        # 好了
        # 这是一段很烂的判断（气笑）
        if not clean_names_ls is None:
            if not trans_num is None:
                if not spk_list_ls is None:
                    if not slice_db_num is None:
                        # 判断非必填项是否填写,若未填写则填写默认值
                        if output_file_type is None:
                            output_file_type = 'wav'
                        # 完事了，可以开始写正经代码了（
                        # 为了省事所以再定义点变量 屎山实锤了
                        clean_names = clean_names_ls.split(',')  # 按逗号分割多wav文件
                        trans = (list(map(int, str(trans_num))))  # 调整半音数
                        spk_list = spk_list_ls.split(',')  # 按逗号分割多说话人
                        slice_db = float(slice_db_num)  # slice_db
                        wav_format = str(output_file_type)  # 音频输出格式
                        # 下面是照搬的推理代码
                        infer_tool.fill_a_to_b(trans, clean_names)
                        for clean_name, tran in zip(clean_names, trans):
                            raw_audio_path = f"raw/{clean_name}"
                            if "." not in raw_audio_path:
                                raw_audio_path += ".wav"
                            infer_tool.format_wav(raw_audio_path)
                            wav_path = Path(raw_audio_path).with_suffix('.wav')
                            chunks = slicer.cut(wav_path, db_thresh=slice_db)
                            audio_data, audio_sr = slicer.chunks2audio(wav_path, chunks)
                            print('SovitsBox正在推理')
                            for spk in spk_list:
                                audio = []
                                for (slice_tag, data) in audio_data:
                                    print(f'#=====分段起点, {round(len(data) / audio_sr, 3)}s======')
                                    length = int(np.ceil(len(data) / audio_sr * svc_model.target_sample))
                                    raw_path = io.BytesIO()
                                    soundfile.write(raw_path, data, audio_sr, format="wav")
                                    raw_path.seek(0)
                                    if slice_tag:
                                        print('SovitsBox:跳过空段')
                                        _audio = np.zeros(length)
                                    else:
                                        out_audio, out_sr = svc_model.infer(spk, tran, raw_path)
                                        _audio = out_audio.cpu().numpy()
                                    audio.extend(list(_audio))

                                res_path = f'./results/{clean_name}_{tran}key_{spk}.{wav_format}'
                                soundfile.write(res_path, audio, svc_model.target_sample, format=wav_format)

                                print('服务端:合成完毕，已保存到' + res_path)
                                return jsonify({'status': 'OK', 'output_wav_path': res_path})
                    else:
                        return jsonify({'Error': '不是有效的参数'}), 801
                else:
                    return jsonify({'Error': '不是有效的参数'}), 801
            else:
                return jsonify({'Error': '不是有效的参数'}), 801
        else:
            return jsonify({'Error': '不是有效的参数'}), 801

    except Exception as e:
        # 如果发生错误，返回异常信息
        print("服务端:Python发生错误：" + str(e))
        return jsonify({'PythonError': str(e)}), 800


# 至此全部完毕

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=65503)  # 默认走65503端口，4.0走65504端口
