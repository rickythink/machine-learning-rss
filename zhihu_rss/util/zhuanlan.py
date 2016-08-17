# -*- coding:utf-8 -*-

from urllib import quote
import datetime
import json
import re
import itertools
import PyRSS2Gen

re_br_to_remove = re.compile(r'(?:<br>)+')
re_img = re.compile(r'<img src="([^h])')
re_zhihu_img = re.compile(r'(?<=<img rel="noreferrer" src=")https://\w+\.zhimg\.com/[^"]+(?=")')
picN = iter(itertools.cycle('1234'))

def proxify_url_cf(match):
	url = match.group()
	return 'https://images.weserv.nl/?url=ssl:' + url[8:]

def proxify_url_google(match):
	url = match.group()
	return 'https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?url=' + quote(url) + '&container=focus'

PIC_PROXIES = {
	'google': proxify_url_google,
	'cf': proxify_url_cf,
}

def proxify_pic(html, pic):
	html = re_zhihu_img.sub(PIC_PROXIES[pic], html)
	return html

def abs_img(m):
	return '<img src="https://pic%s.zhimg.com/' % next(picN) + m.group(1)

def parse_time(t):
	t = ''.join(t.rsplit(':', 1))
	t = t.split('+')[-2]
	return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S')

def process_content(text):
	text = re_br_to_remove.sub(r'', text)
	text = re_img.sub(abs_img, text)
	text = text.replace('<img ', '<img rel="noreferrer" ')
	text = text.replace('<code ', '<pre><code ')
	text = text.replace('</code>', '</code></pre>')
	return text

def post2rss(post, digest=False, pic=None):
	url = 'https://zhuanlan.zhihu.com%s' %  post['url']
	if digest:
		content = post['summary']
	elif post.get('titleImage'):
		content = '<p><img src="%s"></p>' % post['titleImage'] + post['content']
	else:
		content = post['content']

		content = process_content(content)
	if pic is not None:
		content = proxify_pic(content, pic)

		item = PyRSS2Gen.RSSItem(
			title = post['title'].replace('\x08', ''),
			link = url,
			description = content,
			pubDate = parse_time(post['publishedTime']),
			author = post['author']['name'],
		)
	return item

def posts2rss(name, info, posts, digest=False, pic=None):
	items = [post2rss(p, digest=digest, pic=pic) for p in posts]
	rss = PyRSS2Gen.RSS2(
		title = u'%s - 知乎专栏' % info['name'],
		link = 'https://zhuanlan.zhihu.com/%s' % name,
		lastBuildDate = datetime.datetime.now(),
		items = items,
		generator = 'Ricky',
		description = info['description'],
	)
	return rss

'''
name ==> 专栏的英文名称（链接最后面的）
info ==> 'https://zhuanlan.zhihu.com/api/columns/%s' % name 
读取到的json
posts ==> 'https://zhuanlan.zhihu.com/api/columns/%s/posts' % name
读取到的json
'''
def zhuanlan2rss(name,info,posts):
	posts = json.loads(posts)
	rss = posts2rss(name, info, posts, pic='cf')
	rss.write_xml(open("zhihu_rss/rss/%s.xml" %(name), 'w'),'utf-8')
