#coding=utf-8
import re
import requests
import time
from bs4 import BeautifulSoup
import os
import zipfile,os.path

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)

link = 'https://wapiprod.pakingtek.com/Dev/api/app/downloadLog.php#'+time.strftime("%Y%m%d", time.localtime())
print(link)

r = requests.get(link)

downloadList = []

soup = BeautifulSoup(r.text, 'html.parser')
all_hrefs = soup.find_all('a')
all_links = [link.get('href') for link in all_hrefs]
zip_files = [dl for dl in all_links if dl and '.zip' in dl]
print(zip_files)
for i in range(0,len(zip_files)):
    if "_"+time.strftime("%Y%m%d", time.localtime())+"_" in zip_files[i] and "IOS" in zip_files[i]:
        downloadList.append(zip_files[i])

download_folder = 'LogFile/'+time.strftime("%Y%m%d", time.localtime())

if not os.path.exists(download_folder):
    os.makedirs(download_folder)

count = 0;
for zip_file in downloadList:
    full_url = zip_file
    r = requests.get(full_url)
    zip_filename = os.path.basename(zip_file)
    dl_path = os.path.join(download_folder, zip_filename)
    log_path = os.path.join(download_folder, zip_filename.replace(".zip",".log"))
    print(log_path)
    if os.path.exists(log_path) == False :
        with open(dl_path, 'wb') as z_file:
            print("Download log:"+zip_filename)
            z_file.write(r.content)
    else:
        print("NO FILES to Download")





