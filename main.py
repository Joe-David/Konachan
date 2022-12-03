#inport async packages
import aiohttp
import asyncio

import numpy as np
import sys
from lxml import etree
import time
import os
from pathlib import Path
import yaml


empty_img_list = []


try:
    with open("config.yml","r") as f:
        #load config
        config = yaml.safe_load(f)

        print("\033[36m[INFO]\033[0m" + " load config")


        folder_path = config['folder_path']['default_path']
        headers = config['headers']
        proxy_enable = config['proxy']['enable']
        empty_file_path = config['file_path']['empty_file_path']


        print("\033[36m[INFO]\033[0m" + " load config[OK]\n")


        if proxy_enable == "on":
            proxy = config['proxy']['http']
            print("\033[36m[INFO]\033[0m" + " proxy[on]\n")

        else:
            print("\033[36m[INFO]\033[0m" + " proxy[off]\n")

        f.close()

except:
    print("\033[91m[WARNING]\033[00m" + " load config[Error]")
    print("\033[91m[WARNING]\033[00m" + " Exit")
    exit()


async def init(folder_path,empty_file_path):
    t1 = time.time()
    ##check the folder

    print("\033[36m[INFO]\033[0m" + " Checking folder\n")
    if not os.path.exists(folder_path):
        print("\033[36m[INFO]\033[0m" + " There wasn't the folder" + "["+ folder_path + "]")
        print("\033[36m[INFO]\033[0m" + " Create the folder" + "[" + folder_path + "]")
        os.mkdir(folder_path)
    else:
        print("\033[36m[INFO]\033[0m" + " The folder has been created" + "[" + folder_path + "]")
        pass

    
    t2 = time.time()
    use_time = str(t2-t1) + "s"

    print("\033[36m[INFO]\033[0m" + " init folder[OK]" + " use time:" + use_time + "\n")

    ##check the empty_file.txt
    print("\033[36m[INFO]\033[0m" + " Check the empty_file\n")
    if not os.path.exists(empty_file_path):
        print("\033[36m[INFO]\033[0m" " There wasn't the file" + "[" + empty_file_path + "]")
        print("\033[36m[INFO]\033[0m" + " Create the file" + "[" + empty_file_path + "]")
        Path(empty_file_path).touch()

    else:
        print("\033[36m[INFO]\033[0m" + " The file has been created" + "[" + empty_file_path + "]")
        pass


    t2 = time.time()
    use_time = str(t2-t1) + "s"
    print("\033[36m[INFO]\033[0m" + " init file[OK]" + " use time:" + use_time + "\n")


async def init_img_list():
    print("\033[36m[INFO]\033[0m" + " init img list")

    web_url = "https://konachan.com/post"


    async with aiohttp.ClientSession() as session:
        if proxy_enable == "on":
            async with session.get(url=web_url,headers=headers,proxy=proxy) as response:

                html_response = await response.text()
                data = etree.HTML(html_response)
                latest_img = str(data.xpath('//*[@id="post-list-posts"]/li/@id')[0]) ##get the latest img id
                total_img = int(latest_img.split("p",1)[1])
        else:
            async with session.get(url=web_url,headers=headers) as response:

                html_response = await response.text()
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


async def get_html(web_url):
    async with aiohttp.ClientSession() as session:
        if proxy_enable == 'on':
            response = await session.get(url=web_url,headers=headers,proxy=proxy)
        else:
            response = await session.get(url=web_url,headers=headers)

        html_response = await response.read()

        return html_response


async def fetch_img(img_url):
    async with aiohttp.ClientSession() as session:
        if proxy_enable == 'on':
            response = await session.get(url=img_url,headers=headers,proxy=proxy)
        else:
            response = await session.get(url=img_url,headers=headers)

        img_content = await response.read()
        return img_content

async def get_img_url(img_id):

    web_url = "https://konachan.com/post/show/" + str(img_id)

    html_response = await get_html(web_url=web_url)
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



async def save_img(folder_path,file_name,img_content):
    
    try:
        with open(folder_path + "/" + file_name,"wb") as f:
            f.write(img_content)
            f.close()
    
    except IOError as e:
        print(e)
        pass


async def generate_empty_img_list(img_status,img_id):
    empty_file_name = img_id + ".jpg"
    if img_status == "empty":
        empty_img_list.append(empty_file_name)
        return empty_img_list
    else:
        pass


async def download(img_id):
    t1 = time.time()

    img = await get_img_url(img_id)
    img_status = img[0]
    file_name = img_id + ".jpg"


    if img_status == "empty":
        print("\033[36m[INFO]\033[0m" + " img" + "[" + file_name + "]" + " does not exists")
        empty_img_list = await generate_empty_img_list(img_status,img_id)
        if len(empty_img_list) >= 4:
            with open("empty_file.txt","a") as f:
                for file_name in empty_img_list:
                    f.write(file_name + "\n")
                empty_img_list.clear()
                f.close()
                pass

    else:
        img_url = img[1]
        img_content = await fetch_img(img_url)
        img_size = str(sys.getsizeof(img_content) / 1024) + "Kb"

        await save_img(folder_path,file_name,img_content)
        t2 = time.time()
        use_time = str(t2-t1) + "s"
        print("\033[36m[INFO]\033[0m" + " Download the img" + "[" + file_name + "] " + img_size + " " + use_time)



async def downloader1():
    img_list = await init_img_list()
    img_list = np.array_split(np.array(img_list),4)

    for img_name in img_list[0]:
        img_id = img_name.split(".",2)[0]
        await download(img_id)


async def downloader2():
    img_list = await init_img_list()
    img_list = np.array_split(np.array(img_list),4)

    for img_name in img_list[1]:
        img_id = img_name.split(".",2)[0]
        await download(img_id)

async def downloader3():
    img_list = await init_img_list()
    img_list = np.array_split(np.array(img_list),4)

    for img_name in img_list[2]:
        img_id = img_name.split(".",2)[0]
        await download(img_id)


async def downloader4():
    img_list = await init_img_list()
    img_list = np.array_split(np.array(img_list),4)

    for img_name in img_list[3]:
        img_id = img_name.split(".",2)[0]
        await download(img_id)


task = [
    init(folder_path,empty_file_path),
    downloader1(),
    downloader2(),
    downloader3(),
    downloader4(),
]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*task))
