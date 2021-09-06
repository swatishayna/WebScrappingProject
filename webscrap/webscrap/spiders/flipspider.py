import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import WebscrapItem

class ReviewspiderSpider(scrapy.Spider):
    name = 'reviewspider'
    page_number = 2
    count = 1
    #expected_pagereview = int()
    allowed_domains = ["flipkart.com"]
    #start_urls = ["https://www.flipkart.com/apple-iphone-12-blue-128-gb/p/itm02853ae92e90a?pid=MOBFWBYZKPTZF9VG&lid=LSTMOBFWBYZKPTZF9VG6GMIFT&marketplace=FLIPKART&q=iphone11&store=tyy%2F4io&srno=s_1_1&otracker=search&otracker1=search&fm=SEARCH&iid=32493508-8e3d-4f96-b5bd-91fd5f4f5cf5.MOBFWBYZKPTZF9VG.SEARCH&ppt=hp&ppn=homepage&ssid=kjwsyrriv40000001628576519570&qH=d6db477051465f9a"]
    #start_urls = ["https://www.flipkart.com/casio-g346-g-shock-ga-120-1adr-analog-digital-watch-men/p/itmf3zhfvgwvvghc?pid=WATDHTKUW5NF8BGA&lid=LSTWATDHTKUW5NF8BGA6Y1T97&marketplace=FLIPKART&q=gshock&store=r18%2Ff13&srno=s_1_1&otracker=search&otracker1=search&fm=SEARCH&iid=e4cc06e4-b8f9-470a-b0cc-16022a656ac8.WATDHTKUW5NF8BGA.SEARCH&ppt=sp&ppn=sp&ssid=ui72jt53uo0000001628595708103&qH=4b68b5e43ce3f967"]

    myBaseUrl = ''
    start_urls = []

    def __init__(self, category='' ,expected_pageno=None,**kwargs):  # The category variable will have the input URL.
        self.myBaseUrl = category
        self.start_urls.append(self.myBaseUrl)
        self.expected_pagereview = expected_pageno

        super().__init__(**kwargs)

    custom_settings = {'FEED_URI': 'webscrap//reviews.csv','CLOSESPIDER_TIMEOUT': 15}


    def parse(self, response):
        all_reviewslink = response.xpath("//div[@class = '_1AtVbE col-12-12']//a/@href").extract()
        for link in all_reviewslink:
            if str(link).endswith("FLIPKART"):
                self.url = link
                yield response.follow("https://www.flipkart.com"+link, callback= self.parse_reviewpage)

    def parse_reviewpage(self,response):
        items = WebscrapItem()

        bigboxes = response.xpath("//div[@class = '_1AtVbE col-12-12']")
        def check_length(coloumn):

            length = len(coloumn)
            if length < 10:
                return [coloumn.append("") for i in range(10-length)]

        try:
            custnames = bigboxes.xpath("//div[@class = 'row _3n8db9']//p[1]/text()").extract()
        except:
            pass
        finally:
            check_length(custnames)
        try:
            headings = bigboxes.xpath("//p[@class='_2-N8zT']/text()").extract()
        except:
            pass
        finally:
            check_length(headings)
        try:
            areas = bigboxes.xpath("//div[@class= '_1AtVbE col-12-12']//p[@class='_2mcZGG']//span[2]/text()").extract()
        except:
            pass
        finally:
            check_length(areas)
        try:
            ratings = bigboxes.css("._1BLPMq::text").extract()
        except:
            pass
        finally:
            check_length(ratings)
        try:
            dates =  bigboxes.xpath("//div[@class = 'row _3n8db9']//p[@class = '_2sc7ZR']/text()").extract()
        except:
            pass
        finally:
            check_length(dates)
        try:
            custtypes = bigboxes.xpath("//div[@class= '_1AtVbE col-12-12']//p[@class='_2mcZGG']//span[1]/text()").extract()
        except:
            pass
        finally:
            check_length(custtypes)






        for(custnames,ratings,headings,dates,areas,custtypes) in zip(custnames,ratings,headings,dates,areas,custtypes):
            items['count'] = self.count
            items["custnames"]= custnames
            items["ratings"] = ratings
            items["headings"] = headings
            items["dates"] = dates
            items["areas"] = areas
            items["custtypes"] = custtypes
            self.count = self.count + 1

            yield items

        next_page = "https://www.flipkart.com" + self.url + "&page=" + str(self.page_number)

        if self.page_number <= self.expected_pagereview:
            self.page_number = self.page_number + 1
            print(self.page_number)
            yield response.follow(next_page, callback=self.parse_reviewpage)

