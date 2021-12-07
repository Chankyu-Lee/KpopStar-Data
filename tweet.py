#!/usr/bin/env python3
import os
import tweepy
import sys
import time
import re
import json
import requests
from requests_oauthlib import OAuth1
from PIL import Image, ImageFont, ImageDraw 

# Get Twitter API keys
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
access_token = os.environ.get('TWITTER_ACCESS_KEY')
access_token_secret = os.environ.get('TWITTER_ACCESS_SECRET')

module = "Twitter"

MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'

oauth = OAuth1(consumer_key,
  client_secret=consumer_secret,
  resource_owner_key=access_token,
  resource_owner_secret=access_token_secret)

test = False

def set_test_mode():
    """테스트 모드 활성화

    트윗이 게시되지 않도록 합니다. 콘솔에는 여전히 print 됩니다.
    이 기능은 디버깅 목적으로 매우 유용합니다.
    """

    global test 
    test = True

def retrieve_own_tweets(num=3):
    """bot 의 최근 tweet 을 검색합니다.

    전달인자:
    num: 검색할 tweet 수가 포함된 정수입니다.

    반환 값:
    tweet 객체 목록
    """

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    latest_tweets = api.user_timeline(screen_name="data_blackpink", count=num, tweet_mode="extended")
    return latest_tweets

def check_duplicates(message):
    """tweet message 를 최신 세 개의 사용자 tweet 과 대조하여 중복된 게시물이 없는지 확인합니다.

    전달인자:
    message: 게시할 메시지를 포함한 문자열

    반환 값:
    중복이 발견되었을 경우 True를 나타내는 boolean
    """
    last_three = retrieve_own_tweets()
    last_three_tweets = [tweet.full_text for tweet in last_three]  # 확인할 트윗 메시지 문자열 list

    for text_tweet in last_three_tweets:
      text_tweet = remove_URLs(text_tweet) # 각 tweet의 URL 제거
      if remove_URLs(message) in text_tweet: # match 되는 지 확인
        return True
    
    return False

def remove_URLs(text):
    """텍스트 문자열에서 URL 제거

    전달인자:
    텍스트: URL을 포함하는 텍스트

    반환 값:
    URL이 없는 동일한 텍스트
    """
    return re.sub(r" ?http\S+", "", text)

def twitter_repost(artist):
    """주어진 계정의 마지막 tweets 를 Retweets 합니다.

    전달인자:
      artist: artist 의 모든 상세사항이 포함된 dictionary

    반환 값:
      artist 의 업데이트된 data 를 포함하는 dictionary
    """
    print("[{}] repost 작업을 시작하는 중...".format(module))
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    print("[{}] ({}) tweets 가져옴".format(module, artist["twitter"]["url"]))

    if "last_tweet_id" in artist["twitter"] and artist["twitter"]["last_tweet_id"] is not None:
        tweets = api.user_timeline(screen_name = artist["twitter"]["url"], 
                                since_id = artist["twitter"]["last_tweet_id"],
                                include_rts = False,
                                # 전체 텍스트를 가져오는 확장 모드
                                tweet_mode = "extended"
                                )
    else:
        tweets = api.user_timeline(screen_name = artist["twitter"]["url"], 
                                # 마지막 트윗만 가져옴
                                count = 1,
                                include_rts = False,
                                # 전체 텍스트를 가져오는 확장 모드
                                tweet_mode = "extended"
                                )

    for tweet in tweets:
        print("@{} 에서 이 tweet 을 Retwitting 함".format(artist["twitter"]["url"]))
        print("Tweet ID: {}".format(tweet.id))
        print("날짜 시간: {}".format(tweet.created_at))
        print(tweet.full_text[:20])
        if test is False:
          try:
            api.retweet(tweet.id)
          except tweepy.TweepError as error:
            if error.api_code == 327:
              print("::warning file=tweet.py:: Tweet 이 다음 이유로 retweeted 되지 않았습니다. " + str(error.reason))
            else:
              raise tweepy.TweepError(str(error.reason))

    if len(tweets) > 0:
        artist["twitter"]["last_tweet_id"] = tweets[0].id
        
    print()
    return artist

def twitter_post(message):
    """ Twitter 에 message 게시 (Tweepy module 사용)
    
    전달인자:
        message: 게시할 message 를 포함하는 string
    """
    message = message[:270]
    print(message+"\n")

    if test is False:
      if not check_duplicates(message):
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            
            try:
                api.update_status(message)
            except tweepy.TweepError as error:
                 raise tweepy.TweepError(str(error.reason))
      else:
          print("::warning file=tweet.py:: 중복이기 때문에 Tweet 이 게시되지 않음.")
          
