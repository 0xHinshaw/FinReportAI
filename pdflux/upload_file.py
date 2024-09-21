import requests,json
from Get_Token import encode_url
 
""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read() 
 
def upload(URL,fname):
  url = encode_url(URL, 'pdflux', 'TUlnNKr6Cq3t')
  data = {'file':open(fname, 'rb')}
  r =requests.post(url,files=data)
  return r.text
 
  
if __name__ == "__main__":
    fname='/data/financial_report_baijiu/公司公告/202412_15258_公司公告/2023-03-22：舍得酒业：舍得酒业2022年年度报告.pdf'
    user='lydata'
    URL='http://saas.pdflux.com/api/v1/saas/upload?user={}&force_updata=true'.format(user)
    response=upload(URL,fname)
    if response.status_code == 200:
        # Print response content
        print(response.json())
    else:
        print('Error:', response.status_code)
    uuid = response.json()['data']