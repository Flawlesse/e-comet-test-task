import scrapy
from owm_scan.items import OwmScanItem
# from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod
# from scrapy_selenium import SeleniumRequest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
import re

class OwmCityScanSpider(scrapy.Spider):
    name = "owm-city-scan"
    allowed_domains = ["openweathermap.org"]
    # start_urls = ["http://openweathermap.org"]
    url = "https://openweathermap.org/city/{}/"

    def start_requests(self):
        for i in [625144, 524901, 6094817, 264371]:
            # yield SeleniumRequest(
            #     url=self.url.format(i), 
            #     callback=self.parse, 
            #     wait_time=20, 
            #     wait_until=EC.element_to_be_clickable((By.CLASS_NAME,'current-temp'))
            # )
            yield scrapy.Request(self.url.format(i), meta=dict(
                playwright = True,
                playwright_include_page = True,
                playwright_page_methods = [
                    PageMethod('wait_for_selector', '.current-temp')
                ],
                errback = self.err_callback
            ))
        
        
    def parse(self, response):
        # open_in_browser(response)
        item = OwmScanItem()
        city_text_tokenized = response.css('.current-container h2').css("::text").extract_first().split(',')
        item['city_name'] = city_text_tokenized[0].strip()
        item['city_code'] = city_text_tokenized[1].strip()
        item['temperature'] = response.css('.current-temp span.heading').css('::text').get()[:-2]
        windspeed_content = response.css('.wind-line::text').get()
        item['windspeed'] = re.findall(r"\d+\.?\d*", windspeed_content)[0]
        item['pressure'] = response.css('ul.weather-items>li:nth-child(2)::text').get()[:-3]
        yield item

    async def err_callback(self, failure):
        page = failure.request.meta['playwright_page']
        await page.close()