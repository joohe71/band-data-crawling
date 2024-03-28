import json
import requests
import schedule
import time
from datetime import datetime
from urllib import request
from dotenv import load_dotenv
import uuid
# requests 로 대체 가능
import httplib2
import os

load_dotenv()

# 환경 변수 불러오기
token =  os.getenv("TOKEN")
band_key=os.getenv("BAND_KEY")
locale="ko_KR"
url = f"https://openapi.band.us/v2/band/posts?access_token={token}&band_key={band_key}&locale={locale}"
slack_hook_url = os.getenv("WEBHOOK_URL")
# slack_hook_url = os.getenv("JUN_URL")

flag = False
error_flag = True

def convert_date(date):
    epoch_time = int(date)/1000
    # print(epoch_time)
    datetime_type_value = datetime.fromtimestamp(epoch_time)
    # uncomment next line If you want str value of datetime such as ["2022-02-23", "2022-02-24" ...]
    datetime_type_value = datetime_type_value.strftime("%F")
    return datetime_type_value

class LunchCard:
    def __init__(self, image_url: str, content: str, date: str):
        self.image_url = image_url
        self.content = content
        self.date = date

    def to_dict(self):
        text = f"{self.date}"
        content = []
        # 음식 사진 추가
        for image in self.image_url:
            content.append(dict(image=dict(imageUrl=image, altText="Nature")))
        return dict(
            cardsV2=[
                dict(
                    cardId=str(uuid.uuid4()),
                    card=dict(
                        header=dict(title=text),
                        sections=[
                            dict(
                                collapsible=True,
                                uncollapsibleWidgetsCount=2,
                                widgets=[
                                    {
                                    "textParagraph": {
                                        "text": f"오늘 뭐먹지? \n {self.content} \n 메뉴 사진을 보고 싶으시면 아래 [Show more] 버튼을 클릭해주세요."
                                        }
                                    },
                                    # dict(image=dict(imageUrl=self.image_url[2], altText="Nature"))
                                    content
                                ]
                            )
                        ]
                    )
                )
            ]
        )

def get_data():
    global flag
    global error_flag
    now = datetime.now()
    hour, minute= now.hour, now.minute
    if hour == 00 and minute == 35:
        flag = False

    if flag :
        test_res = requests.post(slack_hook_url, json={"test":"test"})
        test_res
    else:
        today = datetime.today().strftime("%Y-%m-%d")
        req = request.Request(url)
        res = request.urlopen(req)
        decoded = res.read().decode("utf8")
        json_dict = json.loads(decoded)
        try:
            items = json_dict["result_data"]["items"]
            for item in items:
                result = []
                # INT 형 날짜 -> 년-월-일 형식으로 변환
                created_date = convert_date(item['created_at'])
                # 게시자가 "김유민"이고 "사진"이 있고 글 생성 일자가 오늘과 같을 때
                if (item['author']['name'] == "조성환" or item['author']['name'] == "김유민") and item["photos"][0]["url"] != '' and today == created_date:
                    for photo in item["photos"]:
                        result.append(photo['url'])
                    content = item["content"]
                    flag = True
                    error_flag = False
                    break
        except Exception as e:
            # print(e)
            error_flag = True
            

        if not error_flag:
            card = LunchCard(image_url=result, content=content, date=today)
            body_string = json.dumps(card.to_dict())

            message_headers = {"Content-Type": "application/json; charset=UTF-8"}
            http_obj = httplib2.Http()
            response, content = http_obj.request(
                uri=slack_hook_url,
                method="POST",
                headers=message_headers,
                # body=json.dumps(app_message),
                body=body_string
            )
            try:
                assert response.status == 200
            except AssertionError as e:
                print(content)
                raise e
        else:
            test_res = requests.post(slack_hook_url, json={"test":"test"})
            test_res

schedule.every(1).minutes.do(get_data)

#무한 루프를 돌면서 스케쥴을 유지한다.
while True:
    schedule.run_pending()
    time.sleep(1)