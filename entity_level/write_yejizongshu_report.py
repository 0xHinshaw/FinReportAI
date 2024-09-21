import json
import asyncio
import re
import requests 

# API配置 
api_base_url = "http://10.120.18.242:30387/v1" 
api_key = "sk-b3RjMZgQjoCCQzqA2dD4F232532645Ab9948062611E45171"

# 设置请求头 
headers = { 
        'Authorization': f'Bearer {api_key}', 
        'Content-Type': 'application/json', 
}

from multi_agent.tools.data_source import (
    get_company_announcement_v2,
    get_baijiu_news,
    get_relative_date,
    get_code_by_company,
)
from multi_agent.tools.utils import apost_query
from multi_agent.tools.data_source import (
    sw_level_1_industry_gains,
    sw_level_3_industry_gains,
    top_gainers_by_industry,
    sw_pe_ttm,
    sw_relative_hs_pe_ttm,
    baijiu_price,
    indicator_price,
    indicator_quarterly_price,
)


def extract_bold_markdown(text):
    bold_pattern = r"\*\*(.*?)\*\*"
    bold_texts = re.findall(bold_pattern, text)
    bold_texts = [text for pair in bold_texts for text in pair if text]
    return bold_texts


def get_last_two_week_day(date_string):
    from datetime import datetime, timedelta
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    previous_date = date_obj - timedelta(days=14)
    previous_date_string = previous_date.strftime("%Y-%m-%d")
    return previous_date_string


def find_closest_previous_date(date_list, target_date,is_daily_data = True):
    from datetime import datetime

    # 将字符串日期转换为datetime对象
    date_list = [datetime.strptime(date, "%Y-%m-%d") for date in date_list]
    target_date = datetime.strptime(target_date, "%Y-%m-%d")
    # 过滤出所有早于目标日期的日期
    if is_daily_data:
        previous_dates = [date for date in date_list if date <= target_date]
    else :
        previous_dates = [date for date in date_list]
    if not previous_dates:
        return None  # 如果没有早于目标日期的日期，返回None
    # 找到最接近的日期
    closest_date = min(previous_dates, key=lambda date: abs(date - target_date))
    # 将datetime对象转换回字符串
    return closest_date.strftime("%Y-%m-%d")


