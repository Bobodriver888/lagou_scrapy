'''
scrapy 拉勾网
待完善：不够稳定，在爬取职位详情时，偶尔会出现302重定向
其它要点：
    post请求必须要携带cookie，cookie可以先get一个网页，然后session.cookies获取
    后面get可以不带cookies，先session取cookies，再requests请求（不能再用session否则容易302）
    Referer必须要准确
    爬取间隔时间要长一点，否则容易被拉入黑名单
'''
import  requests
from  selenium import webdriver
import re
import json
from lxml import etree
from requests import Session
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url='https://www.lagou.com/jobs/positionAjax.json?'
url_start = "https://www.lagou.com/jobs/list_运维?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labelWords=&suginput="
baseurl='https://www.lagou.com/jobs/{}.html?show={}'
params={
'px': 'default',
'gm': '50-150人,150-500人',
'city': '深圳',
'needAddtionalResult': 'false'
}

data={
'first': 'true',
'pn': 1,
'kd': 'Python'
}

headers = {
'Connection': 'close',
'Host': 'www.lagou.com',
'Origin': 'https://www.lagou.com',
'Content-Type': 'application/json;charset=UTF-8',
'Referer': 'https://www.lagou.com/jobs/list_Python/p-city_252-gm_3_4?px=default',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.26 Safari/537.36 Edg/81.0.416.16',
}

##如果职业详情request失败，可以尝试使用chromedriver模拟
def GetJobDetailByChrome(job_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  ##无头模式
    driver = webdriver.Chrome(options=options)
    driver.get(job_url)
    print(driver.find_element_by_xpath('//*[@id="job_detail"]/dd[1]/span').text)
    print(driver.find_element_by_xpath('//*[@id="job_detail"]/dd[1]/p').text)
    print(driver.find_element_by_xpath('//*[@id="job_detail"]/dd[2]/h3').text)
    details=driver.find_elements_by_xpath('//*[@id="job_detail"]/dd[2]/div/p')
    for detail in details:
        print(detail.text)
    driver.close()



def GetJobDetail(job_url,cookie):
    req=requests.get(url=job_url,headers=headers,verify=False,timeout=3)
    req.encoding = 'utf-8'
    if len(req.text)<10000:
        print('尝试用模拟浏览器获取')
        GetJobDetailByChrome(job_url)
        return None
    etree_html = etree.HTML(req.content)
    print(etree_html.xpath('string(//*[@id="job_detail"]/dd[1])').replace('\r', '').replace('\t', '').replace('\n\n', '\n').replace('\xa0', ' '))
    #print(etree_html.xpath('//*[@id="job_detail"]/dd[1]/p/text()'))
    print(etree_html.xpath('string(//*[@id="job_detail"]/dd[2])').replace('\r', '').replace('\t', '').replace('\n\n', '\n').replace('\xa0', ' '))
    #print(etree_html.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()'))
    return req.cookies

def main(pagenum):
    session = requests.Session()

    response = session.get(url=url_start, headers=headers, verify=False, timeout=3)

    cookie = response.cookies  # 为此次获取的cookies
    data['pn']=pagenum
    #print(data)
    response = requests.post(url=url, headers=headers, data=data, cookies=cookie, params=params, verify=False).text
    response = json.loads(response)

    joblist = response.get('content').get('positionResult').get('result')
    showId = response.get('content').get('showId')
    for job in joblist:
        print('公司:',job.get('companyFullName'))
        print('     公司简称:{},公司规模:{},薪资:{},公司领域:{},融资阶段:{},第一需求:{},第二需求:{},公司福利:{},上班城市:{},地区:{},地点:{}'\
              .format(job.get('companyShortName'),job.get('companySize'),job.get('salary'),job.get('industryField'),\
                      job.get('financeStage'),job.get('firstType'),job.get('secondType'),job.get('positionAdvantage'),\
                      job.get('city'),job.get('district'),job.get('businessZones')))
        positionId=job.get('positionId')
        joburl=baseurl.format(positionId,showId)
        #print('joburl=',joburl)
        cookies=GetJobDetail(joburl,cookie)
        time.sleep(10)
        print('\r')
        print('*'*100)
        print('\r')

if __name__ == '__main__':
    for pagenum in range(1,6): ##爬取前5页
        print('开始第{}页爬取'.format(pagenum))
        main(pagenum)
