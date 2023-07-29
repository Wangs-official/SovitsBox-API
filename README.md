<div align="center">
<img src = 'https://s3.bmp.ovh/imgs/2023/07/21/a43006f865b8eaf7.png' >
<h2>欢迎使用SovitsBox</h2>
<h3>SovitsBox服务端文档（SovitsBoxAPI）</h3>
<img src = 'https://img.shields.io/badge/%E5%BC%80%E6%BA%90%E8%AE%B8%E5%8F%AF%E8%AF%81-MIT-blue'>
  <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/wangs-official/sovitsbox-api">

</div>




## 简介

SovitsBox——让小白也会推理Sovits模型

SovitsBox分为服务端（SovitsBoxAPI）以及客户端（SovitsBoxAPP）。原理类似于网络API

## 前期准备

1. 克隆存储库

还可以下载zip，看你心情

下载zip用不了更新功能

`git clone https://github.com/wangs-official/sovitsbox-api.git`

2. 安装库

建议您先创建一个Conda环境（怎么创建自己搜）防止库冲突出现问题

然后，切换到conda环境内，并cd到Sovits根目录，执行该命令安装库

`pip3 install -r requirements.txt `

> 注意：pip可能会出现找不到版本的问题，请尝试更换pip源（阿里源，华为源等）

安装后，若要使用Sovits3.0版本的服务端，请在终端执行`cd v3` 后 `python app.py`

同样的，若要使用Sovits4.0版本的服务端，请在终端执行`cd v4` 后 `python app.py`

> 若报错ModuleNotFoundError，请使用`pip3 install xxx`安装缺失的库

## 快速更新

在根目录执行 `python update.py`来更新，请勿更改 update/ver.json 以及 update/tmp/ver.json 内的任何内容，出事不管哦

```
调用系统git pull origin命令，如果仓库不是克隆下来的话，就不要用了
请提前备份raw/results文件夹内所有内容以及hubert模型文件，丢了不管
```

## API文档

请求地址：3.0为 `127.0.0.1:65503` 4.0为 `127.0.0.1:65504`

1. 状态 (3.0/4.0)

   简要描述

   - 测试接口是否正常

   请求地址

   - `/`

   请求方式

   - GET

   参数

   无

   返回示例

   ```json
   {
     'status':'200OK'
   }
   ```

   返回参数说明

   | 参数名 |  类型  |      说明       |
   | :----: | :----: | :-------------: |
   | status | string | 返回200OK则正常 |



2. 下载Hubert模型文件 (3.0/4.0)

简要描述

- 下载Hubert模型文件

请求地址

- `/download_hubert`

请求方式

- GET

参数

|  参数名  | 必选 | 类型 |          说明          |
| :------: | :--: | :--: | :--------------------: |
| download |  是  | bool | 是否下载，若下载填true |

正常返回示例

```json
{
  'download_status': 'OK'
}
```

正常返回参数说明

|     参数名      |  类型  |     说明     |
| :-------------: | :----: | :----------: |
| download_statud | string | 返回OK则正常 |

异常返回（800）示例

```json
{
  'PythonError': 'xxx'
}
```

异常返回参数说明

|   参数名    |  类型  |         说明         |
| :---------: | :----: | :------------------: |
| PythonError | string | Python执行时发生错误 |

3. 删除raw/results文件夹内的所有文件 (3.0/4.0)

简要描述

- 我怕小白连文件都不会删

请求地址

- `/delete_file`

请求方式

- GET

参数

| 参数名 | 必选 |  类型  |        说明         |
| :----: | :--: | :----: | :-----------------: |
|  del   |  是  | string | raw/results任选其一 |

正常返回示例

```json
{
  'status': 'OK'
  'del_path': 'raw'
}
```

正常返回参数说明

|  参数名  |  类型  |       说明       |
| :------: | :----: | :--------------: |
|  status  | string |   返回OK则正常   |
| del_path | string | 删除的是哪个文件 |

异常返回（800）示例

```json
{
  'PythonError': 'xxx'
}
```

异常返回参数说明

|   参数名    |  类型  |         说明         |
| :---------: | :----: | :------------------: |
| PythonError | string | Python执行时发生错误 |

异常返回（801）：参数填写错误

4. 上传wav文件到raw文件夹 (3.0/4.0)

简要描述

- 我怕小白不会上传文件

请求地址

- `/upload_wav`

请求方式

- GET

参数

|  参数名  | 必选 |  类型  |        说明         |
| :------: | :--: | :----: | :-----------------: |
| wav_path |  是  | string | 待上传的Wav文件路径 |

返回示例

```json
{
  'status':'OK'
  'upload_file_path': '/example/eg.wav'
}
```

返回参数说明

|      参数名      |  类型  |      说明       |
| :--------------: | :----: | :-------------: |
|      status      | string | 返回200OK则正常 |
| upload_file_path | string | 上传wav文件路径 |

异常返回（800）示例

```json
{
  'PythonError': 'xxx'
}
```

异常返回参数说明

|   参数名    |  类型  |           说明           |
| :---------: | :----: | :----------------------: |
| PythonError | string |   Python执行时发生错误   |
|  FileError  | string | 目标文件不存在/非wav文件 |

异常返回（801）：参数填写错误

5. 推理 (3.0)

简要描述

- 没有

请求地址

- `/inference`

请求方式

- GET

参数

