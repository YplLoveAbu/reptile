
import requests,re,json,time
from lxml import etree
from selenium import webdriver
from fake_useragent import UserAgent

#先获取城区，再在城区页面获取城圈，之后从城圈获取房屋列表，
# 最后在房屋列表页面获取详情页并抓取详情页经纪人电话和房屋楼层


class LianJia():

    def __init__(self):
        self.spider_name = '链家爬虫'
        self.count = 1

    def __call__(self, *args, **kwargs):
        base_url = 'https://bj.lianjia.com/zufang/'
        html_xml,html = self.get_html(base_url)
        self.get_data(html_xml)

    #获取页面
    def get_html(self,base_url):
        headers = {
        "User-Agent":UserAgent().random
        }
        html = requests.get(base_url,headers=headers).text
        html_xml = etree.HTML(html)
        # print(html)
        return html_xml,html

    #获取页面数据
    def get_data(self,html_xml):
        #获取所有城区
        city_area_list = html_xml.xpath('//ul[@data-target="area"]/li[position()>1]/a/text()')
        # print(city_area_list)
        # print(len(city_area_list))
        #获取所有城区url
        city_url_list = html_xml.xpath('//ul[@data-target="area"]/li[position()>1]/a/@href')
        # print(city_url_list)
        # print(len(city_url_list))
        #将对应数据组织成元祖
        full_city_list = zip(city_area_list,city_url_list)
        # print(full_city_list)
        #通过城区url获取每一个城区的商圈
        for city_area in full_city_list:
            print('================================================{}城区======================================================='.format(city_area[0]))
            #拼接完整城区url
            city_area_url = 'https://bj.lianjia.com' + city_area[1]
            # print(city_area_url)
            #获取每一个城区页面
            city_area_html_xml,html = self.get_html(city_area_url)
            #获取每一个城区的全部商圈及对应url
            trade_area_list = city_area_html_xml.xpath('//div[@class="filter__wrapper w1150"]/ul[position()=4]/li[position()>1]/a/text()')
            # print(trade_area_list)
            # print(len(trade_area_list))
            trade_area_url_list = city_area_html_xml.xpath('//div[@class="filter__wrapper w1150"]/ul[position()=4]/li[position()>1]/a/@href')
            # print(trade_area_url_list)
            # print(len(trade_area_url_list))
            #将对应数据组织成元祖
            trade_area_full_list = zip(trade_area_list,trade_area_url_list)
            #获取完整的城圈url
            for index1 in range(len(trade_area_list)):
                print('============================{}商圈=================================='.format(trade_area_list[index1]))
                trade_area_full_url = 'https://bj.lianjia.com' + trade_area_url_list[index1]
                #获取每一个城圈页面
                trade_area_html_xml,html = self.get_html(trade_area_full_url)
                # print(trade_area_html_xml)
                # print(html)
                #在该城圈页面获取全部租房信息
                #获取城圈租房信息列表页最大页码
                max_page = self.get_max_page(html)
                for page in range(1,max_page+1):
                    print('=====================第{}页======================='.format(page))
                    trade_area_total_url = trade_area_full_url + 'pg{}'.format(page)
                    #翻页获取每一个城圈全部的租房详情url
                    trade_area_page_html_xml,html = self.get_html(trade_area_total_url)
                    # print(html)
                    #缩小搜索范围
                    div_list = trade_area_page_html_xml.xpath('//div[@class="content__list"]/div')
                    # print(len(div_list))
                    for div in div_list:
                        #获取每一个租房详情页url
                        house_detail_url = div.xpath('./a[@class="content__list--item--aside"]/@href')[0]
                        # print(house_detail_url)
                        house_detail_url = 'https://bj.lianjia.com' + house_detail_url
                        house_detail_html_xml,house_detail_html = self.get_html(house_detail_url)
                        # print(house_detail_html)

                        #获取楼层
                        house_floor = re.search('<li class="fl oneline">楼层：(.*?)</li>',house_detail_html).group(1) if re.search('<li class="fl oneline">楼层：(.*?)</li>',house_detail_html) else ''
                        # print(house_floor)

                        #接口分析
                        #https://bj.lianjia.com/zufang/aj/house/brokers?house_codes=BJ2231820724371193856&position=bottom&ucid=1000000020130787
                        #https://bj.lianjia.com/zufang/aj/house/brokers?house_codes=BJ2197704911918211072&position=bottom&ucid=1000000023002201
                        #多次对比分析后可知house_code为房源编号，页面可获取，position固定值，ucid页面可获取，
                        # 全部获取拼接即可获取接口url，转为json数据后可获取经纪人所有相关信息
                        #获取房源编号
                        # house_code = re.search('<i class="house_code">房源编号：(.*?)</i>',house_detail_html).group(1)
                        house_code = str(re.findall('data-houseCode="(.*?)"',house_detail_html)[0]) if re.findall('data-houseCode="(.*?)"',house_detail_html) else ''
                        # print(house_code)
                        # #获取ucid
                        ucid = re.findall('data-info="(\d+)"',house_detail_html)[0] if re.findall('data-info="(\d+)"',house_detail_html) else ''
                        #获取完整经纪人信息url
                        if ucid and house_code:
                            agent_url = 'https://bj.lianjia.com/zufang/aj/house/brokers?' + 'house_codes={}&position=bottom&'.format(house_code) + 'ucid={}'.format(ucid)
                        # print(agent_url)
                        headers = {
                        # "User-Agent":UserAgent().random
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Accept-Encoding":"gzip, deflate, br",
                        "Accept-Language":"zh-CN,zh;q=0.9",
                        "Cache-Control":"max-age=0",
                        "Connection":"keep-alive",
                        "Cookie":"lianjia_uuid=5f9b843d-26ef-47a0-a597-d8ae451c1b15; _ga=GA1.2.1569907068.1559043886; UM_distinctid=16afe41cbb1aa1-0bb9febf62222b-3e385d05-100200-16afe41cbb28db; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1559045986; _smt_uid=5ced2762.4f323520; _jzqa=1.2211279212136885000.1559045987.1559045987.1559045987.1; CNZZDATA1253477573=1571900170-1559041233-%7C1559041233; CNZZDATA1254525948=1364349946-1559044959-%7C1559044959; CNZZDATA1255633284=1160188183-1559042904-%7C1559042904; CNZZDATA1255604082=1923785869-1559043523-%7C1559043523; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216afe61db8a60d-0cd76b6d5109ce-3e385d05-1049088-16afe61db8b67b%22%2C%22%24device_id%22%3A%2216afe61db8a60d-0cd76b6d5109ce-3e385d05-1049088-16afe61db8b67b%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _qzja=1.744562445.1559045986719.1559045986719.1559045986719.1559046169250.1559046276524.0.0.0.4.1; select_nation=2; ljisid=5f9b843d-26ef-47a0-a597-d8ae451c1b15; select_city=110000; lianjia_ssid=756e5332-2176-4ff3-a399-a27cdcf94ee9",
                        "Host":"bj.lianjia.com",
                        "Upgrade-Insecure-Requests":"1",
                        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
                        }
                        if agent_url:
                            try:
                                agent_info_json = requests.get(agent_url,headers=headers).json()
                                agent_phone = agent_info_json.get('data').get(house_code).get(house_code).get('tp_number') if agent_info_json.get('data').get(house_code).get(house_code).get('tp_number') else ''
                            except:
                                agent_phone = ''
                            else:
                                agent_phone = agent_phone
                        else:
                            agent_phone = ''
                            # # 将最终结果放入字典
                        # time.sleep(0.1)
                        house_agent_dict = {
                            'house_floor': house_floor,
                            'agent_number': agent_phone
                        }
                        print(self.count, house_agent_dict)
                        self.count += 1
                        # break
                    # break
                # break
            # break

    #获取最大页码
    def get_max_page(self,html):
        max_page = re.findall('data-totalPage=(\d+)',html)[0] if re.findall('data-totalPage=(\d+)',html) else ''
        if max_page:
            max_page = max_page
        else:
            max_page = 1
        # print(max_page)
        return int(max_page)



if __name__ == '__main__':
    lianjia = LianJia()
    lianjia()