class WriteWeekReport:
    def __init__(self, industry, start_date, end_date) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.industry = industry
        self.save_path = "/home/llmapi/finreport_test/multi_agent/pics/"
        self.title_prompt = """你是一个金融分析师正在写食品饮料行业的业绩综述报告，请你给这段话总结一个标题
【注意】直接输出标题即可，不要有多余的格式，要求标题精简
【注意】标题中不要出现“：，“”类似的标点符号
{write_content}
"""

    async def async_post_query(self, query, use_local_model=False):
        print("=" * 50)
        # print(f"输入问题：{query}")
        generate_text = await apost_query(query, use_local_model=use_local_model)
        answer = ""
        async for token in generate_text:
            answer += token
        # print(f"输出回复{answer}")
        return answer

    async def write_sw_1level_data(self):
        print("write_week_report:write_sw_1level_data......")
        x_list, y_list = await sw_level_1_industry_gains(
            self.start_date, self.end_date, f"{self.save_path}pic1.png"
        )
        with open(
            "/home/llmapi/finreport_test/multi_agent/pics/data/file1.json",
            "w",
            encoding="utf-8",
        ) as file:
            output_json = {
                "title": "图 1：申万一级行业涨幅（%）",
                "x_list": x_list,
                "y_list": y_list,
            }
            json.dump(output_json, file, ensure_ascii=False, indent=4)
        sorted_pairs = sorted(
            zip(x_list, y_list), key=lambda pair: pair[1], reverse=True
        )
        sorted_x_list, sorted_y_list = zip(*sorted_pairs)
        hs_300_index = sorted_x_list.index("沪深300")
        hs_300_value = sorted_y_list[hs_300_index]
        sorted_x_list, sorted_y_list = list(sorted_x_list), list(sorted_y_list)
        sorted_x_list.pop(hs_300_index)
        sorted_y_list.pop(hs_300_index)
        sort_index = sorted_x_list.index("食品饮料")
        data = f"食品饮料的涨幅为{round(sorted_y_list[sort_index], 2)}%，在申万一级行业中排名为{sort_index + 1}，沪深300的涨幅为{round(hs_300_value, 2)}%。\n食品饮料行业对比同期沪深300指数变化{round(sorted_y_list[sort_index] - hs_300_value, 2)}%"
        input_query = f"""你是一个金融分析师正在写食品饮料行业的分析报告，以下是从{self.start_date}到{self.end_date}之间申万一级行业涨幅情况，请描述总结食品饮料行业指数的情况，不超过100字。
先写从{self.start_date}到{self.end_date}之间SW“{self.industry}”行业指数涨幅情况，再写位于整个申万一级行业的具体排名，在对比同期沪深300指数变化百分点情况。
一级行业涨幅情况：
{data}
"""
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "## {title}\n".format(title=title)
        return write_content, title

    async def write_sw_3level_data(self):
        print("write_week_report:write_sw_3level_data......")
        x_list, y_list = await sw_level_3_industry_gains(
            self.start_date, self.end_date, f"{self.save_path}pic2.png"
        )
        with open(
            "/home/llmapi/finreport_test/multi_agent/pics/data/file2.json",
            "w",
            encoding="utf-8",
        ) as file:
            output_json = {
                "title": "图 2：SW食品饮料行业子行业涨幅（%）",
                "x_list": x_list,
                "y_list": y_list,
            }
            json.dump(output_json, file, ensure_ascii=False, indent=4)

        sorted_pairs = sorted(
            zip(x_list, y_list), key=lambda pair: pair[1], reverse=True
        )
        sorted_x_list, sorted_y_list = zip(*sorted_pairs)
        hs_300_index = sorted_x_list.index("沪深300")
        hs_300_value = sorted_y_list[hs_300_index]
        sorted_x_list, sorted_y_list = list(sorted_x_list), list(sorted_y_list)
        sorted_x_list.pop(hs_300_index)
        sorted_y_list.pop(hs_300_index)
        data = [
            "{}的涨幅为{}%，相比沪深300指数变动{}%".format(
                sorted_x_list[i],
                round(sorted_y_list[i], 2),
                round(sorted_y_list[i] - hs_300_value, 2),
            )
            for i in range(len(sorted_x_list))
        ] + ["沪深300的涨幅为{}".format(round(hs_300_value, 2))]
        input_query = f"""你是一个金融分析师正在写{self.industry}行业的分析报告，以下是从{self.start_date}到{self.end_date}之间SW{self.industry}行业子行业涨幅情况，请描述总结变化情况，不少于100字，不超过200字。
SW{self.industry}行业子行业涨幅情况：{data}
"""
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "\n## {title}\n".format(title=title)

        return write_content, title

    async def write_individual_returns_data(self, top_num):
        print("write_week_report:write_individual_returns_data......")
        save_path_top = f"{self.save_path}pic3.png"
        save_path_bottom = f"{self.save_path}pic4.png"
        x, y = await top_gainers_by_industry(
            self.start_date, self.end_date, save_path_top, save_path_bottom
        )
        with open(
            "/home/llmapi/finreport_test/multi_agent/pics/data/file3.json",
            "w",
            encoding="utf-8",
        ) as file:
            output_json = {
                "title": "图 3：SW食品饮料行业涨幅榜个股（%）",
                "x_list": x[:10],
                "y_list": y[:10],
            }
            json.dump(output_json, file, ensure_ascii=False, indent=4)
        with open(
            "/home/llmapi/finreport_test/multi_agent/pics/data/file4.json",
            "w",
            encoding="utf-8",
        ) as file:
            output_json = {
                "title": "图 4：SW食品饮料行业跌幅榜个股（%）",
                "x_list": x[-10:][::-1],
                "y_list": y[-10:][::-1],
            }
            json.dump(output_json, file, ensure_ascii=False, indent=4)
        pos_value = len([i for i in y if i >= 0])
        neg_value = len([i for i in y if i < 0])
        prompt_des_all = f"""SW食品饮料行业约有{round(pos_value * 100 / len(y), 2)}%个股录得正收益，{round(neg_value * 100 / len(y), 2)}%个股录得负收益"""
        top_up = [f"{x[i]}涨幅为{round(y[i], 2)}%" for i in range(top_num)]
        top_down = [
            f"{x[i]}涨幅为{round(y[i], 2)}%"
            for i in range(len(y) - 1, len(y) - top_num - 1, -1)
        ]
        prompt_change = f"""涨幅居前{top_num}的有:
{top_up}

跌幅居前{top_num}的有:
{top_down}
"""
        input_query = f"""你是一个金融分析师正在写{self.industry}行业的分析报告，以下是从{self.start_date}到{self.end_date}之间SW{self.industry}行业个股收益情况，请描述总结变化情况，不要写自己的观点，不少于100字，不超过200字。
{prompt_des_all}
{prompt_change}"""
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "\n## {title}\n".format(title=title)

        return write_content, title

    async def write_pe_data(self):
        print("write_week_report:write_pe_data......")
        # TODO: 转换为end_date对应的五年前日期
        y1, average_value_y1, x1_end = await sw_pe_ttm(
            "2019-01-01", self.end_date, save_path=f"{self.save_path}pic5.png"
        )
        y2, average_value_y2, x2_end = await sw_relative_hs_pe_ttm(
            "2019-01-01", self.end_date, save_path=f"{self.save_path}pic6.png"
        )
        input_query = f"""你是一个金融分析师正在写{self.industry}行业的分析报告，以下是SW{self.industry}行业市盈率情况，请描述总结变化情况，不要写自己的观点，不少于100字，不超过200字。
截至{x1_end}日，SW食品饮料行业整体PE（TTM，整体法）约{round(y1, 2)}倍，行业近五年均值水平为{round(average_value_y1, 2)}倍；
截至{x1_end}日，相对沪深300 PE（TTM，整体法）为{round(y2, 2)}倍，行业近五年相对估值中枢为{round(average_value_y2, 2)}倍。
"""
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "\n## {title}\n".format(title=title)

        return write_content, title

    async def write_baijius_data(self, produc_list):
        print("write_week_report:write_baijius_data......")
        data = ""
        pic_num = 7
        last_two_week_date = get_last_two_week_day(self.end_date)

        for product in produc_list:
            date_range, y_list = await baijiu_price(
                product,
                self.start_date,
                self.end_date,
                f"{self.save_path}pic{pic_num}.png",
            )
            with open(
                "/home/llmapi/finreport_test/multi_agent/pics/data/file{}.json".format(
                    pic_num
                ),
                "w",
                encoding="utf-8",
            ) as file:
                output_json = {
                    "title": "图 {pic_num}：{product}".format(
                        pic_num=pic_num, product=product
                    ),
                    "x_list": date_range,
                    "y_list": y_list,
                }
                json.dump(output_json, file, ensure_ascii=False, indent=4)

            pic_num += 1
            last_two_week_date = find_closest_previous_date(
                date_range, last_two_week_date
            )
            data += f"""{date_range[-1]}日{product}的价格为{y_list[-1]}元/瓶，{last_two_week_date}对应的价格为{y_list[date_range.index(last_two_week_date)]}元/瓶，相比变化{y_list[-1] - y_list[date_range.index(last_two_week_date)]}元/瓶\n"""
        input_query = f"""你是一个金融分析师正在写{self.industry}行业的分析报告，以下是{self.industry}行业白酒价格变化情况，请描述总结变化情况，不要写自己的观点，不少于100字，不超过200字。
【注意】日期对应的价格千万不要写错
{data}
"""
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "\n## {title}\n".format(title=title)

        return write_content, title

    async def write_indicators_data(self, produc_list, block, pic_num):
        data = ""
        for product in produc_list:
            print(f"write_week_report:write_indicators_data {product}......")
            # 全国:生猪存栏的数据是季度更新，因此需要进行特殊的处理
            if product != "全国:生猪存栏":
                date_range, y_list = await indicator_price(
                    product,
                    "2021-01-01",
                    self.end_date,
                    save_path=f"{self.save_path}pic{str(pic_num)}.png",
                )
            else:
                date_range, y_list = await indicator_quarterly_price(
                    product,
                    "2021-07-29",
                    self.end_date,
                    save_path=f"{self.save_path}pic{str(pic_num)}.png",
                )
                print(date_range)
                print(y_list)
            data_map = {date_range[i]: y_list[i] for i in range(len(date_range))}

            try:
                if product in [
                    "生产资料价格:大豆(黄豆)",
                    "现货价:豆粕",
                    "现货价格:白砂糖:天津:产地广西",
                    "现货价:大麦:全国均价",
                    "现货均价:铝锭(华南):佛山",
                    "出厂价:包装纸:瓦楞纸:140g",
                ]:
                    unit = "元/吨"
                elif product in ["现货价:玻璃"]:
                    unit = "元/平方米"
                elif product in ["平均价:生鲜乳(原奶):主产区", "平均批发价:猪肉"]:
                    unit = "元/公斤"
                elif product in ["全国:生猪存栏"]:
                    unit = "万头"
                with open(
                    "/home/llmapi/finreport_test/multi_agent/pics/data/file{}.json".format(
                        pic_num
                    ),
                    "w",
                    encoding="utf-8",
                ) as file:
                    output_json = {
                        "title": "图 {pic_num}：{indicator}".format(
                            pic_num=pic_num, indicator=product
                        ),
                        "x_list": date_range,
                        "y_list": y_list,
                        "unit": unit,
                    }
                    json.dump(output_json, file, ensure_ascii=False, indent=4)
                if product != "全国:生猪存栏":
                    if product in ["生产资料价格:大豆(黄豆)","啤酒:产量:当月值","啤酒:产量:累计值","平均价:生鲜乳(原奶):主产区"]:
                        is_daily_data = False
                    else:
                        is_daily_data = True
                    previous_month_date, three_months_ago_date, one_year_ago_date = (
                    get_relative_date(date_range[-1])
                    )
                    # todo: 五天前对应为start_date
                    last_two_week_date = get_last_two_week_day(self.end_date)
                    last_two_week_date = find_closest_previous_date(
                        date_range, 
                        last_two_week_date,
                        is_daily_data
                    )
                    previous_month_date = find_closest_previous_date(
                        date_range,
                        previous_month_date,
                        is_daily_data
                    )
                    three_months_ago_date = find_closest_previous_date(
                        date_range,
                        three_months_ago_date,
                        is_daily_data
                    )
                    one_year_ago_date = find_closest_previous_date(
                        date_range, 
                        one_year_ago_date,
                        is_daily_data
                    )
                    (
                        start_price,
                        end_price,
                        previous_month_price,
                        three_months_ago_price,
                        one_year_ago_price,
                        unit,
                    ) = (
                        data_map[last_two_week_date],
                        data_map[date_range[-1]],
                        data_map[previous_month_date],
                        data_map[three_months_ago_date],
                        data_map[one_year_ago_date],
                        unit,
                    )
                    month_gain = round(
                        (end_price - previous_month_price) * 100 / previous_month_price,
                        2,
                    )
                    months_gain = round(
                        (end_price - three_months_ago_price)
                        * 100
                        / three_months_ago_price,
                        2,
                    )
                    year_gain = round(
                        (end_price - one_year_ago_price) * 100 / one_year_ago_price,
                        2,
                    )
                    data += f"""截止{date_range[-1]}日{product}的价格为{end_price}{unit}，{last_two_week_date}日对应的价格为{start_price}{unit}，相比{last_two_week_date}日变化了{end_price-start_price}{unit}。同时月环比变化{month_gain}%，季环比变化{months_gain}%，同比变化{year_gain}%。\n"""
                else:
                    (
                        end_price,
                        three_months_ago_price,
                        one_year_ago_price,
                        unit,
                    ) = (
                        data_map[date_range[-1]],
                        data_map[date_range[-2]],
                        data_map[date_range[-5]],
                        unit,
                    )
                    months_gain = round(
                        (end_price - three_months_ago_price)
                        * 100
                        / three_months_ago_price,
                        2,
                    )
                    year_gain = round(
                        (end_price - one_year_ago_price) * 100 / one_year_ago_price,
                        2,
                    )
                    data += f"""截止{date_range[-1]}日{product}的价格为{end_price}{unit}，季环比变化{months_gain}%，同比变化{year_gain}%。\n"""

                pic_num += 1

            except:
                print(f"{product}出现错误，数据不够！")
        input_query = """你是一个金融分析师正在写{industry}行业的分析报告，以下是{industry}行业{block}原材料价格波动情况，请描述复述总结变化情况，不要写自己的观点，不少于200字，不超过300字。
【注意】不要遗漏关键的价格信息
原材料价格波动情况：
{data}
""".format(
            industry="食品饮料", data=data, block=block
        )
        print(input_query)
        write_content = await self.async_post_query(input_query)
        write_content += "\n"
        title_prompt = self.title_prompt.format(write_content=write_content)
        title = await self.async_post_query(title_prompt)
        title = title.replace(" ", "").replace("\t", "").strip()
        title = "\n## {title}\n".format(title=title)

        return write_content, title

    async def write_important_news(self):
        prompt_select = """你是一个金融分析师，请从以下新闻列表中选取最重要的5个，重点关注股份相关的，并输出对应的列表index
    【注意】输出列表格式[]即可,列表长度不超过5，不要输出多余内容
    公司公告：{}
    """
        prompt_conclusion_announcement = """你是一个金融分析师正在写行业分析报告，请从总结以下新闻中提炼重要信息，不少于100字，不超过150字：
    【注意】直接输出总结内容即可，不要输出多余内容
    新闻：{}
    """
        title_list, time_list, content_list, url_list = get_baijiu_news(
            self.start_date, self.end_date
        )
        input_query = prompt_select.format(str(title_list))
        try:
            select_index = await self.async_post_query(input_query)
            select_index = eval(select_index)
        except:
            import random

            select_index = sorted(
                random.sample(
                    range(len(title_list)),
                    5 if 5 <= len(title_list) else len(title_list),
                )
            )
        write_content = ""
        print("select_index", select_index)
        for index in select_index:
            input_query = prompt_conclusion_announcement.format(content_list[index])
            conclusion = await self.async_post_query(input_query, use_local_model=True)
            title = "[{}({})]({})".format(
                title_list[index], time_list[index], url_list[index]
            )
            write_content += title + "\n"
            write_content += conclusion + "\n\n"
        return write_content, "\n## 行业重要新闻\n"

    async def write_important_announcement(self):
        liquor_stock_ids = []
        for company in ["山西汾酒", "舍得酒业"]:
            res = await get_code_by_company(company)
            liquor_stock_ids.append(res.split(".")[0])

        sauce_stock_ids = []
        for company in ["中炬高新", "海天味业"]:
            res = await get_code_by_company(company)
            sauce_stock_ids.append(res.split(".")[0])
        dairy_stock_ids = []
        for company in ["伊利股份"]:
            res = await get_code_by_company(company)
            dairy_stock_ids.append(res.split(".")[0])
        preprocessed_food_stock_ids = []
        for company in ["安井食品"]:
            res = await get_code_by_company(company)
            preprocessed_food_stock_ids.append(res.split(".")[0])
        module_dict = {
            "白酒板块": liquor_stock_ids,
            "调味品板块": sauce_stock_ids,
            "乳制品板块": dairy_stock_ids,
            "预加工食品板块": preprocessed_food_stock_ids,
        }

        prompt = """你是一个金融分析师，请从以下{module}中相关公司的公告列表中选取最重要的两个，重点关注股份相关的，并输出对应的列表index
    【注意】直接输出index列表即可，不要输出多余内容
    公司公告：{relative_announcements}
    """
        prompt_conclusion_announcement = """你是一个金融分析师正在写行业分析报告，请从总结以下公司公告内容提炼重要信息，不少于100字，不超过200字：
    【注意】直接输出总结内容即可，不要输出多余内容
    公司公告：{}
    """
        write_content = ""
        for module in module_dict.keys():
            relative_announcements = []
            url_list = []
            time_list = []
            content_list = []
            for stockid in module_dict[module]:
                json_data_list = get_company_announcement_v2(
                    stockid, self.start_date, self.end_date
                )
                time_list += [json_data["time"] for json_data in json_data_list]
                url_list += [json_data["url"] for json_data in json_data_list]
                relative_announcements += [
                    json_data["title"] for json_data in json_data_list
                ]
                content_list += [json_data["content"] for json_data in json_data_list]
            input_query = prompt.format(
                module=module, relative_announcements=str(relative_announcements)
            )
            res = []
            try:
                res = await self.async_post_query(input_query)
                res = eval(res)
                res = [i for i in res if i < len(time_list)]
            except:
                import random

                res = sorted(
                    random.sample(
                        range(len(relative_announcements)),
                        (
                            2
                            if 2 <= len(relative_announcements)
                            else len(relative_announcements)
                        ),
                    )
                )
            for i in res:
                time_cur = time_list[i]
                title_cur = relative_announcements[i]
                url_cur = url_list[i]
                content = content_list[i]
                input_query = prompt_conclusion_announcement.format(content)
                conclusion = await self.async_post_query(
                    input_query, use_local_model=True
                )
                write_content += "[{title}({time})]({url})\n\n".format(
                    title=title_cur, time=time_cur, url=url_cur
                )
                write_content += conclusion + "\n\n"
        return write_content, "\n## 上市公司重要公告\n"

    async def write_viewpoint(self, all_content):
        prompt = """你是一个金融分析师，正在写{industry}的行业报告，请根据以下已知的信息总结“白酒板块”和“大众品板块”的行业周观点
【注意】生成的内容一定不要超过450字。
【注意】生成的内容请不要出现换行

已知信息：
{all_content}
"""
        input_query = prompt.format(industry=self.industry, all_content=all_content)
        write_content = await self.async_post_query(query=input_query)
        write_content += "\n\n"
        return write_content, "\n## 行业周观点\n"

    async def write_risk(self, all_content):
        prompt = """你是一个金融分析师，正在写{industry}的行业报告，请根据以下已知的信息分点罗列可能的风险
    【注意】不超过400字
    【注意】罗列最主要的风险点，风险点不超过6点
    已知信息：{all_content}
    """
        input_query = prompt.format(industry=self.industry, all_content=all_content)
        write_content = await self.async_post_query(query=input_query)
        write_content += "\n"
        return write_content, "## 风险提示\n"

    async def write_hangqinghuigu(self, all_content):
        prompt = """你是一个金融分析师，正在写{industry}的行业报告，请根据以下已知的信息总结“行情回顾”部分的内容
    【注意】生成的内容不要超过200字
    【注意】不要换行
    【回答格式】**行情回顾：** ......
    已知信息：{all_content}
    """
        input_query = prompt.format(industry=self.industry, all_content=all_content)
        write_content = await self.async_post_query(query=input_query)
        write_content += "\n\n"
        return write_content, ""

    def write_summary_viewpoint(self, all_content):
        return all_content, "**行业周观点：** "

    async def write_summary_risk(self, all_content):
        prompt = """你是一个金融分析师，正在写{industry}的行业报告，请根据以下已知的信息总结风险点
    【注意】罗列风险点即可，不要输出多余内容
    【注意】输出在一段上，不要有换行符
    已知信息：{all_content}
    """
        input_query = prompt.format(industry=self.industry, all_content=all_content)
        write_content = await self.async_post_query(query=input_query)
        write_content += "\n"
        return write_content, "**风险提示:** "

    async def main(self):
        all_content = ""
        hangqing_content = ""
        viewpont_content = ""
        risk_content = ""
        write_content, title = await self.write_sw_1level_data()
        all_content += title + write_content
        hangqing_content += title + write_content
        yield title
        yield write_content
        yield "\n![图 1：2024年05月20日-2024年05月31日申万一级行业涨幅（%）](http://10.13.14.16:8888/pics/pic1.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file1.json)"
        write_content, title = await self.write_sw_3level_data()
        all_content += title + write_content
        hangqing_content += title + write_content
        yield title
        yield write_content
        yield "\n![图 2：2024年05月20日-2024年05月31日SW食品饮料行业子行业涨幅（%）](http://10.13.14.16:8888/pics/pic2.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file2.json)\n"

        write_content, title = await self.write_individual_returns_data(10)

        all_content += title + write_content
        yield title
        yield write_content
        yield "\n![图 3：SW食品饮料行业涨幅榜个股（%）](http://10.13.14.16:8888/pics/pic3.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file3.json)"

        yield "\n![图 4：SW食品饮料行业跌幅榜个股（%）](http://10.13.14.16:8888/pics/pic4.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file4.json)"

        write_content, title = await self.write_pe_data()
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图5：SW食品饮料行业PE（TTM，剔除负值，倍）](http://10.13.14.16:8888/pics/pic5.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file5.json)"

        yield "\n![图6：SW食品饮料行业相对沪深300PE（TTM，剔除负值，倍）](http://10.13.14.16:8888/pics/pic6.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file6.json)"

        write_content, title = await self.write_baijius_data(
            ["2024年散瓶飞天", "普五八代", "国窖1573"]
        )
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图 7：飞天茅台2024散装批价（元/瓶）](http://10.13.14.16:8888/pics/pic7.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file7.json)"

        yield "\n![图 8：八代普五批价（元/瓶）](http://10.13.14.16:8888/pics/pic8.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file8.json)"

        yield "\n![图 9：国窖1573批价（元/瓶）](http://10.13.14.16:8888/pics/pic9.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file9.json)"

        write_content, title = await self.write_indicators_data(
            produc_list=[
                "生产资料价格:大豆(黄豆)",
                "现货价:豆粕",
                "现货价格:白砂糖:天津:产地广西",
                "现货价:玻璃",
            ],
            block="调味品板块",
            pic_num=10,
        )
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图 10：全国黄豆市场价（元/吨）](http://10.13.14.16:8888/pics/pic10.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file10.json)"

        yield "\n![图 11：全国豆粕市场价（元/吨）](http://10.13.14.16:8888/pics/pic11.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file11.json)"

        yield "\n![图 12：白砂糖现货价（元/吨）](http://10.13.14.16:8888/pics/pic12.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file12.json)"

        yield "\n![图 13：玻璃现货价（元/平方米）](http://10.13.14.16:8888/pics/pic13.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file13.json)"

        write_content, title = await self.write_indicators_data(
            produc_list=[
                "现货价:大麦:全国均价",
                "现货价:玻璃",
                "现货均价:铝锭(华南):佛山",
                "出厂价:包装纸:瓦楞纸:140g",
            ],
            block="啤酒板块",
            pic_num=14,
        )
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图 14：大麦现货均价（元/吨）](http://10.13.14.16:8888/pics/pic14.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file14.json)"

        yield "\n![图 15：玻璃现货价（元/平方米）](http://10.13.14.16:8888/pics/pic15.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file15.json)"

        yield "\n![图 16：铝锭现货均价（元/吨）](http://10.13.14.16:8888/pics/pic16.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file16.json)"

        yield "\n![图 17：瓦楞纸出厂价（元/吨）](http://10.13.14.16:8888/pics/pic17.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file17.json)"

        write_content, title = await self.write_indicators_data(
            produc_list=[
                "平均价:生鲜乳(原奶):主产区",
            ],
            block="乳品板块",
            pic_num=18,
        )
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图 18：生鲜乳均价（元/公斤）](http://10.13.14.16:8888/pics/pic18.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file18.json)"

        write_content, title = await self.write_indicators_data(
            produc_list=["平均批发价:猪肉", "全国:生猪存栏"],
            block="肉制品板块",
            pic_num=19,
        )
        all_content += title + write_content

        yield title
        yield write_content
        yield "\n![图 19：猪肉平均批发价（元/公斤）](http://10.13.14.16:8888/pics/pic19.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file19.json)"

        yield "\n![图 20：生猪存栏量（万头）](http://10.13.14.16:8888/pics/pic20.png)"
        yield "\n[数据源](http://10.13.14.16:8888/pics/data/file20.json)"

        write_content, title = await self.write_important_news()
        all_content += title + write_content

        yield title
        yield write_content
        write_content, title = await self.write_important_announcement()
        all_content += title + write_content

        yield title
        yield write_content
        write_content, title = await self.write_viewpoint(all_content)
        write_content_list = write_content.split("\n")
        write_content_list = [text for text in write_content_list if "##" not in text]
        viewpont_content += "".join(write_content_list)
        yield title
        yield write_content
        write_content, title = await self.write_risk(all_content)
        yield title
        yield write_content
        risk_content += write_content

        yield "## 投资要点\n"
        write_content, title = await self.write_hangqinghuigu(hangqing_content)
        yield title
        yield write_content.replace("\n", "") + "\n"
        write_content, title = self.write_summary_viewpoint(viewpont_content)
        yield title
        yield write_content.replace("\n", "") + "\n"
        write_content, title = await self.write_summary_risk(risk_content)
        yield title
        yield write_content.replace("\n", "") + "\n"


async def start(start_date, end_date):
    async for i in WriteWeekReport("食品饮料", start_date, end_date).main():
        yield json.dumps({"answer": i}, ensure_ascii=False)
        await asyncio.sleep(0.5)  # 每秒发送一次数据


async def start_true(start_date, end_date):
    async for i in WriteWeekReport("食品饮料", start_date, end_date).main():
        output_json = {
            "status": "pending",
            "chunkName": "answer",
            "chunkValue": i,
        }
        data = f"data: {json.dumps(output_json, ensure_ascii=False)}\n\n"
        yield data
        await asyncio.sleep(0.5)  # 每秒发送一次数据
    output_json = {
        "status": "done",
        "chunkName": "answer",
        "chunkValue": "",
    }
    data = f"data: {json.dumps(output_json, ensure_ascii=False)}\n\n"
    yield data
    await asyncio.sleep(0.5)  # 每秒发送一次数据


if __name__ == "__main__":
    path = "/home/llmapi/finreport_test/multi_agent/agents/test.md"
    start_date = "2024-05-20"
    end_date = "2024-06-02"
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
