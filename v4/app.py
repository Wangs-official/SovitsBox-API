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
# Sovits4.0服务端

# 先提示一下

import time

print("SovitsBox服务端(版本4.0)\n请提前安装好所有库(具体请查看README)\n将在3s后启动")
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
import time
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile

from inference import infer_tool
from inference import slicer
from inference.infer_tool import Svc


# 自定义HTTP错误子类
class InsufficientStorage(werkzeug.exceptions.HTTPException):
    code = 800
    description = 'exception return'


class InsufficientStorage(werkzeug.exceptions.HTTPException):
    code = 801
    description = 'parametric error'

print('库加载完成，正在启动...')

app = Flask(__name__)

# 设置超时时间10分钟，防止推理过慢产生的问题
app.config["timeout"] = 600


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': '200OK'})


@app.route('/download_contentvec', methods=['GET'])
def download_hubert():
    # 获取参数
    contentvec_download = request.args.get('download')
    if contentvec_download:
        try:
            print("服务端:正在下载contentvec文件,可随时使用ctrl+C退出")
            # 使用wget库下载
            wget.download('https://ibm.box.com/s/z1wgl1stco8ffooyatzdwsqn2psd9lrr',
                          out='hubert/checkpoint_best_legacy_500.pt')
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
        clean_names_ls = request.args.get('clean_names_ls')
        trans_num = request.args.get('trans_num')  # int
        spk_list_ls = request.args.get('spk_list_ls')
        slice_db_num = request.args.get('slice_db')  # int
        output_file_type = request.args.get('output_file_type') # 不必要
        model_path = request.args.get('model_path')
        json_path = request.args.get('json_path')
        noice_scale = request.args.get('noice_scale')  # 不必须
        pad_seconds = request.args.get('pad_seconds')  # 不必须
        auto_predict_f0 = request.args.get('auto_predict_f0')  # 不必须
        cluster_model_path = request.args.get('cluster_model_path')  # 不必须
        cluster_infer_ratio = request.args.get('cluster_infer_ratio')  # 不必须，float
        if not model_path is None:
            if not json_path is None:
                if os.path.isfile(model_path) and model_path.endswith('pth'):  # 验证文件路径以及后缀名
                    print("服务端:已导入模型文件 路径:" + model_path)
                else:
                    return jsonify({'PthFileError': '目标文件不存在/非pth文件'}), 800
                if os.path.isfile(json_path) and json_path.endswith('json'):  # 验证文件路径以及后缀名
                    print('服务端:已导入Config文件' + json_path)
                    # 继续
                    import argparse
                    parser = argparse.ArgumentParser(description='sovits4 inference')
                    if not clean_names_ls is None:
                        if not trans_num is None:
                            if not spk_list_ls is None:
                                if not slice_db_num is None:
                                    # 判断非必填项是否填写,若未填写则填写默认值
                                    if output_file_type is None:
                                        output_file_type = 'wav'
                                    if noice_scale is None:
                                        noice_scale = float(0.4)
                                    if pad_seconds is None:
                                        pad_seconds = float(0.5)
                                    if cluster_model_path is None:
                                        cluster_model_path = 'logs/44k/10000.pt'
                                    if cluster_infer_ratio is None:
                                        cluster_infer_ratio = float(0)
                                    if auto_predict_f0 is None:
                                        auto_predict_f0 = False

                                    # 转换
                                    trans = (list(map(int, str(trans_num))))
                                    spk_list = spk_list_ls.split(',')  # 按逗号分割多说话人
                                    clean_names = clean_names_ls.split(',')  # 按逗号分割多wav文件

                                    # 推理前设置
                                    parser.add_argument('-m', '--model_path', type=str, default=str(model_path))
                                    parser.add_argument('-c', '--config_path', type=str, default=str(json_path))
                                    parser.add_argument('-n', '--clean_names', type=str, nargs='+', default=clean_names)
                                    parser.add_argument('-t', '--trans', type=int, nargs='+', default=trans, )
                                    parser.add_argument('-s', '--spk_list', type=str, nargs='+', default=spk_list)
                                    parser.add_argument('-a', '--auto_predict_f0', action='store_true',
                                                        default=auto_predict_f0)
                                    parser.add_argument('-cm', '--cluster_model_path', type=str,
                                                        default=cluster_model_path)
                                    parser.add_argument('-cr', '--cluster_infer_ratio', type=float,
                                                        default=cluster_infer_ratio)
                                    parser.add_argument('-sd', '--slice_db', type=int, default=int(slice_db_num))
                                    parser.add_argument('-d', '--device', type=str, default=None)
                                    parser.add_argument('-ns', '--noice_scale', type=float, default=noice_scale)
                                    parser.add_argument('-p', '--pad_seconds', type=float, default=pad_seconds)
                                    parser.add_argument('-wf', '--wav_format', type=str, default=output_file_type)
                                    args = parser.parse_args()
                                    svc_model = Svc(args.model_path, args.config_path, args.device,
                                                    args.cluster_model_path)
                                    infer_tool.mkdir(["raw", "results"])
                                    clean_names = args.clean_names
                                    trans = args.trans
                                    spk_list = args.spk_list
                                    slice_db = args.slice_db
                                    wav_format = args.wav_format
                                    auto_predict_f0 = args.auto_predict_f0
                                    cluster_infer_ratio = args.cluster_infer_ratio
                                    noice_scale = args.noice_scale
                                    pad_seconds = args.pad_seconds

                                    infer_tool.fill_a_to_b(trans, clean_names)
                                    for clean_name, tran in zip(clean_names, trans):
                                        raw_audio_path = f"raw/{clean_name}"
                                        if "." not in raw_audio_path:
                                            raw_audio_path += ".wav"
                                        infer_tool.format_wav(raw_audio_path)
                                        wav_path = Path(raw_audio_path).with_suffix('.wav')
                                        chunks = slicer.cut(wav_path, db_thresh=slice_db)
                                        audio_data, audio_sr = slicer.chunks2audio(wav_path, chunks)

                                        for spk in spk_list:
                                            audio = []
                                            for (slice_tag, data) in audio_data:
                                                print(f'#=====分段起点, {round(len(data) / audio_sr, 3)}s======')

                                                length = int(np.ceil(len(data) / audio_sr * svc_model.target_sample))
                                                if slice_tag:
                                                    print('SovitsBox:跳过空段')
                                                    _audio = np.zeros(length)
                                                else:
                                                    # padd
                                                    pad_len = int(audio_sr * pad_seconds)
                                                    data = np.concatenate(
                                                        [np.zeros([pad_len]), data, np.zeros([pad_len])])
                                                    raw_path = io.BytesIO()
                                                    soundfile.write(raw_path, data, audio_sr, format="wav")
                                                    raw_path.seek(0)
                                                    out_audio, out_sr = svc_model.infer(spk, tran, raw_path,
                                                                                        cluster_infer_ratio=cluster_infer_ratio,
                                                                                        auto_predict_f0=auto_predict_f0,
                                                                                        noice_scale=noice_scale
                                                                                        )
                                                    _audio = out_audio.cpu().numpy()
                                                    pad_len = int(svc_model.target_sample * pad_seconds)
                                                    _audio = _audio[pad_len:-pad_len]

                                                audio.extend(list(infer_tool.pad_array(_audio, length)))
                                            key = "auto" if auto_predict_f0 else f"{tran}key"
                                            cluster_name = "" if cluster_infer_ratio == 0 else f"_{cluster_infer_ratio}"
                                            res_path = f'./results/{clean_name}_{key}_{spk}{cluster_name}.{wav_format}'
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
                else:
                    return jsonify({'JsonFileError': '目标文件不存在/非json文件'}), 800
            else:
                return jsonify({'Error': '不是有效的参数'}), 801
        else:
            return jsonify({'Error': '不是有效的参数'}), 801
    except Exception as e:
        # 如果发生错误，返回异常信息
        print("服务端:Python发生错误：" + str(e))
        return jsonify({'PythonError': str(e)}), 800


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=65504)  # 默认走65504端口，3.0走65503端口
