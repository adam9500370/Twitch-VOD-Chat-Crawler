import requests # $ pip install requests
import json
import time
import datetime

vod_id = input('Please enter vod_id: (https://www.twitch.tv/{channel_name}/v/{vod_id})\n')

# test for getting vod's start & end time
test_start = '0'
url = "https://rechat.twitch.tv/rechat-messages?start=" + test_start + "&video_id=v" + vod_id # get web data
res = requests.get(url)
res.encoding = "utf-8"
content = res.text
json_content = json.loads(content) # decode json data
error_msg = json_content['errors'][0]['detail'] # {test_start} is not between {min_start} and {max_start}
min_start = error_msg.split()[4]
max_start = error_msg.split()[6]
vod_elapsed_time = int(max_start) - int(min_start)

# transform timestamp to datetime format
min_start_datetimestamp = datetime.datetime.fromtimestamp(int(min_start)).strftime('%Y-%m-%d %H:%M:%S')
max_start_datetimestamp = datetime.datetime.fromtimestamp(int(max_start)).strftime('%Y-%m-%d %H:%M:%S')
vod_elapsed_time_datetimestamp = datetime.timedelta(seconds=vod_elapsed_time)

# print data to file, column information splited by TAB (\t)
msg_file = open('rechat_message_' + str(vod_id), 'w', encoding='UTF-8')

msg_file.write("vod_start_time\t" + min_start_datetimestamp + "\t\t\t\t\t\n")
msg_file.write("vod_end_time\t" + max_start_datetimestamp + "\t\t\t\t\t\n")
msg_file.write("vod_elapsed_time\t" + str(vod_elapsed_time_datetimestamp) + "\t\t\t\t\t\n")
msg_file.write("\n")
msg_file.write("channel_name\ttimestamp\tuser_name\tuser_nickname\tis_mod\tis_subscriber\tchat_msg\n")

total_progress_start_time = time.time()
# update chat messages every 30 timestamps offset during vod_elapsed_time
for start in range(int(min_start), int(max_start)+1, 30):
	current_progress_start_time = time.time()
	
	url = "https://rechat.twitch.tv/rechat-messages?start=" + str(start) + "&video_id=v" + vod_id # get web data
	res = requests.get(url)
	res.encoding = "utf-8"
	content = res.text
	json_content = json.loads(content) # decode json data
	if ('data' in json_content) & (len(json_content['data']) > 0):
		for index in range(len(json_content['data'])):
			channel_name = json_content['data'][index]['attributes']['room']
			timestamp = json_content['data'][index]['attributes']['timestamp'] # ms
			user_name = json_content['data'][index]['attributes']['from']
			if 'display-name' in json_content['data'][index]['attributes']['tags']:
				user_nickname = json_content['data'][index]['attributes']['tags']['display-name']
			else:
				user_nickname = [None];
			is_mod = json_content['data'][index]['attributes']['tags']['mod']
			is_subscriber = json_content['data'][index]['attributes']['tags']['subscriber']
			chat_msg = json_content['data'][index]['attributes']['message']
			
			datetimestamp = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S') # 1 ms = 1/1000 s
			
			# write data, column information splited by TAB (\t)
			msg_file.write(channel_name + "\t")
			msg_file.write(datetimestamp + "\t")
			msg_file.write(user_name + "\t")
			if type(user_nickname) is str:
				msg_file.write(user_nickname + "\t")
			else:
				msg_file.write("\t") # null
			msg_file.write(str(is_mod) + "\t")
			msg_file.write(str(is_subscriber) + "\t")
			msg_file.write(chat_msg + "\n")
	
	crawling_progress = (start - int(min_start)) / (vod_elapsed_time) * 100
	print("crawling_progress: " + str(round(crawling_progress, 2)) + "%")
	current_progress_elapsed_time = time.time() - current_progress_start_time
	print("current_progress_elapsed_time: " + str(round(current_progress_elapsed_time, 3)))

total_progress_elapsed_time = time.time() - total_progress_start_time
total_progress_elapsed_datetime = datetime.timedelta(seconds=total_progress_elapsed_time)
print("\ntotal_progress_elapsed_datetime: " + str(total_progress_elapsed_datetime))
msg_file.close()

# URL linking to my crawled dataset:
# https://docs.google.com/spreadsheets/d/12etiCzG95lU8MNNVnxxe3mgQzItgvYxmK_xIbPJTsIQ/edit?usp=sharing
