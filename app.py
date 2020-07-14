import sys, requests, json, re, urllib.parse, urllib.request
from pathlib import Path

# Other Links
#https://i.instagram.com/api/v1/feed/reels_tray/ User feed Stories
#https://i.instagram.com/api/v1/feed/user/{}/reel_media/ Specific user stories
#https://graph.facebook.com/{}/picture?type=large&width=4000&height=4000
#https://www.instagram.com/graphql/query/?query_hash=d4d88dc1500312af6f937f7b804c68c3&variables={"user_id":"546316079","include_chaining":true,"include_reel":true,"include_suggested_users":false,"include_logged_out_extr
#https://www.instagram.com/graphql/query/?query_hash=7223fb3539e10cad7900c019401669e7&variables={"only_stories":true,"stories_prefetch":false,"stories_video_dash_manifest":false}


print("""
==========================================
====| 1) HD profile picture = 1     |=====
====| 2) Specific photo = 2         |=====
====| 3) Specific photos count      |=====
====| 4) All photos                 |=====
====| 5) Specific Story             |=====
==========================================
""")
mode = input("Mode: ")

#Set your own cookie here
headers = {
                'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00; 828x1792; 190542906)',
                'cookie': ''
            }

def main():
    if mode == '1':
        getHD()
    elif mode =='2':
        getSP()
    elif mode == '3':
        getAllP(m=0)
    elif mode == '4':
        getAllP()
    elif mode == '5':
        getStory()

#Get HD profile picture using user name
def getHD():
    #enter user name
    user_name = input("UserName: ")
    url = "https://www.instagram.com/{}/?__a=1"
    #making endpoint request to get user data by user name
    r = requests.get(url=url.format(user_name))
    #checking if response is ok 
    if r.status_code == 200:
        #reading response as json
        data = r.json()
        #getting user id
        user_id = data['graphql']['user']['id']
        url = "https://i.instagram.com/api/v1/users/{}/info/"
        #making request to get user data using user id (mode data) 
        r = requests.get(url=url.format(user_id), headers=headers)
        if r.status_code == 200:
            data = r.json()
            hd_profile = data['user']['hd_profile_pic_url_info']['url']
            #making directory named (user name) if not exist
            Path(user_name).mkdir(parents=True, exist_ok=True)
            #saving user profile picture in that directory
            urllib.request.urlretrieve(hd_profile, "{}/{}.jpg".format(user_name, user_name))
            print("Done")
    #if there is no user name exist
    elif r.status_code == 404:
        print("No such username")
    else:
        print("Something went wrong")

#downloading specific picture using its link or shortcode
def getSP():
    shortcode = input("Link or shortcode: ")
    #searching for shorcode in link using regex
    shortcode = re.search(r"^(?:.*\/p\/)([\d\w\-_]+)", shortcode).group(1)
    url = "https://www.instagram.com/p/{}/?__a=1"
    r = requests.get(url=url.format(shortcode), headers=headers)
    if r.status_code == 200:
        data = r.json()
        photo = data['graphql']['shortcode_media']['display_url']
        user_name = data['graphql']['shortcode_media']['owner']['username']
        Path(user_name).mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(photo, "{}/{}.jpg".format(user_name, shortcode))
        print("Done")
    elif r.status_code == 404:
        print("No such photo, Make sure the url is right")
    else:
        print("Something went wrong")

