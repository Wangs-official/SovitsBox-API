<center>
<img src = 'https://s3.bmp.ovh/imgs/2023/07/21/a43006f865b8eaf7.png' >
<h2>欢迎使用SovitsBox</h2>
<h3>SovitsBox服务端文档（SovitsBoxAPI）</h3>
</center>


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

均使用GET方式请求，请求地址：

- Sovits3.0服务端 127.0.0.1:65503
- Sovits4.0服务端 127.0.0.1:65504

1. 状态

用于检测服务端是否启动

请求地址 `/`

参数：无

正常返回值：

|  KEY   | VALUE |  TYPE  | 兼容性  |
| :----: | :---: | :----: | :-----: |
| status | 状态  | string | 3.0/4.0 |



2. 下载hubert模型文件

用于下载Hubert模型文件

请求地址`/download_hubert`

参数：

|   KEY    | VALUE | TYPE | 兼容性  | 是否必选 |
| :------: | :---: | :--: | :-----: | :------: |
| download | true  | bool | 3.0/4.0 |    是    |

例子：`127.0.0.1:65503/download_hubert?download=true`

返回值

正常返回值：

|       KEY       | VALUE |  TYPE  | 兼容性  |
| :-------------: | :---: | :----: | :-----: |
| download_status |  OK   | string | 3.0/4.0 |

异常返回值：

|     KEY     |        VALUE         |  TYPE  | 兼容性  |
| :---------: | :------------------: | :----: | :-----: |
| PythonError | `Python执行错误返回` | string | 3.0/4.0 |



3. 加载模型

请先加载模型再进行推理！

请求地址 `/loadmodel`

参数：

|    KEY     |       VALUE       |  TYPE  | 兼容性  | 是否必选 |
| :--------: | :---------------: | :----: | :-----: | :------: |
| model_path |    `模型路径`     | string | 3.0/4.0 |    是    |
| json_path  | `config.json路径` | string | 3.0/4.0 |    是    |

例子：`127.0.0.1:65503/loadmodel?model_path=/example/example.pth&json_path=/example/config.json`

返回值

正常返回值：

|    KEY     |    VALUE     |  TYPE  | 兼容性  |
| :--------: | :----------: | :----: | :-----: |
|   status   |      OK      | string | 3.0/4.0 |
| speaker_ls | `说话人列表` | string | 3.0/4.0 |

异常返回值：

|         KEY         |                            VALUE                             |  TYPE  | 兼容性  |
| :-----------------: | :----------------------------------------------------------: | :----: | :-----: |
|     PythonError     |                     `Python执行错误返回`                     | string | 3.0/4.0 |
| HubertNotFoundError | hubert模型不存在，请访问URL：http://127.0.0.1:65503/download_hubert?download=true 下载 | string |   3.0   |
| HubertNotFoundError | hubert模型不存在，请访问URL：http://127.0.0.1:65504/download_hubert?download=true 下载 | string |   4.0   |
|      FileError      |                        `文件错误返回`                        | string | 3.0/4.0 |
|        Error        |                        `通用错误返回`                        | String | 3.0/4.0 |

4. 删除raw/results文件夹内的所有文件

我感觉小白不会删文件所以就写了这个接口

请求地址 `/delete_file`

参数：

| KEY  |    VALUE    |  TYPE  | 兼容性  | 是否必选 |
| :--: | :---------: | :----: | :-----: | :------: |
| del  | raw/results | string | 3.0/4.0 |    是    |

例子`127.0.0.1:65503/delete_file?del=raw`

返回值

正常返回值：

|   KEY    |    VALUE    |  TYPE  | 兼容性  |
| :------: | :---------: | :----: | :-----: |
|  status  |     OK      | string | 3.0/4.0 |
| del_path | raw/results | string | 3.0/4.0 |

异常返回值：

|     KEY     |        VALUE         |  TYPE  | 兼容性  |
| :---------: | :------------------: | :----: | :-----: |
| PythonError | `Python执行错误返回` | string | 3.0/4.0 |
|    Error    |    不是有效的参数    | string | 3.0/4.0 |

5.  上传wav文件到raw目录

没用

请求地址 `/upload_wav`

参数：

|   KEY    |     VALUE     |  TYPE  | 兼容性  | 是否必选 |
| :------: | :-----------: | :----: | :-----: | :------: |
| wav_path | `wav文件路径` | string | 3.0/4.0 |    是    |

例子`127.0.0.1:65503/upload_wav?wav_path=example/aaa.wav`

返回值

正常返回值：

|       KEY        |        VALUE        |  TYPE  | 兼容性  |
| :--------------: | :-----------------: | :----: | :-----: |
|      status      |         OK          | string | 3.0/4.0 |
| upload_file_path | `上传的wav文件路径` | string | 3.0/4.0 |

异常返回值：

|     KEY     |          VALUE           |  TYPE  | 兼容性  |
| :---------: | :----------------------: | :----: | :-----: |
| PythonError |   `Python执行错误返回`   | string | 3.0/4.0 |
|    Error    |      不是有效的参数      | string | 3.0/4.0 |
|  FileError  | 目标文件不存在/非wav文件 | String | 3.0/4.0 |

## 开发中...