#!/usr/bin/env python3
import os
from instascrape import *
from utils import display_num, convert_num, download_image
from tweet import twitter_post, twitter_post_image

# Get Instagram cookies
instagram_sessionid = os.environ.get('INSTAGRAM_SESSION_ID')
headers = {"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
"cookie": f"sessionid={instagram_sessionid};"}

module = "Instagram" #module에 "Instagram"을 저장

def instagram_data(group):
    """
    모든 Instagram 관련 작업을 실행합니다.

    인스타그램에서 그룹 전체 및 싱글 아티스트의 데이터를 스크랩합니다.

    전달인자:
      group: 스크랩할 그룹의 데이터가 있는 딕셔너리

    반환값:
      업데이트된 데이터가 있는 동일한 그룹 딕셔너리
    """

    print("[{}] 시작하는중...".format(module)) # Instagram 시작하는중...
    group, ig_profile = instagram_profile(group)
    group = instagram_last_post(group, ig_profile)

    for artist in group["members"]:
        artist, ig_profile = instagram_profile(artist)
        artist = instagram_last_post(artist, ig_profile)

    print()
    return group

def instagram_last_post(artist, profile):
    """
    프로필의 마지막 게시물을 가져옵니다.

    가장 최근에 저장된 게시물의 타임스탬프가 가장 최근에 가져온 게시물의 타임스탬프와 일치하지 않는 경우,
    새 게시물이 있으면 트윗합니다.
    
    전달인자:
      - profile: 이미 스크랩된 프로필 인스턴스
      - artist: 아티스트의 모든 세부 정보가 포함된 딕셔너리

    반환값:
      아티스트의 업데이트된 모든 데이터를 포함하는 딕셔너리
    """

    print("[{}] ({}) 새 게시물 가져오기".format(module, artist["instagram"]["url"][26:-1]))

    recents = profile.get_recent_posts()
    
    for recent in recents:
      recent.scrape(headers=headers)
      # 마지막 게시물 타임스탬프가 더 크거나(최신 게시물임) 저장된 게시물이 존재하지 않는 경우
      if "last_post" not in artist["instagram"] or recent.timestamp > artist["instagram"]["last_post"]["timestamp"]:
        url = "https://www.instagram.com/p/" + recent.shortcode
        if recent.is_video:
            content_type = "video"
            filename = "temp.mp4"
        else:
            content_type = "photo"
            filename = "temp.jpg"
        recent.download(filename)
        twitter_post_image(
            "{}가 Instagram에 새로운 {} 를 게시했습니다. \n{}\n{}\n{}\n\n{}".format(artist["name"], content_type, clean_caption(recent.caption), recent.timestamp, url, artist["hashtags"]),
            filename,
            None
        )
      else:
        break

    last_post = {}
    last_post["url"] = "https://www.instagram.com/p/" + recents[0].shortcode
    last_post["caption"] = recents[0].caption
    last_post["timestamp"] = recents[0].timestamp

    artist["instagram"]["last_post"] = last_post
    
    return artist

def instagram_profile(artist):
    """
    Instagram에서 아티스트의 세부 정보를 가져옵니다.

    아티스트가 새로운 팔로워 목표에 도달하면 트윗합니다.

    전달인자:
      artist: 아티스트의 모든 세부 정보가 포함된 딕셔너리

    반환값:
      - 아티스트의 업데이트된 모든 데이터가 포함된 딕셔너리
      - 프로필 인스턴스
    """

    print("[{}] ({}) 프로필 세부정보 가져오기".format(module, artist["instagram"]["url"][26:-1]))

    profile = Profile(artist["instagram"]["url"])
    profile = profile.scrape(headers=headers, inplace=False)
    artist["instagram"]["posts"] = profile.posts
    #프로필 사진 업데이트
    artist["instagram"]["image"] = profile.profile_pic_url_hd

    #이전에 발생한 적이 없는 경우 팔로워 추가
    if "followers" not in artist["instagram"]:
      artist["instagram"]["followers"] = profile.followers

    #증가가 있는 경우에만 팔로워 업데이트
    if profile.followers > artist["instagram"]["followers"]:
        print("[{}] ({}) 팔로워 증가함 {} --> {}".format(module, artist["instagram"]["url"][26:-1], artist["instagram"]["followers"], profile.followers))
        if convert_num("M", artist["instagram"]["followers"]) != convert_num("M", profile.followers):
            twitter_post_image(
                "{} 의 Instagram 팔로워가 {}에 도달했습니다.\n{}".format(artist["name"], display_num(profile.followers), artist["hashtags"]),
                download_image(artist["instagram"]["image"]),
                display_num(profile.followers, short=True),
                text_size=50
                )
        artist["instagram"]["followers"] = profile.followers
    
    return artist, profile

def clean_caption(caption):
    """
    Instagram 게시물 캡션의 불필요한 부분을 제거합니다.

    모든 해시태그를 제거하고 일반 텍스트로 태그를 변환합니다.(ex:@marco97pa --> marco97pa)

    전달인자:
      caption:텍스트
    
    반환값
      해시태그와 태그가 없는 동일한 캡션
    """

    clean = "" #빈 문자열 생성

    words = caption.split() #매개변수로 입력한 문자열을 기준으로 원본 문자열을 나누어 리스트로 생성
    for word in words:
        if word[0] != "#":
            if word[0] == "@":
                clean += word[1:] + " " #문자열[0]에 #이나 @가 있으면 문자열[1]부터 clean에 저장
            else:
                clean += word + " "     #문자열[0]에 #이나 @이 없으면 그대로 clean에 저장

    return clean[:90] #clean 반환
