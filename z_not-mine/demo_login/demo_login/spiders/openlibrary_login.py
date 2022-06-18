# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest


class OpenlibraryLoginSpider(scrapy.Spider):
    name = 'openlibrary_login'
    allowed_domains = ['openlibrary.org']
    start_urls = ['https://openlibrary.org/account/login']

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formid='register',
            formdata={
                'username': 'meinherz75@gmail.com',
                'password': 'test123',
                'redirect': '/',
                'debug_token': '',
                'login': 'Log In'
            },
            callback=self.after_login
        )
    
    def after_login(self, response):
        print('logged in...')
