import requests,json
from Get_Token import encode_url
from upload_file import upload
import time
import os
 
def get_status(uuid,user):
  URL='http://saas.pdflux.com/api/v1/saas/document/{}?user={}'.format(uuid,user)
  url = encode_url(URL, 'pdflux', 'TUlnNKr6Cq3t')
  r =requests.get(url)
  return r.text
 
def download_data(uuid,file_name,user):
  url='http://saas.pdflux.com/api/v1/saas/document/{}/excel?user={}'.format(uuid,user)
  down_url=encode_url(url, 'pdflux', 'TUlnNKr6Cq3t')
  down_res = requests.get(url=down_url)
  with open(file_name,"wb") as code:
    code.write(down_res.content)
 
def test_status():
    uuid='fad4c522-c71c-11ea-ba3d-00163e028884'
    # uuid='fb892010-c6a6-11ea-ba3d-00163e028884'
    res=get_status(uuid)
    print(res)
 
 
if __name__ == "__main__":
  fnames=["2023-03-22\uff1a\u820d\u5f97\u9152\u4e1a\uff1a\u820d\u5f97\u9152\u4e1a2022\u5e74\u5e74\u5ea6\u62a5\u544a.pdf"]
 
  user='lydata'
  uuids=["67b101bc-0123-11ef-9224-00163e028884"]
  for uuid,fname in zip(uuids,fnames):
    file_name=fname+'.xls'
    if(os.path.exists(file_name)):
      continue
    while True:
      res=get_status(uuid,user)
      res=json.loads(res)
      print(res)
      if(res['data']['parsed']==2):
        
        download_data(uuid,file_name,user)
        break
      time.sleep(20)