|      参数名      | 必选 |  类型  |                             说明                             |
| :--------------: | :--: | :----: | :----------------------------------------------------------: |
|  clean_names_ls  |  是  | string | 干声路径，支持多个wav文件,请将其放入raw文件夹内，多文件使用半角逗号隔开，无需输入文件扩展名 |
|    trans_num     |  是  |  int   |           音高调整，支持正（半音），无需调整填入 0           |
|   spk_list_ls    |  是  | string |                支持多说话人，使用半角逗号隔开                |
|   slice_db_num   |  是  |  int   |  嘈杂的音频可以-30，干声保留呼吸可以-50 , 无需填入请输入-40  |
| output_file_type |  否  | string |                           默认wav                            |
|    model_path    |  是  | string |                           模型路径                           |
|    json_path     |  是  | string |                       Config.json路径                        |

返回示例

```json
{
  'status': 'OK', 
  'output_wav_path': '/results/eg.wav'
}
```

返回参数说明

|     参数名      |  类型  |       说明       |
| :-------------: | :----: | :--------------: |
|     status      | string | 返回200OK则正常  |
| output_wav_path | string | 推理后的文件路径 |

异常返回（800）示例

```json
{
  'PythonError': 'xxx'
}
```

异常返回参数说明

|    参数名     |  类型  |           说明            |
| :-----------: | :----: | :-----------------------: |
|  PythonError  | string |   Python执行时发生错误    |
| PthFileError  | string | 目标文件不存在/非pth文件  |
| JsonFileError | string | 目标文件不存在/非json文件 |

异常返回（801）：参数填写错误

## 使用前提示/用户协议

### 使用前提示

SovitsBoxAPI（SovitsBox服务端）仅面向于高级用户使用，若您是小白，请使用SovitsBox。若已知自己没有使用API基础仍要使用，请在遇到问题时自己百度/Google/Bing，我们不予解决任何非程序问题。

请善用Issues功能，在发起Issues前请务必确认该问题是一个有价值的问题，否则不予解答

关于贡献问题，请看下方

### 用户协议

本用户协议（以下简称“协议”）是由SovitsBoxAPI/SovitsBoxAPP制作者（以下简称“我们”或“项目”）与使用本项目的用户（以下简称“您”或“用户”）之间订立的。本协议规定了您使用本项目的条款和条件。请您仔细阅读本协议，并在使用本项目之前同意遵守本协议。如果您不同意本协议，您将无法使用本项目。

1. 项目介绍

   本项目使用Python语言开发，基于SO-VITS-SVC项目。项目旨在为用户提供一种改变声音特征的工具，可以用于娱乐、教育、研究等目的。项目使用MIT许可证发布，任何人都可以在遵守许可证条款的前提下使用、复制、修改和分发项目。

2. 用户权利和义务

   - 您有权在遵守本协议和MIT许可证条款的前提下，免费使用、复制、修改和分发本项目。
   - 您有义务保护自己和他人的隐私和知识产权，不得使用本项目收集、存储、传播或泄露他人的个人信息或版权内容，除非您已获得他人的明确授权。
   - 您有义务遵守所有适用的法律法规，不得使用本项目进行非法、不道德或有害活动。这些活动包括但不限于欺诈、诽谤、骚扰、威胁、侵犯他人隐私或知识产权等。
   - 您有义务对自己使用本项目的方式和目的负全责，并承担由此产生的一切风险和后果。

3. 项目责任免除

   - 本项目是按照“现状”提供的，我们不对本项目的正确性、完整性、可靠性、安全性或适用性做出任何明示或暗示的保证或声明。
   - 我们不对任何因使用或无法使用本项目而造成的任何直接或间接的损失、损害、索赔或责任负责。
   - 我们不支持、鼓励或容忍任何使用本项目进行非法、不道德或有害活动的行为。如果我们发现或被告知您违反了本协议或任何适用的法律法规，我们不担任任何法律责任

4. 协议修改和更新

   我们有权根据我们的判断随时修改或更新本协议。我们会在我们认为合适的方式通知您任何重大变更或更新。您应定期查看本协议，以了解任何变更或更新。您继续使用本项目即表示接受本协议及其任何修订。

## 贡献

首先，感谢您对本项目的重视

由于开发时未使用统一的规定，导致了代码可读性下降等恶性问题

您可以对此项目做出优化，请继续看下方

### 文件树（展示的是对你有用的）

```
SovitsBox-API
├─ update.py（更新用程序）
├─ requirements.txt（需求库安装）
├─ README.md（README）
├─ .gitignore（基本已经搞完了）
├─ v3（V3）
│  ├─ app.py（V3的app.py）
├─ v3（V4）
│  ├─ app.py（V4的app.py）
└─ update（更新目录）
	 ├─ tmp（从Github下载的ver.json放在这里，这个文件夹不提交）
	 │  ├─ ver.json
   └─ ver.json（本地ver.json，请在每次提交前将该文件内的版本号+1 如原来0.1.11 提交前改为0.1.12）
```

### 提交标签

`[feat]`添加新功能

`[fix]`修复BUG

`[opt]`优化代码

`[dev->main]`合并dev分支到main分支

`[upd]`版本号文件更新

### 其他

请创建PR到 dev 分支而不是 main 分支

dev分支定时合并到main分支

## 后言

感谢您使用SovitsBox！

### 感谢以下贡献者

<a href="https://github.com/wangs-official/sovitsbox-api/contributors">
  <img src="https://contrib.rocks/image?repo=wangs-official/sovitsbox-api" />
</a>

