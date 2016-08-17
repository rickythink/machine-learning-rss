# -*- coding:utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders import CrawlSpider, Rule
import zhihu_rss.util.zhuanlan as zrss
import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # dirty hack;  remove it later

host = 'http://www.zhihu.com'

class zhuanlan_spider(CrawlSpider):
	name = 'zhuanlan'
	allowed_domains = ['zhihu.com']

	def __init__(self, category=None):
		self.index = 0L
		self.result = list()
		txt = 'zhihu_rss/list/zhuanlan/AI/lists.txt'
		self.lists = open(txt,'r')
		for l in open(txt):
			l = self.lists.readline().strip()
			n = l.split('/')[-1]
			info_url = "https://zhuanlan.zhihu.com/api/columns/%s" %(n)
			self.result.append(info_url)
		self.max = len(self.result)
	def start_requests(self):
		info_url = self.result[self.index]
		yield Request(info_url,callback=self.parse)

	def parse(self, response):
		print 'parsing page: %s' % response.url
		name_url = response.url.split('/')[-1]
		info_txt = response.body
		infos = json.loads(info_txt)
		info = {'name':infos['name'],'description':infos['description']}
		posts_url = "https://zhuanlan.zhihu.com/api/columns/%s/posts" %(name_url)
		yield Request(posts_url,meta={'info':info},callback=self.parse_post)

	def parse_post(self, response):
		print 'parsing page: %s' % response.url
		info = response.meta['info']
		name_url = response.url.split('/')[-2]
		addr = "zhihu_rss/rss/zhuanlan/AI/%s.xml" %(name_url)
		zrss.zhuanlan2rss(name_url,info,response.body,addr)

		self.index +=1
		if self.index < self.max:
			info_url = self.result[self.index]
			yield Request(info_url,callback=self.parse)
