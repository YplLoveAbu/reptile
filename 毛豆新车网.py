from fake_useragent import UserAgent
import re,requests
from selenium import webdriver
from lxml import etree
import pymysql

class Mysql():

    def __init__(self):
        self.count = 1
        #传建数据库连接对象
        self.conn = pymysql.connect(user='root',host='127.0.0.1',password='12345',database='maodou')
        self.cur = self.conn.cursor()

class MaoDou(Mysql):

    def __init__(self):
        Mysql.__init__(self)
        self.spider_name = '毛豆新车网'

    def __call__(self, *args, **kwargs):
        base_url = 'https://www.maodou.com/car/list/all/pg1?keyword='
        self.headers = {
            'User-Agent':UserAgent().random
        }
        html,html_xml = self.get_html(base_url,self.headers)
        max_page = self.get_max_page(html)
        self.get_data(max_page)


    def get_html(self,url,headers):
        html = requests.get(url,headers=self.headers).text
        html_xml = etree.HTML(html)
        # print(html)
        # print(html_xml)
        return html,html_xml

    def get_max_page(self,html):
        max_page = re.findall('{"page":(.*?),"link":"https:',html)[-1] if re.findall('{"page":(.*?),"link":"https:',html) else ''
        # print(max_page)
        return int(max_page)

    def get_data(self,max_page):
        #循环获取分页列表页面
        for page in range(1,max_page+1):
            #拼接url
            page_url = 'https://www.maodou.com/car/list/all/pg{}?keyword='.format(page)
            page_html,page_html_xml = self.get_html(page_url,headers=self.headers)
            # print(page_html)


            #缩小搜索范围
            a_list = page_html_xml.xpath('//div[@class="list-wrap clearfix"]/a')
            # print(len(div))

            #循环获取每一个a标签中的数据
            for a in a_list:

                #获取标题
                title = a.xpath('.//div[2]/h2/span/text()')[0] if a.xpath('.//div[2]/h2/span/text()') else ''
                # print(title)

                #获取图片
                pic = a.xpath('.//div[1]/img/@data-original')[0].strip('@base@tag=imgScale&w=428&h=275&q=88')+'g' if a.xpath('.//div[1]/img/@data-original') else ''
                #拼接完整url
                pic = 'htt' + pic
                # print(pic)

                #获取首付信息
                down_payment = a.xpath('.//div[2]/div/p/em/text()')[0] if a.xpath('.//div[2]/div/p/em/text()') else ''
                # print(down_payment)

                #获取月供信息
                monthly_payment = a.xpath('.//div[2]/div/p[2]/text()')[0].strip('月供').strip('元') if a.xpath('.//div[2]/div/p[2]/text()') else  ''
                # print(monthly_payment)

                #获取详情页url
                detail_url = a.xpath('./@href')[0] if a.xpath('./@href') else ''
                # print(detail_url)

                #获取详情页页面
                detail_html,detail_html_xml = self.get_html(detail_url,headers=self.headers)
                # print(detail_html)

                #获取变速箱信息
                gearbox = detail_html_xml.xpath('//ul[@class="config-detail"]/li[4]/p[2]/text()')[0] if detail_html_xml.xpath('//ul[@class="config-detail"]/li[4]/p[2]/text()') else ''
                # print(gearbox)

                #获取长宽高信息
                lwh = detail_html_xml.xpath('//ul[@class="config-detail"]/li[5]/p[2]/text()')[0] if detail_html_xml.xpath('//ul[@class="config-detail"]/li[5]/p[2]/text()') else ''
                # print(lwh)

                #将所有信息组织放入字典中
                car_dict = {
                    'title':title,
                    'pic':pic,
                    'down_payment':down_payment,
                    'monthly_payment':monthly_payment,
                    'detail_url':detail_url,
                    'gearbox':gearbox,
                    'lwh':lwh
                }
                # print(car_dict)
                self.insert_into(car_dict)
                # break
            # break

    def insert_into(self,car_dict):

        title = car_dict['title']
        pic = car_dict['pic']
        down_payment = car_dict['down_payment']
        monthly_payment = car_dict['monthly_payment']
        detail_url = car_dict['detail_url']
        gearbox = car_dict['gearbox']
        lwh = car_dict['lwh']
        sql = '''
        insert into maodou(title,pic,down_payment,monthly_payment,detail_url,gearbox,lwh) 
        VALUES ("{}","{}","{}","{}","{}","{}","{}")'''.format(title,pic,down_payment,monthly_payment,detail_url,gearbox,lwh)

        try:
            self.cur.execute(sql)
            self.conn.commit()
            print(self.count,sql)
            self.count += 1
        except Exception as e:
            print(e)
            self.conn.rollback()





if __name__ == '__main__':
    maodou = MaoDou()
    maodou()

