# ====================
# 一键包作者:Wangs_official https://space.bilibili.com/2128949940
# 您不得用Sovits推理违法违规的内容，产生的一切问题与一键包制作者和Sovits作者无关
# 加入了colorama库
from colorama import Fore,Back,Style
# ====================

print('====================')
print('欢迎使用SO-VITS-SVC3.0推理一键包 '
      '\n一键包作者:Wangs_official https://space.bilibili.com/2128949940 '
      '\n注意：您不得用Sovits推理违法违规的内容，产生的一切问题与一键包制作者和Sovits作者无关 ')
print('====================')
print(Fore.BLUE + '\n[!]正在加载库文件 '
      '\n[?]如果提示ModuleNotFoundError，如：ModuleNotFoundError: No module named \'librosa\' 请 pip(3) install librosa (其他库同理)')

# 引用库文件
import os
import io
import logging
import time
from pathlib import Path

import librosa
import numpy as np
import soundfile

from inference import infer_tool
from inference import slicer
from inference.infer_tool import Svc

print(Fore.GREEN + '[!]库加载完成,Sovits将自动选择CPU或GPU设备推理')

# 下载hubert文件

download_hubert_file = input(Fore.WHITE + '[?]是否需要下载hubert文件? 需要下载请回答1 无需下载回答任意数字 :')
if download_hubert_file == '1' :
    print(Fore.BLUE + '[···]正在下载')
    os.system('wget -P hubert/ https://github.com/bshall/hubert/releases/download/v0.1/hubert-soft-0d54a1f4.pt')
    print(Fore.GREEN + '[OK]下载完毕')
else:
    print(Fore.RED + '[!]无需下载,跳过此步')

# 加载模型文件以及config.json

while True:
    model_file_path = input(Fore.WHITE + '[!]请输入模型文件路径 \n ⚠ 请使用Sovits3.0训练出的模型,使用4.0模型会导致推理不出声音 \n 输入路径(拖进来也可以):')
    if os.path.isfile(model_file_path) and model_file_path.endswith('pth'): # 验证文件路径以及后缀名
        print(Fore.GREEN + '[OK]文件存在,模型文件路径:' + model_file_path)
        break
    else:
        print(Fore.RED + '[ERROR]文件不存在或导入了非.pth后缀的文件')

while True:
    config_file_path = input(Fore.WHITE + '[!]请输入Config.json路径 \n 输入路径(拖进来也可以):')
    if os.path.isfile(config_file_path) and config_file_path.endswith('json'): # 验证文件路径以及后缀名
        print(Fore.GREEN + '[OK]文件存在,Config文件路径:' + config_file_path)
        break
    else:
        print(Fore.RED + '[ERROR]文件不存在或导入了非.json后缀的文件')

print(Fore.BLUE + '[···]正在加载模型')
svc_model = Svc(model_file_path, config_file_path) # 加载模型
infer_tool.mkdir(["raw", "results"]) # 创建文件夹
print(Fore.GREEN + '[OK]加载模型成功!')

# 推理前设置

# 设置干声路径

clean_names_ls = input(Fore.WHITE + '[!]输入干声路径 \n 支持多个wav文件,请将其放入raw文件夹内 \n 多文件使用空格隔开 无需输入文件扩展名 \n 输入:')
clean_names = clean_names_ls.split()
print(Fore.GREEN + "[OK]这是您所加载的干声文件(列表形式):" + str(clean_names))

# 设置音高偏差

trans_num = input(Fore.WHITE + '[!]音高调整，支持正（半音）, 输入减号会报错我也不知道为什么(wssb) \n 请输入调整半音,无需调整请输入0:')
trans = (list(map(int,str(trans_num))))
print(Fore.GREEN + "[OK]调整的半音数:" + str(trans))

# 设置说话人

spk_list_ls = input(Fore.WHITE + "[!]输入说话人 \n 每次同时合成多语者音色 \n 多说话人使用空格隔开 \n 输入:")
spk_list = spk_list_ls.split()
print(Fore.GREEN + "[OK]这是说话人列表(列表形式):" + str(spk_list))

# 设置slice_db

slice_db = float(input(Fore.WHITE + '[!]设置slice_db \n 嘈杂的音频可以-30，干声保留呼吸可以-50 , 无需调整请输入-40:'))
print(Fore.GREEN + "[OK]slice_db为:" + str(slice_db))

wav_format = 'wav'  # 音频输出格式
print(Fore.GREEN + "[OK]音频输出格式默认为Wav格式")

# 打印设置列表
print('====================')
print('推理前设置列表')
print('加载干声文件列表:' + str(clean_names))
print('说话人列表:' + str(spk_list))
print('调整的半音数:' + str(trans))
print('slice_db:' + str(slice_db))
print('====================')
input("[!]按回车开始推理")

#推理(照搬了)

infer_tool.fill_a_to_b(trans, clean_names)
for clean_name, tran in zip(clean_names, trans):
    raw_audio_path = f"raw/{clean_name}"
    if "." not in raw_audio_path:
        raw_audio_path += ".wav"
    infer_tool.format_wav(raw_audio_path)
    wav_path = Path(raw_audio_path).with_suffix('.wav')
    chunks = slicer.cut(wav_path, db_thresh=slice_db)
    audio_data, audio_sr = slicer.chunks2audio(wav_path, chunks)
    print(Fore.BLUE + '[···]正在推理')
    for spk in spk_list:
        audio = []
        for (slice_tag, data) in audio_data:
            print(f'#=====推理中, {round(len(data) / audio_sr, 3)}s======')
            length = int(np.ceil(len(data) / audio_sr * svc_model.target_sample))
            raw_path = io.BytesIO()
            soundfile.write(raw_path, data, audio_sr, format="wav")
            raw_path.seek(0)
            if slice_tag:
                print('jump empty segment')
                _audio = np.zeros(length)
            else:
                out_audio, out_sr = svc_model.infer(spk, tran, raw_path)
                _audio = out_audio.cpu().numpy()
            audio.extend(list(_audio))

        res_path = f'./results/{clean_name}_{tran}key_{spk}.{wav_format}'
        soundfile.write(res_path, audio, svc_model.target_sample, format=wav_format)

input(Fore.GREEN + "[OK]推理成功!感谢使用该脚本,喜欢的话请给一个Star^_^ \n 一键包作者:Wangs_official https://space.bilibili.com/2128949940 \n 按回车退出程序")
exit()
