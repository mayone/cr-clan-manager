# -*- coding: utf-8 -*-

import os
import inspect
import json
from urllib.parse import quote_plus

from utils import singleton, api, datetime_wrapper, alignment

API = api.API
align = alignment.align

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))

clan_tag = "#8V8CCV"


class CRAPI(metaclass=singleton.Singleton):
    def __init__(self):
        with open(f"{currentdir}/../config/crapi.json") as api_file:
            api_config = json.load(api_file)
        ver = api_config['version']
        jwt = api_config['token']

        self.__api = API()
        self.__api.set_url(f"https://api.clashroyale.com/{ver}")
        self.__api.set_jwt(jwt)

    def __send_req(self, query):
        try:
            resp = self.__api.GET(query)
            return resp
        except Exception as e:
            status, payload = e.args
            print(
                "API request error:\n"
                f"  Status: {status}\n"
                f"  Reason: {payload['reason']}\n"
                f"  Message: {payload['message']}"
            )

    def get_members(self):
        """Get members of the clan.

        Returns
        -------
        members : list
        """
        query = f"/clans/{quote_plus(clan_tag)}/members"
        try:
            members = self.__send_req(query)['items']
        except Exception as e:
            print("Error: Unable to retrieve member list")
            return None

        return members

    def get_members_dic(self):
        """Get members of the clan.

        Returns
        -------
        members : dictionary
            Use tag as key, member as value.
        """
        query = f"/clans/{quote_plus(clan_tag)}/members"
        try:
            members = self.__send_req(query)['items']
        except Exception as e:
            print("Error: Unable to retrieve member list")
            return None
        hash_members = {}

        for member in members:
            tag = member['tag']
            query = f"/players/{quote_plus(tag)}"
            player = self.__send_req(query)
            # Add field "bestTrophies" to each member
            member['bestTrophies'] = player['bestTrophies']
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
            name = member['name']
            role = member['role']
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
                last_seen = member['lastSeen']
                last_seen_date = datetime_wrapper.datetime_from_str(last_seen)
                offline = now - last_seen_date
                last_seen = datetime_wrapper.get_rounded_str(offline)
            except Exception as e:
                last_seen = ""

            clan_rank = str(member['clanRank'])
            trophies = str(member['trophies'])

            print(
                f"{align(clan_rank, length=6)}"
                f"{align(name, length=32)}"
                f"{align(role, length=6)}"
                f"{align(trophies, length=6)}"
                f"{align(last_seen, length=6, dir='r')}"
            )
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
        query = f"/clans/{quote_plus(clan_tag)}/currentriverrace"
        race = self.__send_req(query)

        if not race:
            print("沒有正在進行的部落戰")
            return

        section_idx = race['sectionIndex']
        week_idx = section_idx + 1

        clans = race['clans']
        # Show other clans
        print(f"河流競賽 Week {week_idx}")
        print(
            f"{align('部落 (獎盃)', length=24)}"
            f"{align('名譽值', length=8, dir='r')}"
            f"{align('維修值', length=8, dir='r')}"
            f"{align('完成時間', length=12, dir='r')}"
        )
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
            print(
                f"{align(f'{name} ({score})', length=24)}"
                f"{align(fame, length=8, dir='r')}"
                f"{align(repair, length=8, dir='r')}"
                f"{align(finish_time, length=12, dir='r')}"
            )

        clan = race['clan']
        # Show our clan
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
        print(
            f"{align(f'{name} ({score})', length=24)}"
            f"{align(fame, length=8, dir='r')}"
            f"{align(repair, length=8, dir='r')}"
            f"{align(finish_time, length=12, dir='r')}"
        )
        print("-" * 56)
        # Show contribution of each members
        # print("名單 (名譽/維修)：")
        print("名單 (名譽/次數)：")
        participants = clan['participants']
        participants.sort(
            # key=lambda p: p['fame']+p['repairPoints'], reverse=True)
            key=lambda p: p['fame'], reverse=True)

        num_columns = 2
        for i, p in enumerate(participants):
            p_name = p['name']
            p_fame = str(p['fame'])
            # p_repair = str(p['repairPoints'])
            p_deck_used = str(p['decksUsed'])
            if i % num_columns == 0:
                print("\n  " if i > 0 else "  ", end="")
            print("{0} {1}  ".format(
                align(p_name, length=20),
                # align(f"({p_fame} / {p_repair})", length=16, dir="r")), end="")
                align(f"({p_fame} / {p_deck_used})", length=16, dir="r")), end="")
        print("")

    def get_racelog(self, limit=0):
        """Get racelog of the clan.

        Returns
        -------
        racelog : list
            Order: later to former.
        """
        query = f"/clans/{quote_plus(clan_tag)}/riverracelog" + \
            (f"?limit={limit}" if limit > 0 else "")

        racelog = None
        try:
            racelog = self.__send_req(query)['items']
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
                datetime_wrapper.datetime_from_str(racelog[len(racelog)-1]['createdDate'])))
        late_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(
                datetime_wrapper.datetime_from_str(racelog[0]['createdDate'])))

        print(f"河流競賽紀錄 {early_date_str} ~ {late_date_str}，共 {len(racelog)} 筆")
        print("=" * 56)
        for race in reversed(racelog):
            season_id = race['seasonId']
            section_idx = race['sectionIndex']
            week_idx = section_idx + 1
            created_date_str = datetime_wrapper.get_date_str(
                datetime_wrapper.utc_to_local(
                    datetime_wrapper.datetime_from_str(race['createdDate'])))
            standings = race['standings']
            finished_date_str = None
            rank = None
            trophy_change = None
            fame = None
            # repair = None
            participants = None
            for standing in standings:
                clan = standing['clan']
                if clan['tag'] == clan_tag:
                    rank = standing['rank']
                    trophy_change = standing['trophyChange']
                    fame = clan['fame']
                    # repair = clan['repairPoints']
                    try:
                        finished_date_str = datetime_wrapper.get_date_str(
                            datetime_wrapper.utc_to_local(
                                datetime_wrapper.datetime_from_str(clan['finishTime'])))
                    except Exception as e:
                        finished_date_str = "未完成"
                    participants = clan['participants']
                    participants.sort(
                        # key=lambda p: p['fame']+p['repairPoints'], reverse=True)
                        key=lambda p: p['fame'], reverse=True)
                    break

            print(
                f"河流競賽 {season_id}-{week_idx}\n"
                f"完成日期： {finished_date_str}\n"
                f"結束日期： {created_date_str}\n"
                f"名次： {rank}\n"
                f"獎盃： {trophy_change}\n"
                # f"名譽(維修)： {fame}({repair})\n"
                f"名譽： {fame}\n"
                f"參加人數： {len(participants)}\n"
                # "名單 (名譽/維修)："
                "名單 (名譽/次數)："
            )

            if not participants:
                return

            num_columns = 2
            for i, p in enumerate(participants):
                p_name = p['name']
                p_fame = str(p['fame'])
                # p_repair = str(p['repairPoints'])
                # p_boat_attacks = str(p['boatAttacks'])
                p_deck_used = str(p['decksUsed'])
                # p_deck_used_today = str(p['decksUsedToday'])
                if i % num_columns == 0:
                    print("\n  " if i > 0 else "  ", end="")
                print("{0} {1}  ".format(
                    align(p_name, length=20),
                    # align(f"({p_fame} / {p_repair})", length=16, dir="r")), end="")
                    align(f"({p_fame} / {p_deck_used})", length=16, dir="r")), end="")
            print("")
            print("=" * 56)
