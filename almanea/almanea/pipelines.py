
import os
import scrapy

from urllib.parse import urlparse
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

class AlmaneaPipeline(FilesPipeline):
    
    def get_media_requests(self, item, info):
        '''Capture the download_links from the item'''
        adapter = ItemAdapter(item)
        
        for file_url in adapter['images_links']:
            yield scrapy.Request(file_url)

    # def file_path(self, request, response=None, info=None, *, item=None):
        # '''Change the file_name'''
        # will create folder named files/ inside the files_downloaded
        # return 'files/' + os.path.basename(urlparse(request.url).path)
        # return os.path.basename(urlparse(request.url).path)
    
    def item_completed(self, results, item, info):
        '''Edit the item with the downloaded files names'''
        file_paths = [x['path'] for ok, x in results if ok]
        
        # if not file_paths:
        #     raise DropItem("Item contains no files")
        
        adapter = ItemAdapter(item)
        adapter['images_names'] = '\n'.join(file_paths)
        adapter['images_links'] = '\n'.join(adapter['images_links'])

        return item