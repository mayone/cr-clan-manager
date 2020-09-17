# -*- coding: utf-8 -*-

import requests

class API():
    def __init__(self):
        headers = {
            "Accept": "application/json",
        }
        self.__base_url = ""
        self.__jwt = None
        self.__session = requests.session()
        self.__session.headers.update(headers)

    def set_url(self, url):
        self.__base_url = url

    def set_jwt(self, jwt):
        self.__jwt = jwt
        headers = {
            "Authorization": f"Bearer {self.__jwt}"
        }
        self.__session.headers.update(headers)

    def GET(self, query):
        session = self.__session
        req = self.__base_url + query

        try:
            resp = session.get(req)
        except Exception as e:
            print("API request error", e)
            raise

        status = resp.status_code
        payload = resp.json()

        if not resp.ok:
            raise Exception(status, payload)

        return payload