from __future__ import annotations

import importlib.resources
import json
import os
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv, set_key

from exceptions import APIError
from utils import api, singleton

API = api.API
ENV_PATH = ".env"


def _load_api_config() -> dict[str, Any]:
    with importlib.resources.open_text("config", "crapi.json") as api_file:
        return json.load(api_file)


class CRAPI(metaclass=singleton.Singleton):
    def __init__(self) -> None:
        self._configure()

    def _configure(self) -> None:
        load_dotenv(override=True)
        api_config = _load_api_config()
        uri = api_config["api_uri"] or ""
        ver = api_config["version"] or "v1"
        jwt = os.environ.get("CRAPI_TOKEN") or ""

        self.__api = API()
        self.__api.set_url(f"{uri}/{ver}")
        self.__api.set_jwt(jwt)

        self.__clan_tag: str = os.environ.get("CR_CLAN_TAG") or ""

    def __send_req(self, query: str) -> dict[str, Any] | None:
        def send_query(retry: bool = False) -> dict[str, Any] | None:
            try:
                return self.__api.GET(query)
            except APIError as e:
                if e.status_code == 403 and not retry:
                    self.refresh_token()
                    return send_query(retry=True)

                print(f"API request ({query}) error:\n  Status: {e.status_code}\n  Response: {e}\n")
            return None

        return send_query()

    def refresh_token(self) -> None:
        api_config = _load_api_config()
        uri = api_config["dev_uri"] or ""
        email = os.environ.get("CRAPI_EMAIL")
        password = os.environ.get("CRAPI_PASSWORD")

        dev_api = API()
        dev_api.set_url(uri)

        try:
            dev_api.POST("/login", json.dumps({"email": email, "password": password}))

            date = datetime.today().strftime("%Y%m%d")
            source_ip = dev_api.get_external_ip()

            resp = dev_api.POST("/apikey/list")
            keys = resp["keys"]
            if keys and len(keys) >= 10:
                latest_key = keys[-1]
                dev_api.POST("/apikey/revoke", json.dumps({"id": latest_key["id"]}))

            resp = dev_api.POST(
                "/apikey/create",
                json.dumps(
                    {
                        "name": f"CR Manager {date}",
                        "description": "For single IP address",
                        "cidrRanges": [source_ip],
                        "scopes": None,
                    }
                ),
            )
            set_key(ENV_PATH, key_to_set="CRAPI_TOKEN", value_to_set=resp["key"]["key"])
            self._configure()

        except APIError as e:
            print(f"Refresh request error:\n  Status: {e.status_code}\n  Response: {e}\n")

    def get_clan_tag(self) -> str:
        return self.__clan_tag

    def get_members(self) -> list[dict[str, Any]] | None:
        """Get members of the clan.

        Returns
        -------
        members : list or None
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/members"
        try:
            resp = self.__send_req(query)
            members = resp["items"] if resp else None
        except (TypeError, KeyError) as e:
            print("Error: Unable to retrieve member list", e)
            return None

        return members

    def get_members_dic(self) -> dict[str, dict[str, Any]]:
        """Get members of the clan, enriched with best trophies.

        Returns
        -------
        members : dict
            Use tag as key, member as value.
        """
        members = self.get_members()
        if not members:
            return {}

        hash_members: dict[str, dict[str, Any]] = {}
        for member in members:
            tag = member["tag"]
            player = self.__send_req(f"/players/{quote_plus(tag)}")
            if player:
                member["bestTrophies"] = player["bestTrophies"]
            hash_members[tag] = member

        return hash_members

    def get_race(self) -> dict[str, Any] | None:
        """Get current river race of the clan.

        Returns
        -------
        race : dict or None
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/currentriverrace"
        return self.__send_req(query)

    def get_racelog(self, limit: int = 0) -> list[dict[str, Any]] | None:
        """Get racelog of the clan.

        Returns
        -------
        racelog : list or None
            Order: later to former.
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/riverracelog" + (
            f"?limit={limit}" if limit > 0 else ""
        )

        try:
            resp = self.__send_req(query)
            racelog = resp["items"] if resp else None
        except (TypeError, KeyError):
            print("Error: Unable to retrieve racelog")
            racelog = None

        return racelog