#get all account images or specific amount 
def getAllP(m=1):
    user_name = input("UserName: ")
    if m == 0:
        maxP = input("How many photoes: ")
    url = "https://www.instagram.com/{}/?__a=1"
    r = requests.get(url=url.format(user_name))
    if r.status_code == 200:
        data = r.json()
        user_id = data['graphql']['user']['id']
        #intiating cursor for next page
        cursor = ''
        url = "https://www.instagram.com/graphql/query/?query_id=17880160963012870&id={}&first=50&after={}"
        #image counter
        count = 0
        while True:
            r = requests.get(url=url.format(user_id, cursor), headers=headers)
            if r.status_code == 200:
                data = r.json()
                data = data['data']['user']['edge_owner_to_timeline_media']
                for image in data['edges']:
                    #if its image
                    if image['node']['__typename'] == 'GraphImage':
                        Path(user_name).mkdir(parents=True, exist_ok=True)
                        urllib.request.urlretrieve(image['node']['display_url'], "{}/{}.jpg".format(user_name, image['node']['id']))
                        count += 1
                        print(str(count) + "- " + str(image['node']['id']) + " ==> Done")
                        #if user provided amount (limit/max)
                        if 'maxP' in locals():
                            #if downloaded images equal max
                            if str(count) == maxP:
                                #end
                                sys.exit()
                    #if its album or slider
                    elif image['node']['__typename'] == 'GraphSidecar': 
                        url = "https://www.instagram.com/graphql/query/?query_hash=72c1679c31e5f6570569a249eccadbd2&variables=%7B%22shortcode%22%3A%22{}%22%7D"
                        r1 = requests.get(url=url.format(image['node']['shortcode']), headers=headers)
                        if r.status_code == 200:
                            data1 = r1.json()
                            data1 = data1['data']['shortcode_media']['edge_sidecar_to_children']
                            for image1 in data1['edges']:
                                if image1['node']['__typename'] == 'GraphImage':
                                    Path(user_name).mkdir(parents=True, exist_ok=True)
                                    urllib.request.urlretrieve(image1['node']['display_url'], "{}/{}.jpg".format(user_name, image1['node']['id']))
                                    count += 1
                                    print(str(count) + "- " + str(image1['node']['id']) + " ==> Done")
                                    if 'maxP' in locals():
                                        if str(count) == maxP:
                                            sys.exit()
                        else:
                            print("Something went wrong")
                            sys.exit()
                #if there is another page go for it
                if data['page_info']['has_next_page']:
                        cursor = data['page_info']['end_cursor']
                        continue
                else:
                    print("Total = " + str(count))
                    return
                
    elif r.status_code == 404:
        print("No such username")
        getAllP()
    else:
        print("Something went wrong")

#downloading specific story using its link
def getStory():
    story_link = input("Story link: ")
    user_name = re.search(r"^(?:.*\/stories\/)([\d\w\-_.]+)\/(\d+)", story_link).group(1)
    story_id = re.search(r"^(?:.*\/stories\/)([\d\w\-_.]+)\/(\d+)", story_link).group(2)
    url = "https://www.instagram.com/{}/?__a=1"
    r = requests.get(url=url.format(user_name))
    if r.status_code == 200:
        data = r.json()
        user_id = data['graphql']['user']['id']
        url = 'https://www.instagram.com/graphql/query/?query_hash=de8017ee0a7c9c45ec4260733d81ea31&variables=%7B%22reel_ids%22%3A%5B%22{}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%2C%22show_story_viewer_list%22%3Atrue%2C%22story_viewer_fetch_count%22%3A50%2C%22story_viewer_cursor%22%3A%22%22%7D'
        r = requests.get(url=url.format(user_id), headers=headers)
        if r.status_code == 200:
            data = r.json()
            stories = data['data']['reels_media'][0]['items']
            #itirating over stories searching for that story
            for story in stories:
                if story['id'] == story_id:
                    #if its not video
                    if not story['is_video']:
                        print(story['display_resources'][2]['src'])
                        Path(user_name).mkdir(parents=True, exist_ok=True)
                        urllib.request.urlretrieve(story['display_resources'][2]['src'], "{}/{}.jpg".format(user_name, user_id))
                    #if its video
                    else: 
                        print(story['video_resources'][len(story['video_resources'])-1]['src'])
                        Path(user_name).mkdir(parents=True, exist_ok=True)
                        urllib.request.urlretrieve(story['video_resources'][len(story['video_resources'])-1]['src'], "{}/{}.mp4".format(user_name, user_id))
    elif r.status_code == 404:
        print("No such username")
        getStory()
    else:
        print("Something went wrong")

if __name__ == '__main__':
    main()