"""
BIO标注工具核心模块
提供文本标注和BIO格式转换功能
"""
import re
import csv
import os
from datetime import datetime
from typing import List, Tuple, Optional
from tkinter import Text, END
from config import LABEL_CONFIG, OUTPUT_CONFIG


class BioAnnotator:
    """BIO标注器类，负责处理文本标注和BIO格式转换"""
    
    def __init__(self, text_widget: Text):
        """
        初始化标注器
        
        Args:
            text_widget: tkinter Text组件，用于显示和编辑文本
        """
        self.text_widget = text_widget
        self.color_list = [config[0] for config in LABEL_CONFIG]
        self._initialize_tags()
    
    def _initialize_tags(self) -> None:
        """初始化所有标签的样式配置"""
        for color in self.color_list:
            self.text_widget.tag_config(color, background=color)
    
    def annotate_selection(self, color: str) -> None:
        """
        对选中的文本进行单一标注
        
        Args:
            color: 标签对应的颜色
        """
        try:
            if not self.text_widget.tag_ranges("sel"):
                return
            
            start_pos = self.text_widget.index("sel.first")
            end_pos = self.text_widget.index("sel.last")
            
            # 先移除该区域的所有其他标签
            self._remove_tags_from_range(start_pos, end_pos)
            
            # 如果不是白色（清除标签），则添加新标签
            if color != 'white':
                self.text_widget.tag_add(color, start_pos, end_pos)
        except Exception as e:
            print(f"标注失败: {e}")
    
    def annotate_all_matches(self, color: str) -> None:
        """
        对全文所有匹配选中文本的位置进行标注
        
        Args:
            color: 标签对应的颜色
        """
        try:
            if not self.text_widget.tag_ranges("sel"):
                return
            
            start_pos = self.text_widget.index("sel.first")
            end_pos = self.text_widget.index("sel.last")
            selected_text = self.text_widget.get(start_pos, end_pos)
            
            if not selected_text.strip():
                return
            
            # 获取所有文本
            all_text = self.text_widget.get('1.0', END)
            lines = all_text.split('\n')
            
            # 找到所有匹配位置
            positions = self._find_all_positions(lines, selected_text)
            
            # 应用标签到所有匹配位置
            for start, end in positions:
                self._remove_tags_from_range(start, end)
                if color != 'white':
                    self.text_widget.tag_add(color, start, end)
        except Exception as e:
            print(f"全标注失败: {e}")
    
    def _remove_tags_from_range(self, start_pos: str, end_pos: str) -> None:
        """
        从指定范围移除所有标签
        
        Args:
            start_pos: 起始位置
            end_pos: 结束位置
        """
        for color in self.color_list:
            self.text_widget.tag_remove(color, start_pos, end_pos)
    
    def _find_all_positions(self, lines: List[str], search_text: str) -> List[Tuple[str, str]]:
        """
        在所有行中查找文本的所有出现位置
        
        Args:
            lines: 文本行列表
            search_text: 要搜索的文本
            
        Returns:
            位置列表，每个元素为 (起始位置, 结束位置) 的元组
        """
        positions = []
        escaped_text = re.escape(search_text)
        
        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(escaped_text, line):
                col_start = match.start()
                col_end = match.end()
                start_pos = f'{line_num}.{col_start}'
                end_pos = f'{line_num}.{col_end}'
                positions.append((start_pos, end_pos))
        
        return positions
    
    
    def save_to_bio(self, output_file: Optional[str] = None) -> None:
        """
        将标注结果保存为CSV格式文件
        第一列为原始文本，第二列为BIO标签序列（空格分隔）
        
        Args:
            output_file: 输出文件路径，如果为None则自动生成基于时间戳的文件名
        """
        if output_file is None:
            # 生成基于时间戳的文件名：年-月-日-小时-分钟-秒.csv
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            output_file = f'result/{timestamp}.csv'
            
            # 确保result文件夹存在
            os.makedirs('result', exist_ok=True)
        
        print("开始获取文本并处理...")
        
        # 获取所有文本内容
        all_text = self.text_widget.get("1.0", "end")
        lines = all_text.split('\n')
        
        # 移除最后一个空行（如果存在）
        if lines and lines[-1] == '':
            lines = lines[:-1]
        
        # 初始化结果：每行都是'O'标签
        result = [list('O' * len(line)) for line in lines]
        
        # 处理每个标签（跳过第一个清除标签）
        for label_index in range(1, len(LABEL_CONFIG)):
            color = LABEL_CONFIG[label_index][0]
            bio_tag_name = LABEL_CONFIG[label_index][2] or LABEL_CONFIG[label_index][1].upper()
            
            tag_ranges = self.text_widget.tag_ranges(color)
            
            # 处理每个标注区域
            for range_idx in range(0, len(tag_ranges), 2):
                if range_idx + 1 >= len(tag_ranges):
                    break
                
                start_index = tag_ranges[range_idx].string
                end_index = tag_ranges[range_idx + 1].string
                
                try:
                    start_row, start_col = map(int, start_index.split('.'))
                    end_row, end_col = map(int, end_index.split('.'))
                except ValueError:
                    print(f"警告：无法解析位置 {start_index} 或 {end_index}")
                    continue
                
                # 检查是否跨行
                if start_row != end_row:
                    print(f"警告：标注跨行！位置：{start_row}.{start_col} 到 {end_row}.{end_col}")
                    continue
                
                # 转换为0-based索引
                row_idx = start_row - 1
                
                # 检查索引有效性
                if row_idx < 0 or row_idx >= len(result):
                    continue
                
                if start_col >= len(result[row_idx]) or end_col > len(result[row_idx]):
                    continue
                
                # 应用BIO标签
                self._apply_bio_tags(result[row_idx], start_col, end_col, bio_tag_name)
        
        # 保存为CSV格式：第一列为原始文本，第二列为BIO标签序列（空格分隔）
        with open(output_file, 'w', encoding=OUTPUT_CONFIG['encoding'], newline='') as f:
            writer = csv.writer(f)
            # 写入列名
            writer.writerow(['文本', '标签'])
            # 写入数据行
            for line_idx, line_text in enumerate(lines):
                if line_idx < len(result):
                    # 第一列：原始文本
                    # 第二列：BIO标签序列（空格分隔）
                    bio_tags = ' '.join(result[line_idx])
                    writer.writerow([line_text, bio_tags])
        
        print(f"保存完成！共处理 {len(lines)} 行，已保存到 {output_file}")
    
    @staticmethod
    def _apply_bio_tags(line: List[str], start_col: int, end_col: int, tag_name: str) -> None:
        """
        在指定行的指定列范围应用BIO标签
        
        Args:
            line: 当前行的标签列表
            start_col: 起始列（包含）
            end_col: 结束列（不包含）
            tag_name: BIO标签名称
        """
        length = end_col - start_col
        
        if length == 1:
            # 单字符：S-tag
            line[start_col] = f"S-{tag_name}"
        else:
            # 多字符：B-tag, I-tag, ..., E-tag
            line[start_col] = f"B-{tag_name}"
            for col in range(start_col + 1, end_col - 1):
                line[col] = f"I-{tag_name}"
            line[end_col - 1] = f"E-{tag_name}"
    
    def load_from_csv(self, csv_file: str) -> Tuple[bool, str]:
        """
        从CSV文件加载文本和标注结果
        支持UTF-8和GBK编码格式，自动检测编码
        
        Args:
            csv_file: CSV文件路径
            
        Returns:
            Tuple[bool, str]: (是否成功加载, 错误信息)
        """
        # 尝试的编码列表：先尝试UTF-8，再尝试GBK
        encodings = ['utf-8', 'gbk', 'gb2312']
        file_encoding = None
        
        # 尝试使用不同的编码打开文件
        for encoding in encodings:
            try:
                # 先尝试打开文件并读取第一行来验证编码
                with open(csv_file, 'r', encoding=encoding) as f:
                    # 尝试读取前几行来验证编码是否正确
                    sample = f.read(1024)
                    f.seek(0)
                    # 如果能够成功读取，说明编码正确
                    file_encoding = encoding
                    break
            except UnicodeDecodeError:
                # 编码不匹配，尝试下一个
                continue
            except Exception as e:
                # 如果是其他错误（如文件不存在），直接抛出
                if isinstance(e, FileNotFoundError):
                    raise
                continue
        
        if file_encoding is None:
            error_msg = f"无法读取文件，已尝试编码：{', '.join(encodings)}"
            print(f"错误：{error_msg}")
            return False, error_msg
        
        try:
            with open(csv_file, 'r', encoding=file_encoding) as f:
                reader = csv.DictReader(f)
                
                # 检查列名
                if '文本' not in reader.fieldnames:
                    error_msg = "CSV文件中没有找到'文本'列"
                    print(f"错误：{error_msg}")
                    return False, error_msg
                
                if '标签' not in reader.fieldnames:
                    error_msg = "CSV文件中没有找到'标签'列，请重新导入"
                    print(f"错误：{error_msg}")
                    return False, error_msg
                
                # 读取所有数据
                rows = list(reader)
                
                if not rows:
                    error_msg = "CSV文件中没有数据"
                    print(f"警告：{error_msg}")
                    return False, error_msg
                
                # 清空当前文本
                self.text_widget.delete('1.0', END)
                
                # 创建BIO标签到颜色的映射
                bio_to_color = {}
                for label_index in range(1, len(LABEL_CONFIG)):
                    color = LABEL_CONFIG[label_index][0]
                    bio_tag_name = LABEL_CONFIG[label_index][2] or LABEL_CONFIG[label_index][1].upper()
                    bio_to_color[bio_tag_name] = color
                
                # 处理每一行数据
                all_lines = []
                all_tags = []
                
                for row in rows:
                    text = row['文本'].strip()
                    tags_str = row['标签'].strip()
                    
                    if not text:
                        continue
                    
                    # 判断CSV格式：如果标签是空格分隔的序列，则是行级格式
                    tags = tags_str.split() if tags_str else []
                    
                    if len(tags) == len(text):
                        # 行级格式：文本和标签数量相等
                        all_lines.append(text)
                        all_tags.append(tags)
                    elif len(tags) == 1 and len(text) == 1:
                        # 字符级格式：每行一个字符
                        if not all_lines:
                            # 开始第一行
                            all_lines.append(text)
                            all_tags.append([tags_str])
                        elif text == '' or text == '\n':
                            # 空字符表示行结束，开始新行
                            all_lines.append('')
                            all_tags.append([])
                        else:
                            # 继续当前行
                            all_lines[-1] += text
                            all_tags[-1].append(tags_str)
                    else:
                        # 格式不匹配，跳过
                        # print(f"警告：跳过格式不匹配的行：文本长度={len(text)}, 标签数量={len(tags)}")
                        # continue
                        #如果长度不等，则全部改成O
                        all_lines.append(text)
                        all_tags.append(['O' * len(text)])
                
                # 显示文本并应用标注
                for line_idx, (line_text, line_tags) in enumerate(zip(all_lines, all_tags)):
                    if line_idx > 0:
                        self.text_widget.insert(END, '\n')
                    
                    # 插入文本
                    self.text_widget.insert(END, line_text)
                    
                    # 应用标注：找到所有连续的实体并应用颜色
                    line_num = line_idx + 1
                    i = 0
                    
                    while i < len(line_tags):
                        tag = line_tags[i]
                        
                        # 解析BIO标签
                        if tag == 'O':
                            i += 1
                            continue
                        
                        # 提取标签名称（如 B-VOLTAGE -> VOLTAGE）
                        if '-' in tag:
                            prefix, tag_name = tag.split('-', 1)
                            
                            # 找到对应的颜色
                            if tag_name in bio_to_color:
                                color = bio_to_color[tag_name]
                                
                                # 找到这个实体的起始和结束位置
                                if prefix == 'B' or prefix == 'S':
                                    # 开始一个新实体
                                    start_char = i
                                    end_char = i + 1
                                    
                                    if prefix == 'B':
                                        # B标签，继续查找I和E标签
                                        j = i + 1
                                        while j < len(line_tags):
                                            next_tag = line_tags[j]
                                            if next_tag == f'I-{tag_name}':
                                                end_char = j + 1
                                                j += 1
                                            elif next_tag == f'E-{tag_name}':
                                                end_char = j + 1
                                                j += 1
                                                break
                                            else:
                                                break
                                        i = j
                                    else:
                                        # S标签，单字符实体
                                        i += 1
                                    
                                    # 应用颜色标注
                                    start_index = f'{line_num}.{start_char}'
                                    end_index = f'{line_num}.{end_char}'
                                    self.text_widget.tag_add(color, start_index, end_index)
                                else:
                                    # I或E标签，应该已经被B标签处理了，跳过
                                    i += 1
                            else:
                                # 未找到对应的标签
                                i += 1
                        else:
                            i += 1
                
                print(f"成功加载CSV文件：{csv_file}（编码：{file_encoding}），共 {len(all_lines)} 行")
                return True, ""
                
        except FileNotFoundError:
            error_msg = f"找不到文件：{csv_file}"
            print(f"错误：{error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"加载CSV文件时出错：{str(e)}"
            print(f"错误：{error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg

