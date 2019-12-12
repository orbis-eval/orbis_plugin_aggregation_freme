# -*- coding: utf-8 -*-

import requests
import html
import urllib.parse

from orbis_eval import app
from orbis_eval.core.base import AggregationBaseClass
from orbis_plugin_aggregation_freme import types
from orbis_plugin_aggregation_dbpedia_entity_types import Main as dbpedia_entity_types

import logging
logger = logging.getLogger(__name__)


class Main(AggregationBaseClass):

    def query(self, item):
        service_url = self.get_service_url()
        data = item['corpus']
        logger.debug(f"FREME plugin query for: '{data}')")

        try:
            response = requests.post(service_url, 
                data=data, 
                headers={   'Accept': 'application/ld+json',
                            'Content-Type': 'text/plain'}).json()
        except Exception as exception:
            logger.error(f"Query failed: {exception}")
            response = None
        return response

    def map_entities(self, response, item):
        file_entities = []

        if not response:
            return None
        
        if "@graph" in response:
            for item in response["@graph"]:
                item = self.map_item(item)
                if item is not None:
                    file_entities.append(item)
        else:
            item = self.map_item(response)
            if item is not None:
                file_entities.append(item)

        return file_entities

    def map_item(self, item):
        if "taIdentRef" not in item:
            return None
        
        item["key"] = item["taIdentRef"]
        item["surfaceForm"] = item["nif:anchorOf"]
        item = self.get_type(item)
        
        item["document_start"] = int(item["beginIndex"])
        item["document_end"] = int(item["endIndex"])

        logger.debug(f"key: '{item['key']}', entity_type: '{item['entity_type']}', surfaceForm: '{item['surfaceForm']}', document_start: '{item['document_start']}', document_end: '{item['document_end']}'")
        return item

    def get_type(self, item):
        taClassRef = item["taClassRef"]         
        if taClassRef in types.nerd:
            item["entity_type"] = types.nerd[taClassRef]
        else:    
            item["entity_type"] = 'NoType'

        item["entity_type"] = dbpedia_entity_types.normalize_entity_type(item["entity_type"])            
        return item

    def get_service_url(self):
        lang = self.get_lang_from_config()
        args = {"language": lang, "dataset": "dbpedia", "mode": "all"}
        service_url = "https://api.freme-project.eu/current/e-entity/freme-ner/documents?{}".format(urllib.parse.urlencode(args))
        return service_url

    def get_lang_from_config(self):
        lang = {self.config['aggregation']['service']['language']}
        if(len(lang) < 1):
            return 'en'
        return list(lang)[0]
