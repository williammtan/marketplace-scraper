# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class ScrapyfoodPipeline:
#     def process_item(self, item, spider):
#         return item

from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import re

class customImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'image_names': item["image_names"], 'image_outlets': item["image_outlets"]})
            for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        outlet = request.meta['image_outlets'] 
        outlet = re.sub(r'([^\s\w]|_)+', '', outlet)
        name = request.meta['image_names'] 
        name = re.sub(r'([^\s\w]|_)+', '', name)
        img_name = outlet + "_" + name
        return '%s.jpg.webp' % img_name
