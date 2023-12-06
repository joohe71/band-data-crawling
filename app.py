import json
import requests
import schedule
import time
from datetime import datetime
from urllib import request
import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 불러오기
token =  os.getenv("TOKEN")
band_key=os.getenv("BAND_KEY")
locale="ko_KR"
url = f"https://openapi.band.us/v2/band/posts?access_token={token}&band_key={band_key}&locale={locale}"
slack_hook_url = os.getenv("SLACK_WEBHOOK_URL")

def get_data(): 
    today = datetime.today().strftime("%Y/%m/%d")
    req = request.Request(url)
    res = request.urlopen(req)
    decoded = res.read().decode("utf8")
    json_dict = json.loads(decoded)
    result = json_dict["result_data"]["items"][0]["photos"][0]["url"]
    content = json_dict["result_data"]["items"][0]["content"]
    slack_res = requests.post(slack_hook_url,json={"text": f"<{result}|{today}>\n{content}" })
    # post 요청 함수 실행
    slack_res


# 매일 오전 11시 25분 slack webhook 알림 
schedule.every().day.at("12:00").do(get_data)

#무한 루프를 돌면서 스케쥴을 유지한다.
while True:
    schedule.run_pending()
    time.sleep(1)

