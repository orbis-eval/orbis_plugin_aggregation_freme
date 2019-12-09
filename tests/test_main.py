# -*- coding: utf-8 -*-

from orbis_plugin_aggregation_freme.main import Main

def test_get_lang_from_config():	
    freme = type('', (), {})()
    freme.config = {
        "aggregation": {
            "service": {
                "language": "de"
            }
        }        
    }    
    assert Main.get_lang_from_config(freme) == "de";