def twitter_post_image(message, filename, text, text_size=200, crop=False):
    """ Twitter 에 photo 와 message 를 게시 (Tweepy module 사용)
    
    전달인자:
        - message: 게시할 message 를 포함하는 string
        - url: 게시할 image의 filename
    """

    if text is not None:
        edit_image(filename, text, text_size=text_size, crop=crop)
    
    message = message[:270]
    print(message)
    print("Media: " + filename + "\n")

    if test is False:
      if not check_duplicates(message):
            # 파일이 video 인지 확인
            if filename[-3:] == "mp4":
                print("[{}] File 은 video 입니다.".format(module))
                # 비디오인 경우 chunk upload 를 시작함
                videoTweet = VideoTweet(filename)
                videoTweet.upload_init()
                videoTweet.upload_append()
                videoTweet.upload_finalize()
                videoTweet.media_id

                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                api = tweepy.API(auth)
                api.update_status(message, media_ids=[videoTweet.media_id])
                os.remove(filename)

            else:
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                api = tweepy.API(auth)

                uploaded = api.media_upload(filename)
                api.update_status(message, media_ids=[uploaded.media_id])
                os.remove(filename)
      else:
          print("::warning file=tweet.py:: 중복이기 때문에 Tweet 이 게시되지 않음.")

def edit_image(filename, text, text_size=200, crop=False):
    """ text 를 추가하여 image 편집 (Pillow module 사용)
    
    Args:
        - filename: 수정할 image 의 filename 
        - text: 추가할 text
        - text_size (선택사항): text 크기 (default: 200)
        - crop (선택사항): 활성화된 경우 비디오 섬네일에서 검은색 막대를 제거합니다 (16:9 over 4:3)
    """
    #이미지 열기
    my_image = Image.open(filename)
    # Crop
    if crop:
        # 이미지 크기(픽셀)(조직 이미지 크기) 
        width, height = my_image.size 
        
        # 잘린 이미지의 포인트 설정 
        left = 0
        right = width
        top = height / 8
        bottom = height - (height / 8)
        
        # 잘린 이미지 above dimension 
        my_image = my_image.crop((left, top, right, bottom)) 
    
    # 폰트 열기
    title_font = ImageFont.truetype('Montserrat-Bold.ttf', text_size)
    # 이미지 편집
    image_editable = ImageDraw.Draw(my_image)
    # 텍스트 추가
    image_editable.text((50,15), text, (237, 230, 211), font=title_font)
    # 이미지 저장
    my_image.save(filename)


class VideoTweet(object):

  def __init__(self, file_name):
    '''
    비디오 트윗 속성 정의
    '''
    self.video_filename = file_name
    self.total_bytes = os.path.getsize(self.video_filename)
    self.media_id = None
    self.processing_info = None


  def upload_init(self):
    '''
    업로드 초기화
    '''
    print("[{}] (video) 초기화 하는 중...".format(module))

    request_data = {
      'command': 'INIT',
      'media_type': 'video/mp4',
      'total_bytes': self.total_bytes,
      'media_category': 'tweet_video'
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    media_id = req.json()['media_id']

    self.media_id = media_id


  def upload_append(self):
    '''
    chunks 에 media 를 업로드하고 업로드한 chunks 에 추가합니다.
    '''

    print("[{}] (video) 추가 하는 중...".format(module))

    segment_id = 0
    bytes_sent = 0
    file = open(self.video_filename, 'rb')

    while bytes_sent < self.total_bytes:
      chunk = file.read(4*1024*1024)

      request_data = {
        'command': 'APPEND',
        'media_id': self.media_id,
        'segment_index': segment_id
      }

      files = {
        'media':chunk
      }

      req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=oauth)

      if req.status_code < 200 or req.status_code > 299:
        print(req.status_code)
        print(req.text)
        sys.exit(0)

      segment_id = segment_id + 1
      bytes_sent = file.tell()

      print("[{}] (video) {}%".format(module, int((bytes_sent / self.total_bytes) * 100)))

    print("[{}] (video) 업로드 완료되었습니다. ".format(module))


  def upload_finalize(self):
    '''
    업로드 완료 및 비디오 처리 시작
    '''
    print("[{}] (video) 마무리 중...".format(module))

    request_data = {
      'command': 'FINALIZE',
      'media_id': self.media_id
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)

    self.processing_info = req.json().get('processing_info', None)
    self.check_status()


  def check_status(self):
    '''
    비디오 처리 상태를 확인합니다.
    '''
    if self.processing_info is None:
      return

    state = self.processing_info['state']

    print("[{}] (video) 미디어 처리 상태는 {}".format(module, state))

    if state == u'succeeded':
      print("[{}] (video) 성공적으로 게시되었습니다!".format(module))
      return

    if state == u'failed':
      sys.exit(0)

    check_after_secs = self.processing_info['check_after_secs']
    
    time.sleep(check_after_secs)

    request_params = {
      'command': 'STATUS',
      'media_id': self.media_id
    }

    req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)
    
    self.processing_info = req.json().get('processing_info', None)
    self.check_status()
