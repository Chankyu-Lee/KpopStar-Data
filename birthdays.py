#!/usr/bin/env python3
import datetime
from utils import download_image
from tweet import twitter_post_image, twitter_post

module = "Birthdays"        # module에 "Birthdays" 문자열을 저장한다.

def check_birthdays(group):
    """오늘이 그룹 구성원의 생일인지 확인합니다.

    누군가의 생일이면 트윗을 한다.

    전달인자:
      group: 그룹의 모든 내용을 수록한 dictionary

    반환값:
      그룹의 최신 자료를 모두 수록한 dictionary
    """
    
    now = datetime.datetime.today()                           # 현재 지역 날짜를 now에 저장한다.
    print("[{}] 오늘은 {} 입니다.".format(module, now.date()))        # ex) [Birthdays] 오늘은 2021-11-01
    
    print("[{}] 체크하는중...".format(module))                # [Birthdays] 체크하는중...
    for member in group["members"]:                               # member에 group의 "members" key에 해당하는 value값(멤버)을 대입하고,
        birthday = datetime.datetime.strptime(member["birthday"], '%d/%m/%Y')               # (strptime 함수는 날짜, 시간형식의 문자열을 datetime으로 만들 때 사용)
        difference = round((now - birthday).days / 365.25)        # 현재에서 생일을 뺀 날을 365.25로 나누어 반올림 혹은 반내림한 값 = 나이 = difference
        birthday = birthday.replace(year=now.year)                # year에 저장되어있던 생일 연도를 올해 연도로 바꾼다. -> 올해 생일이 된다.     (replace함수는 날짜나 시간을 변경할 때 쓰는 함수)
        if birthday.date() == now.date() :                        # 생일의 날짜와 오늘 날짜가 같다면,
            print("[{}] ({}) 생일: {}살!".format(module, member["name"], difference))       # ex) [Birthdays] (제니) 생일: 20살!
            if member["years"] != difference:                     # member의 "years" key 값이 difference(나이)와 다르다면
                member["years"] = difference                      # member의 "years" key 값에 difference(나이)를 저장한다.
                twitter_post_image(                               # tweet.py에 있는 twitter_post_image함수(message, filename, text, text_size=200, crop=False) 사용
                    "오늘은 #{}의 {}번째 생일입니다!\n{}".format(member["name"].upper(), difference, member["hashtags"]),       #upper()은 모든 문자열을 대문자로 바꿔주는 함수
                    download_image(member["instagram"]["image"]),         # utils.py에 있는 download_image함수(url) 사용
                    str(difference)
                    )
    print()
    return group        #group을 다시 반환한다.
