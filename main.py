#!/usr/bin/env python3
import sys
import yaml
import os
import pathlib

from utils import convert_num, display_num, download_image
from tweet import twitter_post, twitter_post_image, twitter_repost, set_test_mode
from birthdays import check_birthdays
from instagram import instagram_data
from youtube import youtube_data
from spotify import spotify_data
from billboard_charts import billboard_data


def load_group():
    """YAML 파일 data.yaml 을 읽어옵니다.
    group 에 대한 데이터는 스크립트와 동일한 디렉터리의 data.yaml 파일에 저장됩니다.
   
    반환값:
      group 에 대한 모든 정보가 포함된 dictionary
    """

    print("YAML 파일에서 데이터 불러오는 중...")
    
    with open('data.yaml', encoding="utf-8") as file:
        group = yaml.load(file, Loader=yaml.FullLoader)

        out = "{} 멤버 목록 : ".format(group["name"])
        for artist in group["members"]:
            out += artist["name"]
            out += " "
        print(out + "\n")
    
    
    return group

def write_group(group):
    """YAML 파일 data.yaml 에 씁니다.
    group 에 대한 데이터는 스크립트와 동일한 디렉터리의 data.yaml 파일에 저장됩니다.
    
    전달인자:
      group: group 에 대한 모든 정보가 포함된 dictionary
    """

    print("데이터를 YAML 파일에 저장하는 중...")
    with open('data.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(group, file, sort_keys=False, allow_unicode=True)

def createYAML():
    """YAML 파일 data.yaml 을 생성하고 초기 데이터를 입력 받아 저장합니다.
    data.yaml 파일이 생성되는 위치는 스크립트와 동일한 디렉터리 입니다.
    """

    name = input("그룹의 이름을 입력하세요: ")
    hashtags = input("해쉬태그를 입력하세요 (트윗에 추가됩니다): ")
    spotify_id = input(name + "의 spotify의 ID를 입력하세요: ")
    twitter_url = input(name + "의 트위터 계정 닉네임(@)을 입력하세요: ")
    instagram_url = input(name + "의 인스타그램 계정 url을 입력하세요: ")
    youtube_name = input(name + "의 youtube의 계정 이름을 입력하세요 (비워둘 수 있습니다): ")
    youtube_url = input(name + "의 youtube의 고유 ID를 입력하세요 (채널의 URL에서 찾을 수 있습니다): ")
   
    member = []
    check = 'Y'
    while check == 'Y':
        print("멤버들의 데이터를 입력받습니다.")
        member_name = input("멤버의 이름을 입력하세요: ")
        member_years = int(input(member_name + "의 나이를 입력하세요: "))
        member_birthday = input(member_name + "의 생일을 다음 양식으로 작성하세요 (DD/MM/YYYY): ")
        member_hashtags = input("해쉬태그를 입력하세요 (트윗에 추가됩니다): ")
        member_instagram = input(member_name + "의 인스타그램 계정 url을 입력하세요: ")

        check = input(member_name + "의 유튜브 계정을 추가하시겠습니까? (Y/N): ")

        if check == 'Y':
            member_youtube_name = input(member_name + "의 youtube의 계정 이름을 입력하세요 (비워둘 수 있습니다): ")
            member_youtube_url = input(member_name + "의 youtube의 고유 ID를 입력하세요 (채널의 URL에서 찾을 수 있습니다): ")
        else:
            member_youtube_url = None;
        
        check = input(member_name + "의 스포티파이 계정을 추가하시겠습니까? (Y/N): ")

        if check == 'Y':
            member_spotify_id = input(member_name + "의 spotify의 ID를 입력하세요: ")
        else:
            member_spotify_id = None;

        member_dic = {
                    "name" : member_name,
                    "years" : member_years,
                    "birthday" : member_birthday,
                    "hashtags" : member_hashtags,
                    "instagram" : {
                        'url' : member_instagram
                    },
                }

        if member_youtube_url is not None:
            member_dic["youtube"] = {
                            'name' : member_youtube_name,
                            'url' : member_youtube_url,
                            'views_scale' : "B",
                            'videos_scale' : "B",
                            'subs' : '0',
                            'total_views' : '0',
                            'videos' : None 
                    }
        
        if member_spotify_id is not None:
            member_dic["spotify"] = {
                            'id' : member_spotify_id,
                            'followers' : 0
                        }

        member.append(member_dic)

        check = input("멤버를 추가하시겠습니까? (Y/N): ")

    dic = {
            'name' : name,
            'hashtags' : hashtags,
            'spotify' : {
                            'id' : spotify_id,
                            'followers' : 0
            },
            'twitter' : {
                            'url' : twitter_url
            },
            'instagram' : {
                            'url' : instagram_url
            },
            'youtube' : {
                            'name' : youtube_name,
                            'url' : youtube_url,
                            'views_scale' : "B",
                            'videos_scale' : "B",
                            'subs' : '0',
                            'total_views' : '0',
                            'videos' : None 
            },
            'members' : member
        }

    with open('data.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(dic, file, sort_keys=False, allow_unicode=True)
    
    print("data.yaml 파일이 생성되었습니다.")
    print("data.yaml 파일에 데이터를 불러오는 작업이 실행됩니다.")
    print("test모드(tweet이 게시되지 않음)가 권장됩니다.")

def check_args():
    """명령줄에서 전달된 인자를 확인합니다.
    하나 이상의 파라미터를 전달하여 단일 모듈 source 를 비활성화할 수 있습니다.
    허용되는 실제 매개 변수는 다음과 같습니다.

    * `-no-instagram`: 인스타그램 source 를 비활성화합니다.  
    * `-no-youtube`: 유튜브 source 를 비활성화합니다.  
    * `-no-spotify`: Spotify source 를 비활성화합니다.   
    * `-no-birthday`: 생일 이벤트 source 를 비활성화합니다.   
    * `-no-twitter`: 트위터 source 를 비활성화합니다. (reposting 시에 사용)  
    * `-no-tweet` 은 실제로 활성화된 소스의 업데이트를 봇이 트윗하는 것을 방지합니다. 출력은 여전히 콘솔에서 볼 수 있습니다. 이것은 **테스트**에 매우 유용합니다.
    `-no-twitter`는 `-no-tweet`과 다르다는 것을 기억하세요
    
    반환값:
      모든 소스와 해당 상태를 포함하는 dictionary, write의 활성화 여부(True 또는 False)
    """

    source = {"instagram": True, "youtube": True, "spotify": True, "birthday": True, "twitter": True, "billboard": True}
    write = True

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-no-tweet":
                print("-no-tweet 매개 변수가 전달되었습니다!\nTest 모드가 활성화됨: 봇이 아무 것도 트윗하지 않습니다.")
                set_test_mode()
                
            if arg == "-no-instagram":
                print("-no-instagram 매개 변수가 전달되었습니다!")
                source["instagram"] = False
                
            if arg == "-no-spotify":
                print("-no-spotify 매개 변수가 전달되었습니다!")
                source["spotify"] = False
                
            if arg == "-no-youtube":
                print("-no-youtube 매개 변수가 전달되었습니다!")
                source["youtube"] = False
                
            if arg == "-no-birthday":
                print("-no-birthday 매개 변수가 전달되었습니다!")
                source["birthday"] = False

            if arg == "-no-billboard":
                print("-no-billboard 매개 변수가 전달되었습니다!")
                source["billboard"] = False
                
            if arg == "-no-twitter":
                print("-no-twitter 매개 변수가 전달되었습니다!")
                source["twitter"] = False
            
            if arg == "-no-write":
                print("-no-write 매개 변수가 전달되었습니다!")
                write = False

                
    print()
    return source, write

def set_args(source):
    """명령 줄 에서 입력받는 전달인자를 프로그램 내에서 설정합니다.
    상세 내용은 check_args() 메소드를 참고 하세요.
   
    전달인자:
      - source: 모든 소스와 해당 상태를 포함하는 dictionary
    """
    
    check = -1
    
    while check != '0' :
        print("비활성화할 모듈 source를 설정합니다.")
        print("선택할 모듈에 해당하는 값을 입력하세요.")
        print("인스타그램 : 1 \n유튜브 : 2 \n스포티파이 : 3 \n생일 : 4 \n트위터 : 5 \n빌보드 : 6 \n테스트(트윗 방지)모드 : 7 \nyaml 파일 쓰기 방지 모드 : 8 \n설정 종료 : 0")
        check = input()
        if check == '7':
                print("-no-tweet 매개 변수가 전달되었습니다!\nTest 모드가 활성화됨: 봇이 아무 것도 트윗하지 않습니다.")
                set_test_mode()
                
        if check == '1':
            print("-no-instagram 매개 변수가 전달되었습니다!")
            source["instagram"] = False
                
        if check == '3':
            print("-no-spotify 매개 변수가 전달되었습니다!")
            source["spotify"] = False
                
        if check == '2':
            print("-no-youtube 매개 변수가 전달되었습니다!")
            source["youtube"] = False
                
        if check == '4':
            print("-no-birthday 매개 변수가 전달되었습니다!")
            source["birthday"] = False

        if check == '6':
            print("-no-billboard 매개 변수가 전달되었습니다!")
            source["billboard"] = False
                
        if check == '5':
            print("-no-twitter 매개 변수가 전달되었습니다!")
            source["twitter"] = False
            
        if check == '8':
            print("-no-write 매개 변수가 전달되었습니다!")
            write = False

        if check == '0':
            print("설정을 종료합니다.")

if __name__ == '__main__':

    source, write = check_args()

    exists_file = pathlib.Path('data.yaml').exists()

    if exists_file is False:
        print("data.yaml 파일이 존재하지 않습니다.")
        answer = input("data.yaml 파일을 새로 생성하시겠습니까? (Y/N) : ")
        if (answer == 'Y'):
            createYAML()
    else:
        answer = input("data.yaml 파일을 새로 생성하시겠습니까? (Y/N) : ")
        if (answer == 'Y'):
            createYAML()

    answer = input("비활성화할 모듈을 설정하시겠습니까? (Y/N) : ")
    if (answer == 'Y'):
        set_args(source)
    
    group = load_group()

    if source["birthday"]:
        group = check_birthdays(group)
    
    if source["youtube"]: 
        group = youtube_data(group)
        
    if source["twitter"]:
        group = twitter_repost(group)
    
    if source["instagram"]:
        group = instagram_data(group)
    
    if source["spotify"]:
        group = spotify_data(group)

    if source["billboard"]:
        group = billboard_data(group)

    if write:
        write_group(group)
