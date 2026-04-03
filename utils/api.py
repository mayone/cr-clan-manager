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

    def GET(self, query: str) -> dict[str, Any]:
        session = self.__session
        req = self.__base_url + query
        resp = session.get(req, timeout=REQUEST_TIMEOUT)

        status = resp.status_code
        try:
            payload = resp.json()
        except ValueError as err:
            raise APIError(status, resp) from err

        if not resp.ok:
            raise APIError(status, payload)

        return payload

    def POST(self, query: str, data: str | dict | None = None) -> dict[str, Any]:
        session = self.__session
        req = self.__base_url + query

        if isinstance(data, dict):
            resp = session.post(req, json=data, timeout=REQUEST_TIMEOUT)
        else:
            resp = session.post(
                req,
                data=data,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )

        status = resp.status_code
        try:
            payload = resp.json()
        except ValueError as err:
            raise APIError(status, resp) from err

        if not resp.ok:
            raise APIError(status, payload)

        return payload
