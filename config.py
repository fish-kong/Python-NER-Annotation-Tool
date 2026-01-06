"""
配置文件模块
定义标注工具的颜色和标签配置
"""
from typing import List, Tuple

# 标签配置：每个标签包含 [颜色, 标签名称, BIO标签名称]
# 颜色：用于界面显示的背景色
# 标签名称：按钮上显示的文本
# BIO标签名称：保存到BIO文件时使用的标签名（如果为None，则使用标签名称的大写形式）
LABEL_CONFIG: List[Tuple[str, str, str]] = [
    ('white', '清除选中标注', None),  # 清除标签，不生成BIO标签
    ('red',   '电压等级', 'VOLTAGE'),
    ('yellow','一级间隔', 'INTERVAL_1'),
    ('magenta',  '二级间隔', 'INTERVAL_2'),
    ('Cyan',  '支路间隔', 'BRANCH'),
    ('Lime',  '编号设备', 'DEVICE_ID'),
    ('pink', '装置类型', 'DEVICE_TYPE'),
    ('green', '套数',     'SET_COUNT'),
    ('orange','装置型号', 'DEVICE_MODEL'),
    ('purple','原子事件', 'ATOMIC_EVENT'),
    ('brown', '补充描述', 'DESCRIPTION'),

]

# 界面配置
WINDOW_CONFIG = {
    'text_width': 100,
    'text_height': 30,
    'font': ('宋体', 15),
    'default_text': '贴入你要处理的文字 中文 English 都行\n贴入你要处理的文字',
}

# 输出配置
OUTPUT_CONFIG = {
    'encoding': 'utf-8',  # 输出文件的编码格式
}

