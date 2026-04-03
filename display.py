from __future__ import annotations

from typing import Any

from constants import NAME_MAX_LENGTH, RANKING_MAX_LENGTH, ROLE_DISPLAY, ROLE_MAX_LENGTH
from utils import alignment, datetime_wrapper

align = alignment.align

DISPLAY_WIDTH = 56


def _format_finish_time(raw_time: str | None) -> str:
    try:
        return datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(datetime_wrapper.datetime_from_str(raw_time))
        )
    except (KeyError, ValueError, TypeError):
        return "未完成"


def _print_participants(participants: list[dict[str, Any]]) -> None:
    num_columns = 2
    for i, p in enumerate(participants):
        p_name = p["name"]
        p_fame = str(p["fame"])
        p_deck_used = str(p["decksUsed"])
        if i % num_columns == 0:
            print("\n  " if i > 0 else "  ", end="")
        print(
            f"{align(p_name, length=NAME_MAX_LENGTH)} "
            f"{align(f'({p_fame} / {p_deck_used})', length=16, direction='r')}  ",
            end="",
        )
    print("")


def show_members(members: list[dict[str, Any]] | None) -> None:
    if not members:
        print("沒有可顯示的成員")
        return

    now = datetime_wrapper.get_utcnow()

    print(f"部落成員，共 {len(members)} 名")
    print(
        f"{align('排名', length=RANKING_MAX_LENGTH)}"
        f"{align('名字', length=NAME_MAX_LENGTH)}"
        f"{align('職位', length=ROLE_MAX_LENGTH)}"
        f"{align('獎盃', length=6)}"
        f"{align('上線', length=6, direction='r')}"
    )
    print("=" * DISPLAY_WIDTH)
    num_leader = num_coleader = num_elder = 0
    for member in members:
        name = member["name"]
        role = member["role"]
        display_role = ROLE_DISPLAY.get(role, role)
        if role == "leader":
            num_leader += 1
        elif role == "coLeader":
            num_coleader += 1
        elif role == "elder":
            num_elder += 1

        try:
            last_seen = member["lastSeen"]
            last_seen_date = datetime_wrapper.datetime_from_str(last_seen)
            offline = now - last_seen_date
            last_seen = datetime_wrapper.get_rounded_str(offline)
        except (KeyError, ValueError, TypeError):
            last_seen = ""

        clan_rank = str(member["clanRank"])
        trophies = str(member["trophies"])

        print(
            f"{align(clan_rank, length=RANKING_MAX_LENGTH)}"
            f"{align(name, length=NAME_MAX_LENGTH)}"
            f"{align(display_role, length=ROLE_MAX_LENGTH)}"
            f"{align(trophies, length=6)}"
            f"{align(last_seen, length=6, direction='r')}"
        )
    print(f"首領:{align(str(num_leader), length=6, direction='r')} 位")
    print(f"副首:{align(str(num_coleader), length=6, direction='r')} 位")
    print(f"長老:{align(str(num_elder), length=6, direction='r')} 位")


def show_race(race: dict[str, Any] | None, clan_tag: str) -> None:
    if not race:
        print("沒有正在進行的部落戰")
        return

    section_idx = race["sectionIndex"]
    week_idx = section_idx + 1

    clans = race["clans"]
    print(f"河流競賽 Week {week_idx}")
    print(
        f"{align('部落 (獎盃)', length=24)}"
        f"{align('名譽值', length=8, direction='r')}"
        f"{align('完成時間', length=12, direction='r')}"
    )
    print("=" * DISPLAY_WIDTH)
    for clan in clans:
        if clan["tag"] == clan_tag:
            continue
        name = clan["name"]
        score = str(clan["clanScore"])
        fame = str(clan["fame"])
        finish_time = _format_finish_time(clan.get("finishTime"))
        print(
            f"{align(f'{name} ({score})', length=24)}"
            f"{align(fame, length=8, direction='r')}"
            f"{align(finish_time, length=12, direction='r')}"
        )

    clan = race["clan"]
    name = clan["name"]
    score = str(clan["clanScore"])
    fame = str(clan["fame"])
    finish_time = _format_finish_time(clan.get("finishTime"))
    print(
        f"{align(f'{name} ({score})', length=24)}"
        f"{align(fame, length=8, direction='r')}"
        f"{align(finish_time, length=12, direction='r')}"
    )
    print("-" * DISPLAY_WIDTH)
    print("名單 (名譽/次數):")
    participants = clan["participants"]
    participants.sort(key=lambda p: p["fame"], reverse=True)
    _print_participants(participants)


def show_racelog(racelog: list[dict[str, Any]] | None, clan_tag: str) -> None:
    if not racelog:
        print("沒有河流競賽紀錄")
        return

    early_date_str = datetime_wrapper.get_date_str(
        datetime_wrapper.utc_to_local(
            datetime_wrapper.datetime_from_str(racelog[-1]["createdDate"])
        )
    )
    late_date_str = datetime_wrapper.get_date_str(
        datetime_wrapper.utc_to_local(datetime_wrapper.datetime_from_str(racelog[0]["createdDate"]))
    )

    print(f"河流競賽紀錄 {early_date_str} ~ {late_date_str}，共 {len(racelog)} 筆")
    print("=" * DISPLAY_WIDTH)
    for race in reversed(racelog):
        season_id = race["seasonId"]
        section_idx = race["sectionIndex"]
        week_idx = section_idx + 1
        created_date_str = datetime_wrapper.get_date_str(
            datetime_wrapper.utc_to_local(datetime_wrapper.datetime_from_str(race["createdDate"]))
        )
        standings = race["standings"]
        finished_date_str = None
        rank = None
        trophy_change = None
        fame = None
        participants = None
        for standing in standings:
            clan = standing["clan"]
            if clan["tag"] == clan_tag:
                rank = standing["rank"]
                trophy_change = standing["trophyChange"]
                fame = clan["fame"]
                finished_date_str = _format_finish_time(clan.get("finishTime"))
                participants = clan["participants"]
                participants.sort(key=lambda p: p["fame"], reverse=True)
                break

        print(
            f"河流競賽 {season_id}-{week_idx}\n"
            f"完成日期: {finished_date_str}\n"
            f"結束日期: {created_date_str}\n"
            f"名次: {rank}\n"
            f"獎盃: {trophy_change}\n"
            f"名譽: {fame}\n"
            f"參加人數: {len(participants) if participants else 0}\n"
            "名單 (名譽/次數):"
        )

        if not participants:
            return

        _print_participants(participants)
        print("=" * DISPLAY_WIDTH)
