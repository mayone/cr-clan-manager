# -*- coding: utf-8 -*-

import importlib.resources
import json
import os
from datetime import datetime
from urllib.parse import quote_plus

from dotenv import load_dotenv, set_key

from utils import alignment, api, datetime_wrapper, singleton

align = alignment.align

API = api.API
ENV_PATH = ".env"


class CRAPI(metaclass=singleton.Singleton):
    def __init__(self):
        load_dotenv(override=True)
        # with open(config.CRAPI_PATH) as api_file:
        with importlib.resources.open_text("config", "crapi.json") as api_file:
            api_config = json.load(api_file)
            api_file.close()
        uri = api_config["api_uri"] or ""
        ver = api_config["version"] or "v1"
        jwt = os.environ.get("CRAPI_TOKEN") or ""

        self.__api = API()
        self.__api.set_url(f"{uri}/{ver}")
        self.__api.set_jwt(jwt)

        self.__clan_tag = os.environ.get("CR_CLAN_TAG") or ""

    def __send_req(self, query):
        def send_query(retry=False):
            try:
                resp = self.__api.GET(query)
                return resp
            except Exception as e:
                status, payload = e.args
                if status == 403 and not retry:
                    self.refresh_token()
                    self.__init__()
                    return send_query(retry=True)

                if isinstance(payload, dict):
                    print(
                        f"API request ({query}) error:\n"
                        f"  Status: {status}\n"
                        f"  Response: {payload}\n"
                    )
                else:
                    print(
                        f"API request ({query}) error:\n"
                        f"  Status: {status}\n"
                        f"  Response: {payload.text}\n"
                    )

        return send_query()

    def refresh_token(self):
        with importlib.resources.open_text("config", "crapi.json") as api_file:
            api_config = json.load(api_file)
            api_file.close()
        uri = api_config["dev_uri"] or ""
        email = os.environ.get("CRAPI_EMAIL")
        password = os.environ.get("CRAPI_PASSWORD")

        dev_api = API()
        dev_api.set_url(uri)

        try:
            resp = dev_api.POST(
                "/login", json.dumps({"email": email, "password": password})
            )

            date = datetime.today().strftime("%Y%m%d")
            source_ip = dev_api.get_external_ip()

            resp = dev_api.POST("/apikey/list")
            keys = resp["keys"]
            if keys and len(keys) >= 10:
                latest_key = keys[-1]
                resp = dev_api.POST(
                    "/apikey/revoke", json.dumps({"id": latest_key["id"]})
                )

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
            self.__init__()

        except Exception as e:
            status, payload = e.args
            if isinstance(payload, dict):
                print(
                    "Refresh request error:\n"
                    f"  Status: {status}\n"
                    f"  Response: {payload}\n"
                )
            else:
                print(
                    "Refresh request error:\n"
                    f"  Status: {status}\n"
                    f"  Response: {payload.text}\n"
                )

    def get_clan_tag(self):
        return self.__clan_tag

    def get_members(self):
        """Get members of the clan.

        Returns
        -------
        members : list
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/members"
        try:
            resp = self.__send_req(query)
            members = resp["items"] if resp else None
        except Exception as e:
            print("Error: Unable to retrieve member list", e)
            return None

        return members

    def get_members_dic(self):
        """Get members of the clan.

        Returns
        -------
        members : dictionary
            Use tag as key, member as value.
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/members"
        try:
            resp = self.__send_req(query)
            members = resp["items"] if resp else None
        except Exception:
            print("Error: Unable to retrieve member list")
            return None

        if not members:
            return {}
        hash_members = {}

        for member in members:
            tag = member["tag"]
            query = f"/players/{quote_plus(tag)}"
            player = self.__send_req(query)
            # Add field "bestTrophies" to each member
            if player:
                member["bestTrophies"] = player["bestTrophies"]
            hash_members[tag] = member

        return hash_members

    def show_members(self):
        members = self.get_members()

        if not members or len(members) == 0:
            print("沒有可顯示的成員")
            return

        now = datetime_wrapper.get_utcnow()

        print(f"部落成員，共 {len(members)} 名")
        print(
            f"{align('排名', length=6)}"
            f"{align('名字', length=32)}"
            f"{align('職位', length=6)}"
            f"{align('獎盃', length=6)}"
            f"{align('上線', length=6, dir='r')}"
        )
        print("=" * 56)
        num_leader = num_coleader = num_elder = 0
        for member in members:
            name = member["name"]
            role = member["role"]
            if role == "leader":
                role = "首領"
                num_leader += 1
            elif role == "coLeader":
                role = "副首"
                num_coleader += 1
            elif role == "elder":
                role = "長老"
                num_elder += 1
            elif role == "member":
                role = "成員"
            else:
                role = role
            try:
                last_seen = member["lastSeen"]
                last_seen_date = datetime_wrapper.datetime_from_str(last_seen)
                offline = now - last_seen_date
                last_seen = datetime_wrapper.get_rounded_str(offline)
            except Exception:
                last_seen = ""

            clan_rank = str(member["clanRank"])
            trophies = str(member["trophies"])

            print(
                f"{align(clan_rank, length=6)}"
                f"{align(name, length=32)}"
                f"{align(role, length=6)}"
                f"{align(trophies, length=6)}"
                f"{align(last_seen, length=6, dir='r')}"
            )
        print(f"首領:{align(str(num_leader), length=6, dir='r')} 位")
        print(f"副首:{align(str(num_coleader), length=6, dir='r')} 位")
        print(f"長老:{align(str(num_elder), length=6, dir='r')} 位")

    def show_race(self):
        """Show current river race of the clan.

        Returns
        -------
        warlog : list
            Order: later to former.
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/currentriverrace"
        race = self.__send_req(query)

        if not race:
            print("沒有正在進行的部落戰")
            return

        section_idx = race["sectionIndex"]
        week_idx = section_idx + 1

        clans = race["clans"]
        # Show other clans
        print(f"河流競賽 Week {week_idx}")
        print(
            f"{align('部落 (獎盃)', length=24)}"
            f"{align('名譽值', length=8, dir='r')}"
            f"{align('完成時間', length=12, dir='r')}"
        )
        print("=" * 56)
        for clan in clans:
            if clan["tag"] == self.__clan_tag:
                # Skip our clan
                continue
            name = clan["name"]
            score = str(clan["clanScore"])
            fame = str(clan["fame"])
            try:
                finish_time = datetime_wrapper.get_date_str(
                    datetime_wrapper.utc_to_local(
                        datetime_wrapper.datetime_from_str(clan["finishTime"])
                    )
                )
            except Exception:
                finish_time = "未完成"
            print(
                f"{align(f'{name} ({score})', length=24)}"
                f"{align(fame, length=8, dir='r')}"
                f"{align(finish_time, length=12, dir='r')}"
            )

        clan = race["clan"]
        # Show our clan
        name = clan["name"]
        score = str(clan["clanScore"])
        fame = str(clan["fame"])
        try:
            finish_time = datetime_wrapper.get_date_str(
                datetime_wrapper.utc_to_local(
                    datetime_wrapper.datetime_from_str(clan["finishTime"])
                )
            )
        except Exception:
            finish_time = "未完成"
        print(
            f"{align(f'{name} ({score})', length=24)}"
            f"{align(fame, length=8, dir='r')}"
            f"{align(finish_time, length=12, dir='r')}"
        )
        print("-" * 56)
        # Show contribution of each members
        print("名單 (名譽/次數)：")
        participants = clan["participants"]
        participants.sort(key=lambda p: p["fame"], reverse=True)

        num_columns = 2
        for i, p in enumerate(participants):
            p_name = p["name"]
            p_fame = str(p["fame"])
            p_deck_used = str(p["decksUsed"])
            if i % num_columns == 0:
                print("\n  " if i > 0 else "  ", end="")
            print(
                f"{align(p_name, length=20)} {align(f'({p_fame} / {p_deck_used})', length=16, dir='r')}  ",
                end="",
            )
        print("")

    def get_racelog(self, limit=0):
        """Get racelog of the clan.

        Returns
        -------
        racelog : list
            Order: later to former.
        """
        query = f"/clans/{quote_plus(self.__clan_tag)}/riverracelog" + (
            f"?limit={limit}" if limit > 0 else ""
        )

        try:
            resp = self.__send_req(query)
            racelog = resp["items"] if resp else None
        except Exception:
            print("Error: Unable to retrieve racelog")

        return racelog

    def show_racelog(self, limit=0):
        racelog = self.get_racelog(limit)

        if not racelog or len(racelog) == 0:
            print("沒有河流競賽紀錄")
            return

        early_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(
                    racelog[len(racelog) - 1]["createdDate"]
                )
            )
        )
        late_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(racelog[0]["createdDate"])
            )
        )

        print(f"河流競賽紀錄 {early_date_str} ~ {late_date_str}，共 {len(racelog)} 筆")
        print("=" * 56)
        for race in reversed(racelog):
            season_id = race["seasonId"]
            section_idx = race["sectionIndex"]
            week_idx = section_idx + 1
            created_date_str = datetime_wrapper.get_date_str(
                datetime_wrapper.utc_to_local(
                    datetime_wrapper.datetime_from_str(race["createdDate"])
                )
            )
            standings = race["standings"]
            finished_date_str = None
            rank = None
            trophy_change = None
            fame = None
            participants = None
            for standing in standings:
                clan = standing["clan"]
                if clan["tag"] == self.__clan_tag:
                    rank = standing["rank"]
                    trophy_change = standing["trophyChange"]
                    fame = clan["fame"]
                    try:
                        finished_date_str = datetime_wrapper.get_date_str(
                            datetime_wrapper.utc_to_local(
                                datetime_wrapper.datetime_from_str(clan["finishTime"])
                            )
                        )
                    except Exception:
                        finished_date_str = "未完成"
                    participants = clan["participants"]
                    participants.sort(key=lambda p: p["fame"], reverse=True)
                    break

            print(
                f"河流競賽 {season_id}-{week_idx}\n"
                f"完成日期： {finished_date_str}\n"
                f"結束日期： {created_date_str}\n"
                f"名次： {rank}\n"
                f"獎盃： {trophy_change}\n"
                f"名譽： {fame}\n"
                f"參加人數： {len(participants) if participants else 0}\n"
                "名單 (名譽/次數)："
            )

            if not participants:
                return

            num_columns = 2
            for i, p in enumerate(participants):
                p_name = p["name"]
                p_fame = str(p["fame"])
                # p_boat_attacks = str(p['boatAttacks'])
                p_deck_used = str(p["decksUsed"])
                # p_deck_used_today = str(p['decksUsedToday'])
                if i % num_columns == 0:
                    print("\n  " if i > 0 else "  ", end="")
                print(
                    f"{align(p_name, length=20)} {align(f'({p_fame} / {p_deck_used})', length=16, dir='r')}  ",
                    end="",
                )
            print("")
            print("=" * 56)
