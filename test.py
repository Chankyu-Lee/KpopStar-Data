import yaml
import pathlib

exists_file = pathlib.Path('data.yaml').exists()

if exists_file is False:
    name = input("그룹의 이름을 입력하세요: ")
    hashtags = input("해쉬태그를 입력하세요: ")
    spotify_id = input("spotify의 ID를 입력하세요: ")
    twitter_url = input("트위터의 url을 입력하세요: ")
    instagram_url = input("인스타그램 url을 입력하세요: ")
    youtube_name = input("youtube의 이름을 입력하세요: ")
    youtube_url = input("youtube의 url을 입력하세요: ")
   
    member = []
    check = 'Y'
    while check == 'Y':
        print("멤버들의 데이터를 입력받습니다.")
        member_name = input("멤버의 이름을 입력하세요: ")
        member_years = input("멤버의 나이를 입력하세요: ")
        member_birthday = input("멤버의 생일을 입력하세요: ")
        member_hashtags = input("해쉬태그를 입력하세요: ")
        member_instagram = input("멤버의 인스타 url을 입력하세요: ")

        member.append({
                    "name" : member_name,
                    "years" : member_years,
                    "birthday" : member_birthday,
                    "hashtags" : member_hashtags,
                    "instagram" : {
                        'url' : member_instagram
                    }
                })

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
                            'subs' : 0,
                            'total_views' : 0,
                            'videos' : None 
            },
            'members' : member
        }

    with open('data.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(dic, file, sort_keys=False, allow_unicode=True)


"""
with open('sample_data.yaml', encoding="utf-8") as file:
    group = yaml.load(file, Loader=yaml.FullLoader)
    print(group)

    str = {
            'name': 'BLACKPINK', 
            'hashtags': '#BLACKPINK #blinks @BLACKPINK', 
            'spotify': {'id': '41MozSoPIsD1dJM0CLPjZF', 'followers': 0}, 
            'twitter': {'url': 'blackpink'}, 
            'instagram': {'url': 'https://www.instagram.com/blackpinkofficial/'}, 
            'youtube': {
                'name': 'BLACKPINK', 
                'url': 'UCOmHUn--16B90oW2L6FRR3A', 
                'views_scale': 'B', 
                'videos_scale': 'B', 
                'subs': '0', 
                'total_views': '0', 'videos': None}, 
                'members': [{
                    'name': 'Jennie', 
                    'years': 25, 
                    'birthday': 
                    '18/05/1996', 
                    'hashtags': 
                    '#JENNIE #제니 #BLACKPINK @BLACKPINK', 
                    'instagram': {'url': 'https://www.instagram.com/jennierubyjane/'}
                    }]
        }
"""