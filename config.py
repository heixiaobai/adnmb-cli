import os
import json

path = os.path.dirname(os.path.realpath(__file__))
c_path = path+"/config/"

theme = {
    'post_info': [9, 15, 30, 42]
}

# 从配置文件获取配置信息
with open(c_path+"config.json", 'r') as f:
    config_info = json.loads(f.read())


# 初始化状态控制变量
control_info = {
    "pad_browse_height": 500,
    "pad_info_height": 1,
    "pad_control_height": 1,
    "input_command_info": "",
    "input_command_char": [],
    "address": "",
    "back_list": [],
    "location": [None, None, None, None]
}

# 读取配色方案
with open(c_path+"color/"+config_info["color_file"], "r") as f:
    color_info = json.loads(f.read())


