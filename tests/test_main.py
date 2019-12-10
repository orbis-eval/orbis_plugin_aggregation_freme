# -*- coding: utf-8 -*-

from orbis_plugin_aggregation_freme.main import Main
from orbis_eval.core.rucksack import Rucksack

import requests_mock
import unittest
import json

class TestMain(unittest.TestCase):

    def setUp(self):
        self.config = {
            "aggregation": {
                "service": {
                    "language": "de",
                    "location": "web"
                },
                "input": {
                    "data_set": {
                        "name": "rss1"
                    }
                }
            },
            "file_name": "rss1_freme_web.yaml"
        }
        self.rucksack = Rucksack(self.config)
        self.main = Main(rucksack=self.rucksack)

    def test_get_lang_from_config(self):
        self.assertEqual(self.main.get_lang_from_config(), "de")

    def test_get_service_url(self):	
        expectedURL = "https://api.freme-project.eu/current/e-entity/freme-ner/documents?language=de&dataset=dbpedia&mode=all"
        self.assertEqual(self.main.get_service_url(), expectedURL)

    def test_get_type_place(self):
        item = {
            "taClassRef": "http://nerd.eurecom.fr/ontology#Location"
        }
        item = self.main.get_type(item)
        self.assertEqual(item["entity_type"], 'Place')

    def test_get_type_organization(self):
        item = {
            "taClassRef": "http://nerd.eurecom.fr/ontology#Organization"
        }
        item = self.main.get_type(item)
        self.assertEqual(item["entity_type"], 'Organization')

    def test_get_type_person(self):
        item = {
            "taClassRef": "http://nerd.eurecom.fr/ontology#Person"
        }
        item = self.main.get_type(item)
        self.assertEqual(item["entity_type"], 'Person')           

    def test_get_type_none(self):
        item = {
            "taClassRef": "http://fhgr.ch/ontology#Dude"
        }
        item = self.main.get_type(item)
        self.assertEqual(item["entity_type"], 'Notype')   

    def test_map_item_none(self):
        item = {}
        item = self.main.map_item(item)
        self.assertEqual(item, None)

    def test_map_item(self):
        item = {
            "taIdentRef": "http://dbpedia.org/resource/American_Civil_Liberties_Union",
            "nif:anchorOf": "ACLU",
            "beginIndex": 4,
            "endIndex": 22,
            "taClassRef": "http://nerd.eurecom.fr/ontology#Organization",


        }
        item = self.main.map_item(item)
        self.assertEqual(item["key"], "http://dbpedia.org/resource/American_Civil_Liberties_Union")
        self.assertEqual(item["surfaceForm"], "ACLU")
        self.assertEqual(item["document_start"], 4)
        self.assertEqual(item["document_end"], 22)

    def test_map_entities_none(self):
        item = self.main.map_entities(None, None)
        self.assertEqual(item, None)

    @requests_mock.Mocker()
    def test_query(self, requests_mock):
        item = {
            "corpus": "The U.S. Patent Office allows genes to be patented as soon as someone isolates the DNA by removing it from the cell , says ACLU attorney Sandra Park."
        }
        with open('tests/test_query_response.json') as json_file:
            data = json.load(json_file)
        
        requests_mock.post(self.main.get_service_url(), json=data, status_code=200)
        response = self.main.query(item)
        self.assertEqual(response, data)

if __name__ == '__main__':
    unittest.main()