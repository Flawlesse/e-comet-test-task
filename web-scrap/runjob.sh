#!/bin/sh
# go to the spider directory
cd /app/owm_scan
# run the spider
$SCRAPY crawl owm-city-scan
