#!/usr/bin/env python
# coding: utf-8
import time
import requests
from tqdm import tqdm
import os
import json
from random import uniform
from concurrent.futures import ThreadPoolExecutor
import random

DATA_DIRECTORY = "./dataset_on/"
TATGET_PATH = "./APKs_on/"

URL1 = 'https://d.apkpure.com/b/XAPK/'
URL2 = 'https://d.apkpure.com/b/APK/'

VERSION = '?version=latest'

LOOP_CTRL = 4
# IP_POOL = "Active_Proxy.txt"
SLEEP_TIME = 3
MAX_THREAD = 5

STOP_THRESHOLD = 100 * (1024 ** 2)  # e.g., 10 MB
stop_script = False

# Proxies = {
#      "http": "http://172.67.27.160:80",
# }

HEADERS = {}
IP_LISTS = []

def monitor_space():
    used_space = get_directory_size(TATGET_PATH)
    print(f"Used space: {used_space} bytes")
    if used_space > STOP_THRESHOLD:
        print("Space exceeded. Stopping script!")
        stop_script = True
        return stop_script
    else:
        stop_script = False
        return stop_script


def get_headers():

    header = random.choice(HEADERS)
    return header

def get_proxy():
    ip = random.choice(IP_LISTS)
    proxy = "http://" + str(ip[0])+ ":80"
    prox = {
        "http": proxy,
    }
    return prox


def get_directory_size(path='./APP/'):
    """Return the total size of the directory in bytes."""
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    return total


def json_walker(data_directory):
    json_files = []
    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(data_directory):
        for filename in filenames:
            # Check if the file has a .json extension
            if filename.endswith('.json'):
                full_path = os.path.join(dirpath, filename)
                json_files.append(full_path)

    return json_files


def assessment(file_path):  # evaluate valid app's numbers
    app_count = 0
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            #   get all valid apps' number
            valid_n = int(data.get("count", {}).get("valid"))
            app_count = app_count + valid_n
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
    return app_count


def read_each_json(file_path):
    """
    Extract item names  both valid_apps.

    Parameters:
    - data: Dictionary containing the JSON data

    Returns:
    - A list of tuples with item's key and its name field
    """

    results = []
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

            for key, value in data['apps'].items():
                # only donwload free apks
                # if value['price']==0 :
                #     results.append((key, value['name']))
                results.append((key, value['name']))
            return results
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")


def download(id, target_path):
    url1 = URL1 + id + VERSION
    url2 = URL2 + id + VERSION

    try:
        r = requests.get(url1, headers=get_headers(), proxies=get_proxy(), stream=True)
    except Exception as e:
        print(e)
        try:
            r = requests.get(url2, headers=get_headers(), proxies=get_proxy(), stream=True)
        except:
            return

    r.raise_for_status()

    total_size = int(r.headers.get('content-length', 0))
    chunk_size = 1024  # 1 KB

    if not os.path.exists(target_path):
        # If not, create the directory
        os.makedirs(target_path)
    file_path = os.path.join(target_path, id + '.xapk')

    # Download the file and save it chunk by chunk
    with open(file_path, 'wb') as f:
        for chunk in tqdm(r.iter_content(chunk_size), total=total_size // chunk_size, unit='KB'):
            if chunk:  # filter out keep-alive chunks
                f.write(chunk)
    # sleep for a while
    sleep_time = uniform(0, SLEEP_TIME)
    time.sleep(sleep_time)


def download_wrapper(m):
    round = 0
    while round < 3:
        try:
            print("Downloading " + str(m[0]) + " ...")
            download(m[0], TATGET_PATH)
            return
        except:
            print("Downloading " + str(m[0]) + " failed")
            round += 1


"""
    For further work, an IP pool is neccessary, but for test stage, it's not that urgent
"""
# def switch_id(id_pool):
#     with open("id_pool.txt",'r') as f:

if __name__ == '__main__':
    if not os.path.exists(TATGET_PATH):
        os.mkdir(TATGET_PATH)

    with open('headers1.json', 'r') as file:
        HEADERS = json.load(file)

    with open('ip_list.json', 'r') as file:
        IP_LISTS = json.load(file)

    # Get all json files
    json_paths = json_walker(DATA_DIRECTORY)
    print("Total json files: " + str(len(json_paths)))

    #   Evaluate workload
    # for iter in range(LOOP_CTRL):
    #     cur_path = json_paths[iter]
    #     counts = assessment(cur_path)

    # Open each file and get all valid names
    for i in tqdm(range(len(json_paths))):
        stop_script = monitor_space()
        if stop_script:
            print("Space exceeded. Stopping script!")
            break
        else:
            pass
        jsonpath = json_paths[i]
        app_urls = read_each_json(jsonpath)
        for m in app_urls:
            with ThreadPoolExecutor(max_workers=MAX_THREAD) as executor:
                executor.map(download_wrapper, app_urls)

    print("Download Completed!")