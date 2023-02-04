import scrapy
from owm_scan.items import OwmScanItem
from scrapy_playwright.page import PageMethod
import re
from decouple import Config, RepositoryEnv
import psycopg2


env_config = Config(RepositoryEnv("/.env"))


class OwmCityScanSpider(scrapy.Spider):
    name = "owm-city-scan"
    allowed_domains = ["openweathermap.org"]
    # start_urls = ["http://openweathermap.org"]
    url = "https://openweathermap.org/city/{}/"

    def start_requests(self):
        connection = psycopg2.connect(
            database=env_config.get("POSTGRES_NAME"), 
            user=env_config.get("POSTGRES_USER"),
            password=env_config.get("POSTGRES_PASSWORD"), 
            host=env_config.get("HOST"), 
            port=env_config.get("PORT")
        )
        cursor = connection.cursor()
        # Get cities' id list from db
        sql = "SELECT id FROM city"
        cursor.execute(sql)
        cities_id_list = [el[0] for el in cursor.fetchall()]
        cursor.close()
        connection.close()
        # open up page for each of picked city ids
        # and wait for main ul to render via JS.
        # .icon-pressure load pretty much means that
        # all the list items we need are loaded since
        # it goes as one of the latest in ul.weather-items
        for i in cities_id_list:
            yield scrapy.Request(
                self.url.format(i), 
                meta=dict(
                    playwright = True,
                    playwright_include_page = True,
                    playwright_page_methods = [
                        PageMethod('wait_for_selector', '.icon-pressure')
                    ],
                    errback = self.err_callback,
                ),
                callback=self.parse,
                cb_kwargs=dict(current_city_id=i)
            )
        
        
    def parse(self, response, current_city_id):
        item = OwmScanItem()
        item['city_id'] = str(current_city_id)
        city_text_tokenized = response.css('.current-container h2').css("::text").extract_first().split(',')
        item['city_name'] = city_text_tokenized[0].strip()
        item['city_code'] = city_text_tokenized[1].strip()
        item['temperature'] = response.css('.current-temp span.heading').css('::text').get()[:-2]
        windspeed_content = response.css('.wind-line::text').get()
        item['windspeed'] = re.findall(r"\d+\.?\d*", windspeed_content)[0]
        # ul.weather-items contains li tags that have no class in them, but
        # we know for sure that the text content ends with 'hPa', so we loop
        # through each li tag's text contents & look for what we need.
        # The reason why we're doing this is simply because in some cases li
        # tags are reordered in ul.weather-items in weird ways sometimes.
        # For example, I encountered the first li tag to display 
        # snow precipitation level.
        p_li_text_list = response.css('ul.weather-items li').css("::text").extract()
        for elem_text in p_li_text_list:
            if elem_text is not None and elem_text.lower().strip().endswith("hpa"):
                item['pressure'] = elem_text[:-3]
                break
        yield item

    async def err_callback(self, failure):
        page = failure.request.meta['playwright_page']
        await page.close()