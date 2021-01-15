#!/usr/bin/env python
#coding=utf-8

from elasticsearch import Elasticsearch


def _put_mapping_in_es_failed_login(index, doc_type):
    mapping_body = {
        "properties": {
            "eventID": {
                "type": "keyword"
            },
            "count": {
                "type": "long"
            },
            "ipAddress": {
                "type": "keyword"
            },
            "userId": {
                "type": "keyword"
            },
            "timestamp": {
                "format": "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd||epoch_millis",
                "type": "date"
            }
        }
    }

    es.indices.put_mapping(body=mapping_body, doc_type=doc_type, index=index)


es = Elasticsearch(
            hosts="localhost:9200",
            sniff_on_start=False,
            sniff_on_connection_fail=False,
            sniffer_timeout=None,
            max_retries=3
        )

index = 'failed_login_events'

if not es.indices.exists(index=index):
    es.indices.create(index=index)
    _put_mapping_in_es_failed_login(index, index)
