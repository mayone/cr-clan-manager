from __future__ import annotations

from typing import Any

import requests

from exceptions import APIError

REQUEST_TIMEOUT = 30


class API:
    def __init__(self) -> None:
        headers = {"Accept": "application/json"}
        self.__base_url: str = ""
        self.__jwt: str | None = None
        self.__session = requests.session()
        self.__session.headers.update(headers)

    def set_url(self, url: str) -> None:
        self.__base_url = url

    def set_jwt(self, jwt: str) -> None:
        self.__jwt = jwt
        headers = {"Authorization": f"Bearer {self.__jwt}"}
        self.__session.headers.update(headers)

    def get_external_ip(self) -> str:
        req = "https://ipecho.net/plain"
        resp = requests.get(req, timeout=REQUEST_TIMEOUT)
        return resp.text

    @staticmethod
    def _parse_response(resp: requests.Response) -> dict[str, Any]:
        status = resp.status_code
        try:
            payload = resp.json()
        except ValueError as err:
            raise APIError(status, resp) from err

        if not resp.ok:
            raise APIError(status, payload)

        return payload

    def GET(self, query: str) -> dict[str, Any]:
        resp = self.__session.get(self.__base_url + query, timeout=REQUEST_TIMEOUT)
        return self._parse_response(resp)

    def POST(self, query: str, data: str | dict | None = None) -> dict[str, Any]:
        req = self.__base_url + query

        if isinstance(data, dict):
            resp = self.__session.post(req, json=data, timeout=REQUEST_TIMEOUT)
        else:
            resp = self.__session.post(
                req,
                data=data,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )

        return self._parse_response(resp)
