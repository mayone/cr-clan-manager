# -*- coding: utf-8 -*-

import json
import requests
import urllib
try:
    # python 2
    from urllib import quote_plus
except ImportError:
    # python 3
    from urllib.parse import quote_plus

from utils import singleton, datetime_wrapper, alignment
align = alignment.align

clan_tag = "#8V8CCV"


class CRAPI(metaclass=singleton.Singleton):
    def __init__(self):
        with open("crapi.json") as api_file:
            api = json.load(api_file)
        api_token = api["token"]
        headers = {
            "Accept": "application/json",
            "authorization": "Bearer" + " " + api_token
        }
        self.__base_url = "https://api.clashroyale.com/" + api["version"]
        self.__session = requests.session()
        self.__session.headers.update(headers)

    def __send_req(self, query):
        session = self.__session

        req = self.__base_url + query
        try:
            resp = session.get(req)
        except Exception as e:
            print(e)
            return None

        status_code = resp.status_code
        body = resp.json()

        if status_code == 200:
            return body
        else:
            print("Error: {0}".format(status_code))
            print("Reason: {0}".format(body["reason"]))
            print("Message: {0}".format(body["message"]))
            return None

    def get_members(self):
        """Get members of the clan.

        Returns
        -------
        members : list
        """
        query = "/clans/{0}".format(quote_plus(clan_tag)) + "/members"
        try:
            members = self.__send_req(query)["items"]
        except Exception as e:
            print("Unable to retrieve member list")
            return None

        return members

    def get_members_dic(self):
        """Get members of the clan.

        Returns
        -------
        members : dictionary
            Use tag as key, member as value.
        """
        query = "/clans/{0}".format(quote_plus(clan_tag)) + "/members"
        try:
            members = self.__send_req(query)["items"]
        except Exception as e:
            print("Unable to retrieve member list")
            return None
        hash_members = {}

        for member in members:
            query = "/players/{0}".format(quote_plus(member["tag"]))
            player = self.__send_req(query)
            # Add field "bestTrophies" to each member
            member["bestTrophies"] = player["bestTrophies"]
            hash_members[member["tag"]] = member

        return hash_members

    def show_members(self):
        try:
            members = self.get_members()
        except Exception as e:
            print("No member to display")
            return

        now = datetime_wrapper.get_utcnow()

        print("部落成員，共 {0} 名".format(len(members)))
        print("{0}{1}{2}{3}{4}".format(
            align("排名", length=6),
            align("名字", length=32),
            align("職位", length=6),
            align("獎盃", length=6),
            align("上線", length=6, dir="r")))
        print("=" * 56)
        num_leader = num_coleader = num_elder = 0
        for member in members:
            tag = member["tag"]
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
            except Exception as e:
                last_seen = ""

            clan_rank = str(member["clanRank"])
            trophies = str(member["trophies"])

            print("{0}{1}{2}{3}{4}".format(
                align(clan_rank, length=6),
                align(name, length=32),
                align(role, length=6),
                align(trophies, length=6),
                align(last_seen, length=6, dir="r")))
        print("首領:{0} 位".format(align(str(num_leader), length=6, dir="r")))
        print("副首:{0} 位".format(align(str(num_coleader), length=6, dir="r")))
        print("長老:{0} 位".format(align(str(num_elder), length=6, dir="r")))

    def show_race(self):
        """Show current river race of the clan.

        Returns
        -------
        warlog : list
            Order: later to former.
        """
        query = "/clans/{0}".format(quote_plus(clan_tag)) + "/currentriverrace"
        race = self.__send_req(query)

        if not race:
            print("沒有正在進行的部落戰")
            return

        section_idx = race['sectionIndex']

        clans = race['clans']
        # Show other clans
        print("河流競賽 Week "+ str(section_idx))
        print("{0}{1}{2}{3}".format(
            align("部落 (獎盃)", length=24),
            align("名譽值", length=8, dir="r"),
            align("維修值", length=8, dir="r"),
            align("完成時間", length=12, dir="r")))
        print("=" * 56)
        for clan in clans:
            if clan['tag'] == clan_tag:
                # Skip our clan
                continue
            name = clan['name']
            score = str(clan['clanScore'])
            fame = str(clan['fame'])
            repair = str(clan['repairPoints'])
            try:
                finish_time = datetime_wrapper.get_date_str(
                    datetime_wrapper.utc_to_local(
                        datetime_wrapper.datetime_from_str(clan['finishTime'])))
            except Exception as e:
                finish_time = "未完成"
            print("{0}{1}{2}{3}".format(
                align("{0} ({1})".format(name,score), length=24),
                align(fame, length=8, dir="r"),
                align(repair, length=8, dir="r"),
                align(finish_time, length=12, dir="r")))

        clan = race['clan']
        # Show our clan
        # print(clan)
        name = clan['name']
        score = str(clan['clanScore'])
        fame = str(clan['fame'])
        repair = str(clan['repairPoints'])
        print("{0}{1}{2}{3}".format(
            align("{0} ({1})".format(name,score), length=24),
            align(fame, length=8, dir="r"),
            align(repair, length=8, dir="r"),
            align(finish_time, length=12, dir="r")))
        # TODO: Show contribution of members

    def get_racelog(self, limit=0):
        """Get racelog of the clan.

        Returns
        -------
        racelog : list
            Order: later to former.
        """
        query = "/clans/{0}".format(quote_plus(clan_tag)) + "/riverracelog" + \
            ("?limit={0}".format(limit) if limit > 0 else "")

        racelog = None
        try:
            racelog = self.__send_req(query)["items"]
        except Exception as e:
            print("Error: Unable to retrieve racelog")

        return racelog
    
    def show_racelog(self, limit=0):
        racelog = self.get_racelog(limit)
        if not racelog or len(racelog) == 0:
            print("沒有河流競賽紀錄")
            return
        early_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(racelog[len(racelog)-1]["createdDate"])))
        late_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(racelog[0]["createdDate"])))

        print("河流競賽紀錄 {0} ~ {1}，共 {2} 筆".format(
            early_date_str,
            late_date_str,
            len(racelog)))
        print("=" * 56)
        for race in reversed(racelog):
            season_id = race["seasonId"]
            created_date_str = datetime_wrapper.get_date_str(
                datetime_wrapper.utc_to_local(
                    datetime_wrapper.datetime_from_str(race["createdDate"])))
            standings = race["standings"]
            for standing in standings:
                clan = standing["clan"]
                if clan["tag"] == clan_tag:
                    rank = standing["rank"]
                    trophy_change = standing["trophyChange"]
                    fame = clan["fame"]
                    repair = clan["repairPoints"]
                    try:
                        finished_date_str = datetime_wrapper.get_date_str(
                            datetime_wrapper.utc_to_local(
                                datetime_wrapper.datetime_from_str(clan["finishTime"])))
                    except Exception as e:
                        finished_date_str = "未完成"
                    participants = clan["participants"]

            print("河流競賽 {0}".format(season_id))
            print("完成日期： {0}".format(finished_date_str))
            print("結束日期： {0}".format(created_date_str))
            print("名次： {0}".format(rank))
            print("獎盃： {0}".format(trophy_change))
            print("名譽(維修)： {0}({1})".format(fame, repair))
            print("參加人數： {0}".format(len(participants)))
            print("名單 (名譽/維修)：", end="")
            i = 0
            num_columns = 2
            for p in participants:
                p_name = p["name"]
                p_fame = str(p["fame"])
                p_repair = str(p["repairPoints"])
                if i % num_columns == 0:
                    print("\n  ", end="")
                print("{0} {1}  ".format(
                    align(p_name, length=20),
                    align("("+p_fame+" / "+p_repair+")", length=16, dir="r")), end="")
                i += 1
            print("")
            print("=" * 56)

    def get_warlog(self, limit=0):
        """Get warlog of the clan.

        Returns
        -------
        warlog : list
            Order: later to former.
        """
        query = "/clans/{0}".format(quote_plus(clan_tag)) + "/warlog" + \
            ("?limit={0}".format(limit) if limit > 0 else "")

        warlog = None
        try:
            warlog = self.__send_req(query)["items"]
        except Exception as e:
            print("Error: Unable to retrieve warlog")

        return warlog

    def show_warlog(self, limit=0):
        warlog = self.get_warlog(limit)
        if not warlog or len(warlog) == 0:
            print("沒有部落戰紀錄")
            return
        early_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(warlog[len(warlog)-1]["createdDate"])))
        late_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(warlog[0]["createdDate"])))

        print("部落戰紀錄 {0} ~ {1}，共 {2} 筆".format(
            early_date_str,
            late_date_str,
            len(warlog)))
        print("=" * 56)
        for war in reversed(warlog):
            date_str = datetime_wrapper.get_date_str(
                datetime_wrapper.utc_to_local(
                    datetime_wrapper.datetime_from_str(war["createdDate"])))
            participants = war["participants"]
            standings = war["standings"]
            for standing in standings:
                if standing["clan"]["tag"] == clan_tag:
                    trophy_change = standing["trophyChange"]
            print("部落戰 {0}".format(date_str))
            print("獎盃： {0}".format(trophy_change))
            print("參加人數： {0}".format(len(participants)))
            print("名單：", end="")
            i = 0
            num_columns = 3
            for p in participants:
                if i % num_columns == 0:
                    print("\n\t", end="")
                print("{0}".format(align(p["name"], length=20)), end="")
                i += 1
            print("")
            print("=" * 56)
