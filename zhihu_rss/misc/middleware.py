# -*- coding: utf-8 -*-

import random

from zhihu_rss.misc.agents import AGENTS

class CustomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent

