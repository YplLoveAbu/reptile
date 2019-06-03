

import re,requests,json
from lxml import etree
import pymysql

class MySql():

    def __init__(self):
        self.count = 1
        self.conn_mysql()

    def conn_mysql(self):
        #创建数据库连接对象
        self.conn = pymysql.connect(host='127.0.0.1',user='root',password='12345',charset='utf8',database='youxin')
        #创建操作数据库对象
        self.cur = self.conn.cursor()




class YouXin(MySql):

    # def __init__(self):
    #     self.spider_name = '优信二手车'
    #     self.count = 1

    def __call__(self, *args, **kwargs):
        base_url = 'https://www.xin.com/beijing/?'
        self.headers = {
        # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        # "Accept-Encoding":"gzip, deflate, br",
        # "Accept-Language":"zh-CN,zh;q=0.9",
        # "Cache-Control":"max-age=0",
        # "Connection":"keep-alive",
        # "Cookie":"RELEASE_KEY=; acw_tc=77bcd71f15592650272931081edadcbce442d724c1af8441471d116e8d; XIN_anti_uid=93CC65C6-8A5F-470D-DDB3-AD040DC4AED4; uid=rBQKDVzwfwO1RELMdracAg==; Hm_lvt_ae57612a280420ca44598b857c8a9712=1559265043; XIN_UID_CK=bc5c0fcd-1bef-8cd5-9016-9874ed22a5ce; SEO_KEY=优信; SEO_REF=https://www.xin.com/beijing/?; session_xin=pacp08mtjjqicoc565f9ui6koo5kjcmf; Hm_lpvt_ae57612a280420ca44598b857c8a9712=1559268745; SERVERID=2b9b3eff6cd4c8e6aeab0731ad09b7de|1559268730|1559265027; XIN_LOCATION_CITY=%7B%22cityid%22%3A%22201%22%2C%22areaid%22%3A%221%22%2C%22big_areaid%22%3A%222%22%2C%22provinceid%22%3A%222%22%2C%22cityname%22%3A%22%5Cu5317%5Cu4eac%22%2C%22ename%22%3A%22beijing%22%2C%22shortname%22%3A%22BJ%22%2C%22service%22%3A%221%22%2C%22near%22%3A%22910%2C2501%2C906%2C1701%2C901%2C2601%2C1001%22%2C%22tianrun_code%22%3A%22010%22%2C%22zhigou%22%3A%221%22%2C%22is_visit%22%3A%221%22%2C%22longitude%22%3A%22116.4075260%22%2C%22latitude%22%3A%2239.9040300%22%2C%22city_rank%22%3A%221%22%2C%22city_group%22%3A%222%22%2C%22is_gold_partner%22%3A%22-1%22%2C%22direct_rent_support%22%3A%221%22%2C%22salvaged_support%22%3A%221%22%2C%22isshow_c%22%3A%221%22%2C%22is_lease_back%22%3A%221%22%2C%22mortgage_service_fee%22%3A%2260000%22%2C%22is_small_pub_house%22%3A%221%22%2C%22is_wz_mortgage%22%3A%221%22%2C%22is_purchase_direct%22%3A%221%22%2C%22is_purchase_origin%22%3A%221%22%2C%22is_ms_ex%22%3A%220%22%2C%22is_ms_trans%22%3A%220%22%2C%22updatetime%22%3A%222019-05-27+14%3A08%3A59%22%7D",
        # "Host":"www.xin.com",
        # "If-Modified-Since":"Fri, 31 May 2019 01:42:21 GMT",
        # "If-None-Match":"W/d3635680eadb30e2b6f64ec809eb6decb5ea8c14935b94e1f87476947c484548",
        # "Referer":"https://www.xin.com/changsha/",
        # "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
        }
        html,html_xml = self.get_html(base_url,self.headers)
        #获取城市列表
        self.city_constitute_list = self.get_city_list()#含有城市及对应的url

        #获取品牌列表
        brand_total_list = self.get_brand_list()

        #获取每个城市各个品牌列表页面
        #拼接每个城市各个品牌列表页面url
        for city in self.city_constitute_list:
            city_url = city[1]
            # print(city_url)
            for brand_tuple in brand_total_list:
                brand_city_url = city_url + brand_tuple[1]+ '/'
                # print(brand_city_url)
                #获取车系
                car_series_list = self.get_car_series(brand_city_url,city[0],brand_tuple[0])#含有汽车车系和对应url
                # break
            # break



    def get_html(self,url,headers):
        html = requests.get(url,headers=self.headers).text
        html_xml = etree.HTML(html)
        # print(html)
        return html,html_xml

    #获取所有城市名和对应url列表
    def get_city_list(self):
        base_url = 'https://www.xin.com/apis/Ajax_common/get_home_city/'
        city_html,city_html_xml = self.get_html(base_url,self.headers)
        # print(city_html)

        #将城市接口页面获取的字典转换为json格式
        city_json = json.loads(city_html)
        # print(city_json)

        #获取全部城市cityid
        cityid_list = city_json.get('data').get('city_all').keys()
        # print(cityid_list)
        # print(len(cityid_list))#286

        #由cityid循环获取每个城市cityname,ename(ename用于拼接城市url)
        self.city_constitute_list = []
        for cityid in cityid_list:
            cityname = city_json.get('data').get('city_all').get(cityid).get('cityname')
            # print(cityname)
            ename = city_json.get('data').get('city_all').get(cityid).get('ename')
            # print(ename)

            #拼接每个城市优信二手车完整url
            city_url = 'https://www.xin.com/' +ename + '/'
            # print(city_url)

            #组合城市名字和url
            city_constitute =(cityname ,city_url)
            self.city_constitute_list.append(city_constitute)
        # print(self.city_constitute_list)
        # print(len(self.city_constitute_list))
        return self.city_constitute_list

    #获取所有品牌名称及拼音（#用来拼接品牌url）
    def get_brand_list(self):
        #汽车品牌接口地址#https://www.xin.com/apis/Ajax_home/get_home_brand/
        base_url = 'https://www.xin.com/apis/Ajax_home/get_home_brand/'
        html,html_xml = self.get_html(base_url,self.headers)
        json_html = json.loads(html)
        # print(json_html)

        #获取所有汽车品牌
        #获取所有品牌首字母
        brand_alpha_list1 = json_html.get('data')[0].keys()
        brand_alpha_list2 = json_html.get('data')[1].keys()
        brand_alpha_list3 = json_html.get('data')[2].keys()
        # print(type(brand_alpha_list1))#<class 'dict_keys'>
        # print(brand_alpha_list1)#dict_keys(['G', 'F', 'A', 'C', 'H', 'B', 'D'])
        #循环取出所有品牌，和品牌拼音（#用来拼接品牌url）放入一个列表中
        brand_total_list = []
        for index in range(3):
            for alpha in json_html.get('data')[index].keys():
                #通过品牌首字母获取所有品牌品牌名，及拼音
                brandname_list = json_html.get('data')[index].get(alpha)
                for brandname_index in brandname_list:
                    brandname = brandname_index.get('brandname')
                    # print(brandname)
                    brandspell = brandname_index.get('pinyin')
                    brand_tuple = (brandname,brandspell)
                    brand_total_list.append(brand_tuple)
        # print(brand_total_list)
        # print(len(brand_total_list))#242个品牌
        return brand_total_list#含有brandname及pinyin

    #获取车系及地址
    def get_car_series(self,url,cityname,brandname):
        '''
        :param url: 每个城市每个品牌列表页url
        :return:
        '''
        html,html_xml = self.get_html(url,headers=self.headers)
        # print(html)
        car_series_list = html_xml.xpath('//dl[@id="select2"]/dd[position()>1]/a/text()|//dl[@id="select2"]/dd[position()>1]/a/@href')
        # print(car_series_list)
        # print(len(car_series_list))

        #拼接完整的城市品牌车系地址
        for index in range(len(car_series_list)):
            # print(car_series)
            if 'com' in car_series_list[index]:
                # 完整的城市品牌车系地址
                car_series_list[index] = 'http:' + car_series_list[index]
                # print(car_series)
                # break
        # print(car_series_list)
        self.get_data(car_series_list,cityname,brandname)
        return car_series_list
    def get_data(self,car_series_list,cityname,brandname):
        #循环获取每一个车系汽车列表数据
        for index in range(0,len(car_series_list),2):
            page = 1
            while True:
                print('============车系{}-第{}页============'.format(car_series_list[index + 1],page))

                #拼接分页url
                page_url = car_series_list[index] + 'i{}/'.format(page)
                # print(page_url)
                html,html_xml = self.get_html(page_url,self.headers)

                # print(html)
                #缩小列表页面搜索范围
                li_list = html_xml.xpath('//div[@class="_list-con list-con clearfix ab_carlist"]/ul/li')
                # print(len(li_list))

                #循环获取每一个li标签中的信息
                for li in li_list:
                    # print(li)
                    #获取图片
                    pic = ('http:'+ li.xpath('.//div[@class="across"]/a/img/@src')[0]) if li.xpath('.//div[@class="across"]/a/img/@src') else ''
                    # print(pic)
                #
                #   #获取标题
                    title = li.xpath('.//div[@class="pad"]/h2/span/text()')[0] if li.xpath('.//div[@class="pad"]/h2/span/text()') else ''
                    # print(title)

                    #获取车辆年限
                    buy_date = li.xpath('.//div[@class="pad"]/span/text()[1]')[0].strip() if li.xpath('.//div[@class="pad"]/span/text()[1]') else ''
                    # print(buy_date)

                    #获取里程
                    mileage = li.xpath('.//div[@class="pad"]/span/text()[2]')[0].strip() if li.xpath('.//div[@class="pad"]/span/text()[2]') else ''
                    # print(mileage)

                    #库存地址
                    stock_address = li.xpath('.//div[@class="pad"]/span/span/text()')[0] if li.xpath('.//div[@class="pad"]/span/span/text()') else ''
                    # print(stock_address)

                    #车辆价格
                    price = li.xpath('.//div[@class="pad"]/p/em/text()')[0].strip().strip('万').strip().strip('\n') if li.xpath('.//div[@class="pad"]/p/em/text()') else ''
                    # print(price)

                    #详情页url
                    detail_url = ('https:' + li.xpath('.//div[@class="across"]/a/@href')[0]) if li.xpath('.//div[@class="across"]/a/@href') else ''
                    # print(detail_url)

                    #获取详情页
                    detail_html,detail_html_xml = self.get_html(detail_url,self.headers)
                    # print(detail_html)

                    #获取变速箱
                    gearbox = detail_html_xml.xpath('//div[@class="cd_m_i_pz"]/dl[3]/dd[2]/span[2]/a/text()')[0].strip() if detail_html_xml.xpath('//div[@class="cd_m_i_pz"]/dl[3]/dd[2]/span[1]') else ''
                    # print(gearbox)

                    #获取长宽高
                    leng = detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[1]/span[2]/text()')[0].strip() if detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[1]/span[2]/text()') else ''
                    weight = detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[2]/span[2]/text()')[0].strip() if detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[2]/span[2]/text()') else ''
                    height = detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[3]/span[2]/text()')[0].strip() if detail_html_xml.xpath('//div[@class="cd_m_pop_pzcs_slide"]/ul/li[3]/dl[1]/dd[3]/span[2]/text()') else ''
                    # print(leng,weight,height)
                    #将长宽高放在一起
                    lwh = [leng,weight,height]
                    #将所有数据存入字典
                    car_detail_dict = {
                        'cityname':cityname,
                        'brandname':brandname,
                        'car_series':car_series_list[index + 1],
                        'pic':pic,
                        'title':title,
                        'buy_date':buy_date,
                        'mileage':mileage,
                        'stock_address':stock_address,
                        'price':price,
                        'detail_url':detail_url,
                        'gearbox':gearbox,
                        'lwh':lwh,
                    }
                    # print(car_detail_dict)
                    self.insert_into(car_detail_dict)

                    # break

                page += 1
                if '下一页' not in html:
                    break
                # break
            # break

    def insert_into(self,data):

        cityname = data['cityname']
        brandname = data['brandname']
        car_series = data['car_series']
        pic = data['pic']
        title = data['title']
        buy_date = data['buy_date']
        mileage = data['mileage']
        stock_address = data['stock_address']
        price = data['price']
        detail_url = data['detail_url']
        gearbox = data['gearbox']
        lwh = data['lwh']
        sql = '''
        insert into youxin(cityname,brandname,car_series,pic,title,buy_date,mileage,stock_address,price,detail_url,gearbox,lwh) 
        VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")
        '''.format(cityname,brandname,car_series,pic,title,buy_date,mileage,stock_address,price,detail_url,gearbox,lwh)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            print(self.count,sql)
            self.count += 1
        except Exception as e:
            print(e)
            self.conn.rollback()

if __name__ == '__main__':
    mysql = MySql()
    youxin = YouXin()
    youxin()










