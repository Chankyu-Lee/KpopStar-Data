#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import display_num, convert_num, download_image
from tweet import twitter_post, twitter_post_image

module = "Spotify"

def login():
    """
    Spotify에 로그인

     클라이언트 자격 증명 승인 흐름
     환경 변수로 설정하려면 다음 API 키가 필요합니다.

       * SPOTIPY_CLIENT_ID
       * SPOTIPY_CLIENT_SECRET
      
     API 키는 `Spotify 개발자 대시보드 <https://developer.spotify.com/dashboard/>`_에서 요청할 수 있습니다.

     자세한 내용은 https://spotipy.readthedocs.io/en/2.16.1/#authorization-code-flow를 참조하세요.
    """

    print("[{}] 로그인중...".format(module)) #Spotify 로그인중...
    
    auth_manager = SpotifyClientCredentials() #auth_manager라는 SpotifyClientCredentials 클래스 생성
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return spotify

def get_artist(spotify, artist, hashtags):
    """
    아티스트에 대한 세부정보를 가져옵니다.

    아티스트가 Spotify에서 팔로워의 새로운 목표에 도달하면 트윗합니다.

    전달인자:
    - Spotify: Spotify 인스턴스
    - artist: 단일 아티스트에 대한 모든 데이터가 포함된 딕셔너리
    - hashtags: 트윗에 추가할 해시태그

    반환값:
    업데이트된 프로필 세부 정보가 포함된 아티스트 딕셔너리
    """
    # URI 생성
    artist["uri"] = 'spotify:artist:' + artist["id"]

    artist_details = spotify.artist(artist["uri"])


    artist["name"] = artist_details["name"]
    print("[{}] ({}) 세부정보 불러오는중... (ID: {})".format(module, artist["name"], artist["id"]))

    artist["popularity"] = artist_details["popularity"]
    artist["genres"] = artist_details["genres"]
    try: 
        artist["image"] = artist_details["images"][0]["url"]
    except: #이미지가 없으면 경고 출력
        artist["image"] = None
        print("경고:{}의 이미지를 불러오지 못했습니다.".format(artist["name"])) #이것은 프로필 이미지가 없는 아티스트에게 필요합니다.
    #convert_num("100k",num):100000으로 num을 나눔,artist_details["followers"]["total"]이 artist["followers"]보다 크면 
    if convert_num("100K", artist_details["followers"]["total"]) > convert_num("100K", artist["followers"]):
        artist["followers"] = artist_details["followers"]["total"] #artist["followers"]를 artist_details["followers"]["total"]로 변경
        twitter_post_image( #이미지 게시
            "{}가 Spotify {} 팔로워를 달성했습니다. \n{}\n{}".format(artist["name"], display_num(artist["followers"], decimal=True), link_artist(artist["id"]), hashtags),
            download_image(artist["image"]),
            display_num(artist["followers"], short=True, decimal=True),
            text_size=125
            )

    return artist

def get_discography(spotify, artist):
    """
    아티스트의 모든 발매를 가져옵니다.

    발매는 싱글, EP, 미니 앨범 또는 앨범입니다. Spotify는 단순히 모든 "앨범"이라고 부릅니다.
    
    아티스트가 피쳐링한 발매도 제공됩니다.
    예시: Sour Candy <https://open.spotify.com/album/6y6lP1WRfqEhv8RLy4ufZB>`는 레이디 가가의 노래지만 블랙핑크가 피처링

    Spotify는 또한 동일한 앨범의 많은 복제본을 만듭니다. 확장된 앨범이나 나중에 트랙을 추가한 앨범이 있을 수 있습니다.
    이 각각은 동일한 앨범의 복제본을 만듭니다.
    따라서 이 기능은 또한 중복을 제거하여 음반을 정리하려고 합니다.

    전달인자:
      - spotify: Spotify 인스턴스
      - artist: 단일 아티스트에 대한 모든 데이터를 포함하는 딕셔너리

    반환값:
      업데이트된 음반 세부 정보가 포함된 딕셔너리
    """

    print("[{}]에서 ({})의 음반 가져오는중...".format(module, artist["name"])) #Spotify에서 artist의 음반 가져오는중...

    # 앨범 세부정보
    albumResults = spotify.artist_albums(artist["uri"], limit=50)
    albumResults = albumResults['items']
    z = 0


    # 앨범 반복
    collection = []
    for album in albumResults:

        # 트랙 세부정보
        trackResults = spotify.album_tracks(album['id'])
        trackResults = trackResults['items']
        
        ## 트랙 반복
        tracks = []
        for track in trackResults:
            
            artists_names =[]
            artists_ids = []
            
            for artist_track in track['artists']:
                artists_names.append(artist_track['name'])
                artists_ids.append(artist_track['id'])
            
            ## 트랙 데이터 추출 및 데이터베이스 채우기
            if artist["id"] in artists_ids:
                z+=1
                tracks.append({'name':track['name'],
                                'id': track['id']}
                                )

        if album['album_group'] != 'appears_on':
            collection.append({'name':album['name'],
                                'id': album['id'],
                                'release_date':album['release_date'],
                                'total_tracks':album['total_tracks'],
                                'type':album['album_group'],
                                'image':album['images'][0]['url'],
                                'tracks': tracks}
                                )
        else:
            collection.append({'name':album['name'],
                                'id': album['id'],
                                'release_date':album['release_date'],
                                'total_tracks':album['total_tracks'],
                                'type':album['album_group'],
                                'image':album['images'][0]['url'],
                                'artist_collab':album['artists'][0]['name'],
                                'tracks': tracks}
                                )
    
    print("[{}]에서 ({})의 노래를 {}개 불러왔습니다.".format(module, artist["name"], z)) 

    # 중복 되는 노래 제거
    seen = set()
    result = []
    z = 0

    for album in collection:
        key = album['name']
        if key in seen:
            continue

        result.append(album)
        z += 1
        seen.add(key)

    print("[{}]에서 ({})는 {}개 발매했습니다. (싱글/EPs/앨범)".format(module, artist["name"], z))
    return result

