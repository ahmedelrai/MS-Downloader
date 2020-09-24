import requests
import json
import re
from tqdm import tqdm
import os
import time

def main():
    print('''
   __  __    _____   _____                      _                 _                       
 |  \/  |  / ____| |  __ \                    | |               | |                      
 | \  / | | (___   | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __             
 | |\/| |  \___ \  | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|            
 | |  | |_ ____) | | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |               
 |_|  |_(_)_____/  |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|               
      _                      _                        _   _    _       _                 
     | |               /\   | |                      | | | |  | |     | |                
     | |__  _   _     /  \  | |__  _ __ ___   ___  __| | | |__| | __ _| |_ ___ _ __ ___  
     | '_ \| | | |   / /\ \ | '_ \| '_ ` _ \ / _ \/ _` | |  __  |/ _` | __/ _ \ '_ ` _ \ 
     | |_) | |_| |  / ____ \| | | | | | | | |  __/ (_| | | |  | | (_| | ||  __/ | | | | |
     |_.__/ \__, | /_/    \_\_| |_|_| |_| |_|\___|\__,_| |_|  |_|\__,_|\__\___|_| |_| |_|
             __/ |                                                                                                                                 
''')
    print('\n')
    requested_session = input("Enter Session Title/Link/ID: ")
    print('\n')
    get_data(requested_session)

def get_data(requested_session):

    response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts")
    data = response.json()

    sessions_list = []
    for obj in data:
        obj_title = obj['title']['rendered']
        obj_url = obj['link']
        obj_id = obj['id']
        sessions_list.append({'title':obj_title,'url':obj_url,'id':obj_id})

    pattern = re.compile("(?<=href=')(.*?)(?=\')")
    pattern2 = re.compile('(?<=href=")(.*?)(?=\")')

    for session in sessions_list:
        if requested_session.lower() == session['title'].lower():
            session_response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts/"+str(session['id']))
            session_data = session_response.json()
            session_content = session_data['content']['rendered']
            session_urls = pattern.findall(session_content)
            proccess_urls(session_urls)
            break

        elif requested_session == session['url']:    
            session_response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts/"+str(session['id']))
            session_data = session_response.json()
            session_content = session_data['content']['rendered']
            session_urls = pattern.findall(session_content) or pattern2.findall(session_content)
            proccess_urls(session_urls)           
            break

        elif requested_session == session['id']:    
            session_response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts/"+str(session['id']))
            session_data = session_response.json()
            session_content = session_data['content']['rendered']
            session_urls = pattern.findall(session_content)
            proccess_urls(session_urls)
            break
    else:
        print('Session is not Found')
        time.sleep(3)
        os.system('cls||clear')
        main()


def proccess_urls(urls):
    for url in urls:
        print(url.split('/')[-1])
        downloader(url)

def downloader(url):
    chunk_size = 1024
    url = url
    title = url.split('/')[-1]
    r = requests.get(url,stream=True)
    total_size = int(r.headers['content-length'])
    ext = r.headers['content-type'].split('/')[1]
    with open(title,'wb') as f:
        for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size),total=total_size/chunk_size,unit='KB'):
            f.write(data)
    print('================================')
    

if __name__ == "__main__":
    main()