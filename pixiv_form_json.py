# -*- coding: utf-8 -*-

import json
import time
from rdflib import NoElementException
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime


class GetIamgeList:
    def __init__(self) -> None:
        self.prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
                'permissions.default.stylesheet': 2,
                # 'javascript': 2
            }
        }
        self.headers = {
            'Referer': 'https://www.pixiv.net/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self.proxies = {
            "http": "127.0.0.1:7890",
            "https": "127.0.0.1:7890",
        }
        self.url = "https://www.pixiv.net/ranking.php?mode=male"
        self.url2 = 'https://www.pixiv.net/artworks/{}'
        self.url3 = 'https://www.pixiv.net/ranking.php?mode=male&p={}&format=json'
        self.jsonName = 'foot.json'
        self.savedir = './pix'
        self.result_imgs = []

        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', self.prefs)
        options.add_argument(r"user-data-dir=C:\Users\flan\AppData\Local\Google\Chrome\User Data")
        self.driver = webdriver.Chrome(options=options)

        self.mkSaveDir()

    def mkSaveDir(self):
        if not os.path.exists(self.savedir):
            os.makedirs(self.dir)

        if not os.path.exists(self.savedir + '/' + self.jsonName):
            os.makedirs(self.savedir + '/' + self.jsonName)

    def readJson(self):
        with open(f'./{self.jsonName}','r') as f:
            json_data = json.load(f)
            return json_data

    def getImages(self):
        json_data = self.readJson()
        res_tmp = []
        for r in json_data['body']['illusts']:
            if r.get('id') is not None:
                res_tmp.append(r['id'])
        for r in json_data['body']['nextIds'] :
            res_tmp.append(r)
        self.result_imgs = res_tmp

    def saveIamge(self, img_url: str, res):
        with open(self.savedir + '/' + self.jsonName + '/{}'.format(img_url.split('/')[-1]), 'wb') as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)

    def singleImagePageDownload(self,img_url):
        res = self.requestGetImage(img_url)
        self.saveIamge(img_url, res)

    def getImageUrlByRe(self,img_url):
        pattern = re.compile(r'(https://i\.pximg\.net/.+?)_p\d_(.+?\.jpg)')
        match = pattern.match(img_url)
        return match.group(1),match.group(2)

    def requestGetImage(self,i_url):
        for i in range(5):
            try:
                res = requests.get(i_url, headers=self.headers, proxies=self.proxies)
                return res 
            except:
                time.sleep(60)
        raise Exception("下载出错，尝试下载失败")


    def mutileImagePageDownload(self,number,img_url):
        r1,r2 = self.getImageUrlByRe(img_url)
        for i in range(int(number)):
            i_url = r1 + f'_p{i}_' + r2
            res = self.requestGetImage(i_url)
            self.saveIamge(i_url, res)

    def getAllPageAndImgUrl(self):

        bs4 = BeautifulSoup(self.driver.page_source, features="lxml", from_encoding='utf-8')
        try:
            img_tag = bs4.find('div', class_='sc-1qpw8k9-0 gTFqQV').find('img')
            img_url = img_tag['src']
        except:
            return None,None
        try:
            number_element = bs4.find('div', class_='sc-zjgqkv-1 cykQFD').find('span')
            number = number_element.text.split('/')[-1]

            return number,img_url
        except:
            return None,img_url


    def downLoadIamge(self):
        if len(self.result_imgs) == 0:
            return

        for i in self.result_imgs:
            self.driver.get(self.url2.format(str(i)))
            time.sleep(1)
            pageNumber,img_url = self.getAllPageAndImgUrl()
            if img_url ==None:
                continue
            if pageNumber == '' or pageNumber == None:
                self.singleImagePageDownload(img_url)
            else:
                self.mutileImagePageDownload(pageNumber,img_url)

    def start(self):
        self.getImages()
        self.downLoadIamge()


if __name__ == '__main__':
    g = GetIamgeList()
    g.start()
