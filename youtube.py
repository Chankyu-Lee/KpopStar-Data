#!/usr/bin/env papihon3
import os
import requests
import json
from pyyoutube import Api
from utils import display_num, convert_num, download_image
from tweet import twitter_post, twitter_post_image

# Get API key for YouTube
youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
url_video = "https://youtu.be/"

module = "YouTube"

def youtube_data(group):
    """youtube 관련 모든 작업을 수행합니다.
    유튜브에서 group 전체와 싱글 아티스트 data 를 스크랩합니다.
    전달인자:
      group: 스크랩할 group 의 data 를 갖는 dictionary
    반환값:
      갱신된 data 를 가진 동일한 group dictionary
    """

    print("[{}] 작업을 시작하는 중...".format(module))
    api = Api(api_key=youtube_api_key)

    # channel data 및 통계 가져오기
    channel_data = youtube_get_channel(api, group["youtube"]["url"])
    group["youtube"] = youtube_check_channel_change(group["youtube"], channel_data, group["hashtags"])

    # video data 및 통계 가져오기
    videos = youtube_get_videos(api, group["youtube"]["playlist"], group["youtube"]["name"])
    group["youtube"]["videos"] = youtube_check_videos_change(group["name"], group["youtube"]["videos"], videos, group["hashtags"])

    # 각 member 의 youtube data 가져오기
    for member in group["members"]:
        if "youtube" in member:
            channel_data = youtube_get_channel(api, member["youtube"]["url"])
            member["youtube"] = youtube_check_channel_change(member["youtube"], channel_data, member["hashtags"])

            videos = youtube_get_videos(api, member["youtube"]["playlist"], member["youtube"]["name"])
            member["youtube"]["videos"] = youtube_check_videos_change(member["name"], member["youtube"]["videos"], videos, member["hashtags"])
    
    print()
    return group

def youtube_get_channel(api, channel_id):
    """채널에 대한 세부 정보를 가져옵니다.
    전달인자:
      - api: The YouTube instance
      - channel_id: YouTube에 있는 해당 channel 의 ID
    반환값:
      channel 의 모든 스크랩된 data 를 포함하는 dictionary
    """

    data = api.get_channel_info(channel_id=channel_id)
    channel = data.items[0]

    channel_data = {
       "name": channel.snippet.title,
       "subs": channel.statistics.subscriberCount,
       "views": channel.statistics.viewCount,
       "playlist": channel.contentDetails.relatedPlaylists.uploads,
       "image": channel.snippet.thumbnails.high.url
       }

    print("[{}] ({}) 채널 불러옴".format(module, channel_data["name"]))

    return channel_data

def youtube_get_videos(api, playlist_id, name):
    """playlist 에서 videos 를 가져옵니다.
    전달인자:
      - api: The YouTube instance
      - playlist_id: YouTube의 playlist ID
      - name: playlist의 channel 소유자 name
    반환값:
      videos 목록
    """
    videos = []
    
    playlist = api.get_playlist_items(playlist_id=playlist_id, count=None)

    for video in playlist.items:
      # 최고 품질의 thumbnail 다운로드 시도
      if video.snippet.thumbnails.maxres is None:
        thumbnail = video.snippet.thumbnails.default.url
      else:
        thumbnail = video.snippet.thumbnails.maxres.url

        videos.append(
         {"name": video.snippet.title,
         "url": video.snippet.resourceId.videoId,
         "image": thumbnail}
        )

    print("[{}] {} videos 를 ({}) 에서 가져옴. ".format(module, len(videos), name))

    return videos
    

def youtube_check_channel_change(old_channel, new_channel, hashtags):
    """구독자 수 또는 channel 의 총 조회수에 변화가 있는지 확인합니다 .
    이전 channel data 와 새로운(이미 가져온) data 를 비교합니다.
    전달인자:
      - old_channel: channel 의 모든 이전 data 를 포함하는 dictionary
      - new_channel: channel 의 갱신된 모든 data 를 포함하는 dictionary
      - hashtags: 트윗에 추가할 hashtags
    반환값:
      channel 의 최신 data 를 갱신한 dictionary
    """

    # subs 가 새롭게 10만 명대에 도달하면 Tweet 합니다.
    if convert_num("100K", new_channel["subs"]) != convert_num("100K", old_channel["subs"]):
        twitter_post_image(
            "{} 가 {} 구독자를 달성했습니다. #YouTube\n{}".format(new_channel["name"], display_num(new_channel["subs"], decimal=True), hashtags),
            download_image(new_channel["image"]),
            display_num(new_channel["subs"], short=True, decimal=True),
            text_size=150
        )
    old_channel["subs"] = new_channel["subs"]

    # 합계 조회수가 증가하고 새로운 값에 이르렀을 경우는 tweet 합니다. (views_scale 를 기반로 합니다)
    if new_channel["views"] > old_channel["total_views"]:
      if convert_num(old_channel["views_scale"], new_channel["views"]) != convert_num(old_channel["views_scale"], old_channel["total_views"]):
          twitter_post_image(
              "{} 가 총 조회수 {} 을 달성했습니다! #YouTube\n{}".format(new_channel["name"], display_num(new_channel["views"]), hashtags),
              download_image(new_channel["image"]),
              display_num(new_channel["views"], short=True)
          )
      old_channel["total_views"] = new_channel["views"]

    old_channel["playlist"] = new_channel["playlist"]
    old_channel["name"] = new_channel["name"]
    old_channel["image"] = new_channel["image"]

    return old_channel

def youtube_check_videos_change(name, old_videos, new_videos, hashtags): 
    """새로운 video 가 있는지 확인합니다.
    아티스트의 이전 video 목록과 새(이미 가져온) video 목록을 비교합니다.
    새로 발표된 video 가 있거나 video 가 새로운 뷰 목표에 도달하는 경우 tweet 합니다.
    전달인자:
      - name: channel 의 이름
      - old_videos: 모든 이전 videos 를 포함하는 list
      - new_videos: 갱신된 모든 videos 를 포함하는 list
      - hashtags: Tweet 에 추가할 hashtags
    반환값:
      new_videos
    """
    
    if old_videos is not None:
        for new_video in new_videos:
            found = False
            for old_video in old_videos:
                if new_video["url"] == old_video["url"]:
                    found = True
            if not found:
                twitter_post_image(
                    "{} 의 유튜브에 새로운 영상 {} 가 업로드 되었습니다. \n{}\n{}".format(name, new_video["name"], url_video + new_video["url"], hashtags),
                    download_image(new_video["image"]),
                    "NEW",
                    text_size=100,
                    crop=True
                    )
    return new_videos
