#import packages

import requests
import os
import sys
import yaml
from pathlib import Path
from lxml import etree

empty_img_list = []

try:
    with open("config.yml","r") as f:
        #load config
        print("\033[36m[INFO]\033[0m" + " load config")
        config = yaml.safe_load(f)
        folder_path = config['folder_path']['default_path']
        headers = config['headers']
        proxies_enable = config['proxies']['enable']
        empty_file_path = config['file_path']['empty_file_path']


        print("\033[36m[INFO]\033[0m" + " load config[OK]\n")


        if proxies_enable == "on":
            proxies = config['proxies']
            print("\033[36m[INFO]\033[0m" + " proxy[on]\n")

        else:
            print("\033[36m[INFO]\033[0m" + " proxy[off]\n")

        f.close()

except:
    print("\033[91m[WARNING]\033[00m" + " load config[Error]")
    print("\033[91m[WARNING]\033[00m" + " Exit")
    exit()



def init(folder_path,empty_file_path):
    ##check the folder

    print("\033[36m[INFO]\033[0m" + " Checking folder\n")
    if not os.path.exists(folder_path):
        print("\033[36m[INFO]\033[0m" + " There wasn't the folder" + "["+ folder_path + "]")
        print("\033[36m[INFO]\033[0m" + " Create the folder" + "[" + folder_path + "]")
        os.mkdir(folder_path)
    else:
        print("\033[36m[INFO]\033[0m" + " The folder has been created" + "[" + folder_path + "]")
        pass

    print("\033[36m[INFO]\033[0m" + " init folder[OK]\n")

    ##check the empty_file.txt
    print("\033[36m[INFO]\033[0m" + " Check the empty_file\n")
    if not os.path.exists(empty_file_path):
        print("\033[36m[INFO]\033[0m" " There wasn't the file" + "[" + empty_file_path + "]")
        print("\033[36m[INFO]\033[0m" + " Create the file" + "[" + empty_file_path + "]")
        Path(empty_file_path).touch()
        
    else:
        print("\033[36m[INFO]\033[0m" + " The file has been created" + "[" + empty_file_path + "]")
        pass
    
    print("\033[36m[INFO]\033[0m" + " init file[OK]\n")


def init_img_list():
    print("\033[36m[INFO]\033[0m" + " init img list")

    web_url = "https://konachan.com/post"
    html_response = request_html(web_url=web_url)
    data = etree.HTML(html_response)
    latest_img = str(data.xpath('//*[@id="post-list-posts"]/li/@id')[0]) ##get the latest img id
    total_img = int(latest_img.split("p",1)[1])


    plan_img_list = []
    for i in range(total_img):
        img_name = str(total_img - i) + ".jpg"
        plan_img_list.append(img_name)

    exists_img_list = os.listdir(folder_path) ##get exists_img_list of downloaded imgs
    with open("empty_file.txt","r") as f:
        empty_img_list = list(f.read())
        f.close()
    
    img_list = list(set(plan_img_list) - set(exists_img_list) - set(empty_img_list))

    empty_img_list.clear()
    print("\033[36m[INFO]\033[0m" + " init img list[OK]\n")

    return img_list


def request_html(web_url):
    if proxies_enable == "on":
        html_response = requests.get(url=web_url,headers=headers,proxies=proxies).text
        return html_response
    else:
        html_response = requests.get(url=web_url,headers=headers).text
        return html_response


def fetch_img(img_url):
    if proxies_enable == "on":
        img_content = requests.get(url=img_url,headers=headers,proxies=proxies).content
        return img_content
    else:
        img_content = requests.get(url=img_url,headers=headers).content
        return img_content



def get_img_url(img_id):
    base_url = "https://konachan.com/post/show/" + str(img_id)

    html_response = request_html(web_url=base_url)
    data = etree.HTML(html_response)

    #check if the img does not exist
    img_url_list = data.xpath('//img[@id="image"]/@src')
    img_url_list_size = len(img_url_list)

    img_status = "exists"
    if img_url_list_size == 0:
        img_url = "empty"
        img_status = "empty"
        return img_status,img_url
    else:
        img_url = img_url_list[0]
        return img_status,img_url


def save_img(folder_path,file_name,img_content):

    img_size = str(sys.getsizeof(img_content) / 1024) + "Kb"
    try:
        with open(folder_path + "/" + file_name,"wb") as f:
            print("\033[36m[INFO]\033[0m" + " Download the img" + "[" + file_name + "] " + img_size)
            f.write(img_content)
            f.close()
    except IOError as e:
        print(e)
        pass


def generate_empty_img_list(img_status,img_id):
    empty_file_name = img_id + ".jpg"
    if img_status == "empty":
        empty_img_list.append(empty_file_name)
        return empty_img_list
    else:
        pass


def download_img(img_name):
    file_name = img_name
    img_id = file_name.split(".",1)[0]

    img = get_img_url(img_id)
    img_status = img[0]

    if img_status == "empty":
        print("\033[36m[INFO]\033[0m" + " img" + "[" + file_name + "]" + " does not exists")
        empty_img_list = generate_empty_img_list(img_status,img_id)
        if len(empty_img_list) >= 4:
            with open("empty_file.txt","a") as f:
                for file_name in empty_img_list:
                    f.write(file_name + "\n")
                empty_img_list.clear()
                f.close()
        pass

    else:
        img_url = img[1]
        img_content = fetch_img(img_url)
        save_img(folder_path,file_name,img_content)


def main():
    init(folder_path,empty_file_path)
    img_list = init_img_list()
    for img_id in img_list:
        download_img(img_id)

if __name__ == "__main__":
    main()
