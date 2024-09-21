from income import get_income_info
from cashflow import find_cash_flow_statements
from net_profit import get_net_profit
from gross_margin import find_gross_margin
from revenue import get_revenue

possible_parameters = {"营业总收入总量",'营业总收入同比', '营业总收入季环比',
                       "归属于母公司股东的净利润总量",'归属于母公司股东的净利润同比', '归属于母公司股东的净利润季环比',
                       "毛利率", '销售费用率', '管理费用率', '财务费用率', '研发费用率', '净利润',
                       '经营活动产生的现金流量净额'}

def extract_data(file_path, parameter):
    """
    The function `extract_data` takes a file path and a parameter, and based on the parameter, it
    extracts specific data from the file or performs certain operations.
    
    :param file_path: The `file_path` parameter is a string that represents the file path of the Excel
    file from which you want to extract data
    :param parameter: Must be one of the specified parameters.
    :return: The function `extract_data` returns different values based on the `parameter` provided:
    - If the `parameter` contains '营业总收入', it returns the income information using `get_income_info`.
    - If the `parameter` contains '归属于母公司股东的净利润', it extracts the target and returns the net profit
    using `
    """
    assert parameter in possible_parameters, "Invalid parameter."

    if '营业总收入' in parameter:
        return get_income_info(file_path, parameter)
    elif '归属于母公司股东的净利润' in parameter:
        target = parameter[12:]
        return get_net_profit(file_path, target)
    elif parameter == '经营活动产生的现金流量净额':
        return find_cash_flow_statements(file_path)
    elif parameter == "毛利率":
        return find_gross_margin(file_path)
    else:
        result = get_revenue(file_path)
        if result:
            return {parameter: result.get(parameter, None)}
        else:
            return None
    
if __name__ == '__main__':
    file_path = '/data/financial_report_baijiu/公司公告/tables/2018-03-28：贵州茅台2017年年度报告.xlsx'
    print(extract_data(file_path, "营业总收入总量"))
