from lxml import etree
import re,requests
from fake_useragent import UserAgent

class GuaZi():

    def __init__(self):
        self.spider_name = '瓜子二手车'
        self.count = 1

    def __call__(self, *args, **kwargs):
        base_url = 'https://www.guazi.com/bj'
        self.headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Cookie":"antipas=67P2283Tp067J41i4090333M; uuid=b115ede9-6bf4-4904-929d-f687c8007e05; cityDomain=bj; clueSourceCode=%2A%2300; user_city_id=12; preTime=%7B%22last%22%3A1559225364%2C%22this%22%3A1559225364%2C%22pre%22%3A1559225364%7D; ganji_uuid=8804976426474529035194; sessionid=582fb773-1376-4c22-ad21-693ae1af4343; lg=1; cainfo=%7B%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22self%22%2C%22ca_i%22%3A%22-%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_a%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22b115ede9-6bf4-4904-929d-f687c8007e05%22%2C%22sessionid%22%3A%22582fb773-1376-4c22-ad21-693ae1af4343%22%7D; close_finance_popup=2019-05-30",
        "Host":"www.guazi.com",
        "Referer":"https://www.guazi.com/bj/",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }
        html,html_xml = self.get_html(base_url,self.headers)
        # print(html)
        self.get_all_city_list(html)

    def get_all_city_list(self,html):
        #缩小查找范围
        city_search_area = re.search('<div class="city-box all-city">[\W\w]*?<!-- 城市选择 e -->',html).group()
        # print(city_search_area)
        #获取城市列表及url
        city_list = re.findall('pc_index_all_city_c" href="(.*?)" title="(.*?)二手车">',city_search_area)
        # print(city_list)
        # print(len(city_list))

        for city in city_list:
            city_url = city[0]
            #拼接完整city_url
            city_url = 'https://www.guazi.com' + city_url
            # print(city_url)

            #分析全部汽车品牌url #https://www.guazi.com/bj/buy/?fromindex=true 上海
            #获取每个城市全部汽车品牌页面
            print('==================================={}二手车======================================='.format(city[1]))
            base_url_brand = city_url+ 'buy/?fromindex=true'
            html,html_xml = self.get_html(base_url_brand,self.headers)
            # print(html)
            brand_list = html_xml.xpath('//div[@class="dd-all clearfix js-brand js-option-hid-info"]/ul/li/p/a/text()'
                                        '|//div[@class="dd-all clearfix js-brand js-option-hid-info"]/ul/li/p/a/@href')
            # print(brand_list)
            # print(len(brand_list))


            for index in range(0,len(brand_list),2):
                #拼接完整汽车品牌url
                brand_url = 'https://www.guazi.com' + brand_list[index]
                # print(brand_url)
                page = 1
                while True:
                    brand_page_url = brand_url.replace('#bread','o{}/'.format(page))
                    print('==================={}======================='.format(brand_list[index+1]))
                    html,html_xml = self.get_html(brand_page_url,self.headers)

                    #根据不同车系获取汽车列表页面
                    brand_car_html,brand_car_html_xml = self.get_html(brand_page_url,self.headers)
                    # print(brand_car_html)

                    #缩小汽车列表页面抓取范围
                    li_list = brand_car_html_xml.xpath('//ul[@class="carlist clearfix js-top"]/li')
                    # print(len(li_list))
                    if li_list:
                        for li in li_list:
                            #获取图片
                            pic = li.xpath('./a/img/@src')[0]
                            pic = pic.replace('@base@tag=imgScale&w=287&h=192&c=1&m=2&q=88','')
                            # print(pic)

                            #获取汽车title
                            title = li.xpath('./a/h2/text()')[0]
                            # print(title)

                            #获取汽车年限
                            car_year = li.xpath('./a/div/text()[1]')[0] if li.xpath('./a/div/text()[1]') else ''
                            # print(car_year)

                            #获取汽车里程
                            car_mileage = li.xpath('./a/div/text()[2]')[0] if li.xpath('./a/div/text()[2]') else ''
                            # print(car_mileage)

                            #服务类型
                            car_service = li.xpath('./a/div/text()[3]')[0].strip() if li.xpath('./a/div/text()[3]') else ''
                            # print(car_service)

                            #现价
                            cur_price = li.xpath('./a/div[2]/p/text()')[0] if li.xpath('./a/div[2]/p/text()') else ''
                            # print(cur_price)

                            #原价
                            original_price = li.xpath('./a/div[2]/em/text()')[0] if li.xpath('./a/div[2]/em/text()') else ''
                            # print(original_price)

                            #标签
                            label = li.xpath('./a/div[2]/i/text()')
                            # print(label)
                            label = '|'.join(label)

                            #获取详情页url
                            car_detail_url = li.xpath('./a[1]/@href')[0] if li.xpath('./a/@href') else ''
                            # print(car_detail)
                            #拼接完整详情页url
                            car_detail_url = 'https://www.guazi.com'+car_detail_url
                            # print(car_detail)


                            #将数据存入字典中
                            car_dict = {
                                'pic':pic,
                                'title':title,
                                'car_year':car_year,
                                'car_mileage':car_mileage,
                                'car_service':car_service,
                                'cur_price':cur_price,
                                'original_price':original_price,
                                'label':label,
                                'car_detail_url':car_detail_url
                            }
                            # print(car_dict)

                            #获取汽车详情页面
                            car_detail_html,car_detail_html_xml = self.get_car_detail(car_dict)
                            # print(car_detail_html)

                            #获取详情页变速箱
                            gearbox = car_detail_html_xml.xpath('//div[@class="detailcontent clearfix js-detailcontent active"]/table[1]/tr[6]/td[2]/text()')[0] if car_detail_html_xml.xpath('//div[@class="detailcontent clearfix js-detailcontent active"]/table[1]/tr[6]/td[1]/text()') else ''
                            # print(gearbox)

                            #获取长宽高
                            lwh = car_detail_html_xml.xpath('//div[@class="detailcontent clearfix js-detailcontent active"]/table[1]/tr[8]/td[2]/text()')[0] if car_detail_html_xml.xpath('//div[@class="detailcontent clearfix js-detailcontent active"]/table[1]/tr[8]/td[1]/text()') else ''
                            # print(lwh)

                            #车源号
                            vehicle_source_number = car_detail_html_xml.xpath('//div[@class="placeon clearfix"]/div[2]/text()[1]')[0] if car_detail_html_xml.xpath('//div[@class="placeon clearfix"]/div[2]/text()[1]') else ''
                            vehicle_source_number = vehicle_source_number.replace('车源号：','').strip()
                            # print(vehicle_source_number)

                            #将新获得的参数放入列表中
                            car_dict['gearbox'] = gearbox
                            car_dict['lwh'] = lwh
                            car_dict['vehicle_source_number'] = vehicle_source_number
                            print(self.count,car_dict)
                            self.count += 1
                            # break
                    else:
                        pass
                    page += 1
                    if '下一页' not in html:
                        # pass
                        break
                # break



    def get_car_detail(self,car_dict):
        return self.get_html(car_dict['car_detail_url'],self.headers)


    def get_html(self,url,headers):
        html = requests.get(url,headers=headers).text
        html_xml = etree.HTML(html)
        return html,html_xml













if __name__ == '__main__':
    guazi = GuaZi()
    guazi()