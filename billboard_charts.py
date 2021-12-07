#!/usr/bin/env python3
import billboard
from datetime import date
from tweet import twitter_post

module = "Billboard"				#  module에 "Billboard" 문자열을 저장한다.

def billboard_data(group):
	"""group의 빌보드 차트를 가져옵니다.

	최신 데이터를 가져오는 데 필요한 모든 작업을 시작하고 결국 트윗 업데이트를 시작합니다.
	데이터는 하루에 한 번 업데이트됩니다.

    전달인자:
      - group: group에 대한 모든 데이터가 포함된 dictionary

    반환값:
      업데이트된 데이터가 있는 동일한 group dictionary
    """
	
	print("[{}] 시작하는중...".format(module))				# ex) [Billboard] 시작하는중...

	report = ""				# 빈 문자열을 저장한다.

	# 오늘 체크하지 않았다면 시작하세요. (If the check didn't run today, start it)
	if "billboard_check" not in group or group["billboard_check"] != date.today().strftime("%d-%m-%Y"):			# "billboard_check" 문자열이 group에 없거나, gorup의 "billboard_check" key 값이 오늘 날짜가 아니라면, (strftime()함수는 시간을 원하는 형식의 문자열로 출력하는 함수)

		chart = billboard.ChartData('hot-100')				# 빌보드 hot 100 차트 정보를 불러와 저장한다. (print(chart)하면 현재 hot100차트가 뜬다.)
		print("[{}] Hot 100 차트가 패치되었습니다.".format(module))				# [Billboard] Hot 100 차트가 패치되었습니다.
		report += get_artist_rank(group, chart)				# 차트에 group이 있다면 빈 문자열에 더한다. 없다면 그대로 빈 문자열이다.

		for artist in group["members"]:						# artist에 group의 "members" key에 해당하는 값을 대입하고,
			report += get_artist_rank(artist, chart)		# 차트에 artist가 있다면 빈 문자열에 더한다. 없다면 그대로 빈 문자열이다.

		group["billboard_check"] = date.today().strftime("%d-%m-%Y")			# gorup의 "billboard_check"에 오늘 날짜를 저장한다. "01-11-2021" ==> data.yaml 파일의 2005번줄에 저장된 것을 확인할 수 있다.

		if len(report) > 0:				# report 변수의 길이가 0보다 크다면,  ( = 차트에 들어갔다면,)
			report = "Today on #Billboard #Hot100:\n" + report + "\n" + group["hashtags"]			# "Today on #Billboard #Hot100:\n#1 How You Like That by BLACKPINK\n"+group["hashtags"] 
			twitter_post(report)		# tweet.py에 있는 twitter_post(message) 함수를 사용해 글 작성
		else:							# 아니라면, ( = 차트에 들어가있지 않다면, )
			print("[{}] 제공된 아티스트(들)에 대한 노래를 찾을 수 없습니다.".format(module))		# [Billboard] 제공된 아티스트(들)에 대한 노래를 찾을 수 없습니다.

	else:			# "billboard_check" 문자열이 group에 있거나, gorup의 "billboard_check" key 값이 오늘 날짜라면,
		print("[{}] 이미 오늘 체크했으므로, 스킵합니다.".format(module))			# [Billboard] 이미 오늘 체크했으므로, 스킵합니다.
		
	return group			# group 반환

def get_artist_rank(artist, chart):				# 현재 파일에서는 artist가 블랙핑크이다.
	"""빌보드 핫 100 차트에 진입하여 artist를 찾습니다.

    전달인자:
      - artist: 찾고 있는 예술가

    반환값:
	  차트에 있는 노래 목록을 포함하는 문자열(비워둘 수 있음)
    """
	report = ""					# 빈 문자열을 저장한다.

	for song in chart:			# song에 chart를 대입하고,
		if artist["name"].lower() in song.artist.lower():				# song의 artist에 artist의 "name"에 해당하는 value값(이름)이 있다면
			report += "#{} {} by {}\n".format(song.rank, song.title, song.artist)				# 빈 문자열에 "#1 How You Like That by BLACKPINK"을 더한다.(예시)
	
	return report				# 차트에 artist가 없다면 빈 문자열을, 있다면 위의 더해진 문자열 반환
