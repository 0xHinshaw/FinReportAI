import json
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from datetime import datetime
import re
from matplotlib.ticker import FormatStrFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
import math



font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
prop = FontProperties(fname=font_path)
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

def calculate_average(numbers):
    numbers = [i for i in numbers if i is not None and not math.isnan(i) and i != ""]
    return sum(numbers) / len(numbers)

def get_bar(x, y, save_path, mark=None,default_color = "#C00000",mark_color = "#FFC000",type = "bar",sort = True):
    """_summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        save_path (_type_): _description_
        mark (_type_, optional): _description_. Defaults to None.
        default_color (str, optional): _description_. Defaults to "#C00000".
        mark_color (str, optional): _description_. Defaults to "#FFC000".
        type (str, optional): _description_. Defaults to "bar".
        sort (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    width = 0.4
    spacing = 0.5
    try:
        if mark is not None:
            colors = [default_color if index != mark else mark_color for index in x]
        else:
            colors = [default_color for i in x]
        x = ['\n'.join(list(sub_x)) for sub_x in x]
        data = {
            'x': x,
            'y': y,
            'colors' : colors
        }
        x_location = np.arange(len(x)) * (width + spacing)
        df = pd.DataFrame(data)
        # 按销售量降序排序
        if sort:
            df_sorted = df.sort_values(by='y', ascending=False)
        else:
            df_sorted = df
        # 创建柱状图
        plt.figure(figsize=(8, 4))  # 设置图形的尺寸
        if type == "bar":
            plt.bar(x_location, df_sorted["y"], color=df_sorted["colors"],width=width)  # 创建柱状图，并指定颜色
        elif type == "scatter":
            plt.scatter(df_sorted["x"], df_sorted["y"],color=df_sorted["colors"])  # 创建散点图，并指定颜色
        # 添加标题和标签
        plt.title('', fontproperties=prop)
        plt.xlabel('', fontproperties=prop,labelpad=15)
        plt.ylabel('', fontproperties=prop)
        for label in plt.gca().get_xticklabels():
            label.set_fontproperties(prop)
        for label in plt.gca().get_yticklabels():
            label.set_fontproperties(prop)
        plt.xticks(x_location, df_sorted["x"])
        plt.axhline(0, color='#D9D9D9', linewidth=1.5)
        # 保存图表到文件
        # plt.xticks(rotation=90) 
        # 获取当前的Axes对象并隐藏特定的轴线
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().tick_params(axis='y',  direction='in') 
        plt.gca().tick_params(axis='x', color = "#FFFFFF", direction='in',bottom= False) 

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
    except Exception as e:
        print(f"柱状图制作遇到{e}问题")
    return plt

def get_line(x, y, save_path, default_color = "#C00000",average_color = "#FFC000",indicator="市盈率",
             x_lable = None,today = "6-19",average = False,legend = False):
    """_summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        save_path (_type_): _description_
        default_color (str, optional): _description_. Defaults to "#C00000".

    Returns:
        _type_: _description_
    """
    try:
        x_location = range(len(x))
        if x_lable is None:
            if isinstance(x[0],str):
                x_lable = [x[index] if x[index].endswith(today) else  "" for index in x_location ]
            else :
                x_lable = [x[index].strftime("%Y-%m-%d") if x[index].strftime("%Y-%m-%d").endswith(today) else  "" for index in x_location ]
        data = {
            'x': x_location,
            'y': y,
            'colors' : default_color
        }
        df = pd.DataFrame(data)
        # 按销售量降序排序
        df_sorted = df
        
        fig, ax = plt.subplots(figsize=(8, 4))  # 设置图形的尺寸
        line1, = ax.plot(df_sorted["x"], df_sorted["y"], color=default_color,label=f'{indicator}')  # 创建折线图
        line2 = ax.axhline(0, color='#D9D9D9', linewidth=1.5, )
        if average:
            line3 = ax.axhline(calculate_average(list(df_sorted["y"])), color=average_color, linewidth=1.5,label='平均值')

        # 添加标题和标签
        ax.set_title('', fontproperties=prop)
        ax.set_xlabel('', fontproperties=prop, labelpad=15)
        ax.set_ylabel('', fontproperties=prop)

        # 设置x轴和y轴标签的字体属性
        for label in ax.get_xticklabels():
            label.set_fontproperties(prop)
        for label in ax.get_yticklabels():
            label.set_fontproperties(prop)

        # 设置x轴刻度
        ax.set_xticks(x_location)
        ax.set_xticklabels(x_lable)

        # 自定义y轴格式
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

        # 隐藏特定的轴线
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # 设置刻度方向和颜色
        ax.tick_params(axis='y', direction='in')
        ax.tick_params(axis='x', color="#FFFFFF", direction='in', bottom=False)

        # 添加自定义图例
        if legend:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2,edgecolor='none', frameon=False,prop=prop)

        # 调整布局
        fig.tight_layout()

        # 保存图表到文件
        fig.savefig(save_path)
        plt.close(fig)
    
    except Exception as e:
        print(f"折线图制作遇到{e}问题")
    return plt