def check_new_songs(artist, collection, hashtags):
    """
    신곡이 있는지 확인

    그것은 아티스트의 오래된 음반을 새로운(이미 가져온) 음반과 비교합니다.
    아티스트의 신곡이나 피처링이 있으면 트윗합니다. 

    전달인자:
      - artist: 단일 아티스트에 대한 모든 데이터를 포함하는 딕셔너리
      - collection: 아티스트의 모든 업데이트된 디스코그래피가 포함된 딕셔너리
      - hashtags: 트윗에 추가할 해시태그

    반환값:
      업데이트된 음반 세부 정보가 포함된 아티스트 딕셔너리
    """
    print("[{}]에서 ({})의 새로운 노래 체크중...".format(module, artist["name"]))

    # 음반이 비어 있는지 확인 건너뛰기
    if "discography" in artist:
      old = artist["discography"]

      for album in collection:
          found = False
          for old_album in old:
              if album["name"] == old_album["name"]:
                  found = True
                  break
          if not found:
              if album["type"] != 'appears_on':
                  twitter_post_image(
                      "{}가 Spotify에서 새로운 {}을 발매했습니다. : {}\n{}\n{}".format(artist["name"], album["type"], album["name"], link_album(album["id"]), hashtags),
                      download_image(album["image"]),
                      None
                      )
              else:
                  twitter_post("{} 의 앨범 {} 의 신곡 {} 이 발매되었습니다. feat.{}\n{}\n{} #spotify".format(artist["name"], album["artist_collab"], album["name"], album["tracks"][0]["name"], link_album(album["id"]), hashtags))
      
    artist["discography"] = collection
    return artist

def link_album(album_id):
    """
    앨범에 대한 링크 생성

    전달인자:
    album_id: 앨범의 id

    반환값:
    Spotify의 해당 앨범에 대한 링크
    """
    return "https://open.spotify.com/album/" + album_id

def link_artist(artist_id):
    """
    아티스트에 대한 링크 생성

    전달인자:
    artist_id: 아티스트 id

    Returns:
    Spotify의 해당 아티스트 링크
    """
    return "https://open.spotify.com/artist/" + artist_id

def spotify_data(group):
    """
    모든 Spotify 관련 작업을 실행합니다.

    그룹 전체 및 단일 아티스트에 대한 Spotify의 데이터를 스크랩합니다.

    전달인자:
    group: 긁을 그룹의 데이터가 있는 딕셔너리

    반환값:
    업데이트된 데이터가 있는 동일한 그룹 딕셔너리
    """
    print("[{}] 작업 실행중...".format(module))
    spotify = login()

    group["spotify"] = get_artist(spotify, group["spotify"], group["hashtags"])
    collection = get_discography(spotify, group["spotify"])
    group["spotify"] = check_new_songs(group["spotify"], collection, group["hashtags"])

    for member in group["members"]:
        if "spotify" in member:
            member["spotify"] = get_artist(spotify, member["spotify"], member["hashtags"])
            collection = get_discography(spotify, member["spotify"])
            member["spotify"] = check_new_songs(member["spotify"], collection,  member["hashtags"])

    print()

    return group


    
    