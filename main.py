"""
BIO标注工具主程序
基于tkinter的文本标注工具，支持将标注结果导出为BIO格式
"""
import os
import tkinter as tk
from tkinter import Frame, Text, Scrollbar, Button, filedialog, messagebox
from config import LABEL_CONFIG, WINDOW_CONFIG
from bio_annotator import BioAnnotator


class BioAnnotatorApp:
    """BIO标注工具主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.root = tk.Tk()
        self.root.title("NER标注工具")
        
        # 创建文本编辑区域
        self.text_widget = self._create_text_widget()
        
        # 创建标注器
        self.annotator = BioAnnotator(self.text_widget)
        
        # 创建按钮区域
        self.button_frame = self._create_button_frame()
        
        # 创建按钮
        self._create_buttons()
    
    def _create_text_widget(self) -> Text:
        """
        创建文本编辑组件
        
        Returns:
            配置好的Text组件
        """
        text = Text(
            self.root,
            width=WINDOW_CONFIG['text_width'],
            height=WINDOW_CONFIG['text_height'],
            font=WINDOW_CONFIG['font'],
            wrap='none'
        )
        
        # 插入默认文本
        text.insert('1.0', WINDOW_CONFIG['default_text'])
        
        # 创建垂直滚动条
        v_scroll = Scrollbar(self.root, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        v_scroll.config(command=text.yview)
        text.config(yscrollcommand=v_scroll.set)
        
        # 创建水平滚动条
        h_scroll = Scrollbar(self.root, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        h_scroll.config(command=text.xview)
        text.config(xscrollcommand=h_scroll.set)
        
        text.pack()
        
        return text
    
    def _create_button_frame(self) -> Frame:
        """
        创建按钮容器框架
        
        Returns:
            配置好的Frame组件
        """
        frame = Frame(self.root, relief=tk.RAISED, borderwidth=2)
        frame.pack(side=tk.TOP, fill=tk.BOTH, ipadx=5, ipady=5, expand=1)
        return frame
    
    def _create_buttons(self) -> None:
        """创建所有标注按钮"""
        # 第一排：清除标注按钮
        clear_config = LABEL_CONFIG[0]
        clear_color = clear_config[0].lower()
        clear_button = Button(
            self.button_frame,
            text=clear_config[1],
            command=lambda: self.annotator.annotate_selection(clear_config[0]),
            bg=clear_color if clear_color != 'white' else 'lightgray'
        )
        clear_button.grid(row=0, column=0, padx=10, pady=5)
        
        # 第二排：清除所有匹配的标注按钮（根据当前选中文本，清除全文中所有匹配位置的标注）
        clear_all_button = Button(
            self.button_frame,
            text="清除全文匹配",
            command=lambda: self.annotator.annotate_all_matches('white'),
            bg='lightgray'
        )
        clear_all_button.grid(row=1, column=0, padx=10, pady=5)
        
        # 第一排：各标签的单一标注按钮
        # 第二排：各标签的全标注按钮
        for i in range(1, len(LABEL_CONFIG)):
            color, label_name, _ = LABEL_CONFIG[i]
            # 将颜色名称转换为小写，确保tkinter能识别
            bg_color = color.lower()
            # 对于深色背景，设置浅色文字
            fg_color = 'white' if bg_color in ['black', 'blue', 'red', 'brown', 'purple'] else 'black'
            
            # 单一标注按钮
            single_button = Button(
                self.button_frame,
                text=label_name,
                command=lambda c=color: self.annotator.annotate_selection(c),
                bg=bg_color,
                fg=fg_color
            )
            single_button.grid(row=0, column=i, padx=10, pady=5)
            
            # 全标注按钮
            all_label_button = Button(
                self.button_frame,
                text=f"{label_name}全标注",
                command=lambda c=color: self.annotator.annotate_all_matches(c),
                bg=bg_color,
                fg=fg_color
            )
            all_label_button.grid(row=1, column=i, padx=10, pady=5)
        
        # 导入CSV按钮
        load_button = Button(
            self.button_frame,
            text="导入CSV",
            command=self._load_csv_file,
            bg='lightgreen'
        )
        load_button.grid(row=0, column=len(LABEL_CONFIG), padx=10, pady=5)
        
        # 保存按钮
        save_button = Button(
            self.button_frame,
            text="保存文件为CSV",
            command=self._save_csv_file,
            bg='lightblue'
        )
        save_button.grid(row=1, column=len(LABEL_CONFIG), padx=10, pady=5)
    
    def _load_csv_file(self) -> None:
        """打开文件选择对话框并加载CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if file_path:
            success, error_msg = self.annotator.load_from_csv(file_path)
            if not success:
                messagebox.showerror("错误", error_msg or "加载CSV文件失败，请检查文件格式")
            else:
                messagebox.showinfo("成功", f"成功加载CSV文件：{file_path}")
    
    def _save_csv_file(self) -> None:
        """打开保存对话框，选择保存路径和文件名"""
        # 确保默认保存目录存在
        os.makedirs("result", exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            title="保存标注结果为CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialdir=os.path.abspath("result"),
            initialfile="ner_result.csv"
        )

        if not file_path:
            return

        try:
            self.annotator.save_to_bio(file_path)
            messagebox.showinfo("成功", f"标注结果已保存到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败：{e}")
    
    def run(self) -> None:
        """运行应用主循环"""
        self.root.mainloop()

def main():
    """主函数"""
    app = BioAnnotatorApp()
    app.run()


if __name__ == '__main__':
    main()
