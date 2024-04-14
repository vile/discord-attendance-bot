import shelve

from discord import Member

import cogs.utils.constants as constants


def get_instructors() -> list[int]:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        return handle["instructors"] if "instructors" in handle else []


def add_instructor(user_id: Member.id) -> bool:
    if user_id in get_instructors():
        return False

    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.append(user_id)
        handle["instructors"] = temp_instructors

    return user_id in get_instructors()


def remove_instructor(user_id: Member.id) -> bool:
    if user_id not in get_instructors():
        return False

    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.remove(user_id)
        handle["instructors"] = temp_instructors

    return user_id not in get_instructors()


def take_member_snapshot(member_ids: list[int]) -> None:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        temp_snapshots: list[dict] = handle["snapshots"]
        snapshot: list[int] = member_ids
        temp_snapshots.append(snapshot)
        handle["snapshots"] = temp_snapshots


def get_snapshots() -> list[int]:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        snapshots: list[int] = handle["snapshots"]

    return snapshots or []


def clear_snapshots() -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["snapshots"] = []

    return get_snapshots() == []


def get_attendance_rate() -> float:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        attendance_rate: float = handle["minimum_attendance_rate"]

    return attendance_rate


def set_attendace_rate(rate: float) -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["minimum_attendance_rate"] = rate

    return rate == get_attendance_rate()


def get_snapshot_interval() -> int:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        snapshot_interval: int = handle["snapshot_interval"]

    return snapshot_interval


def set_snapshot_interval(interval: int) -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["snapshot_interval"] = interval

    return interval == get_snapshot_interval()


def get_auto_clear_on_new_session() -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        auto_clear: bool = handle["auto_clear_snapshots_on_new_session"]

    return auto_clear


def set_auto_clear_on_new_session(should_clear: bool) -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["auto_clear_snapshots_on_new_session"] = should_clear

    return should_clear == get_auto_clear_on_new_session()


def get_auto_clear_after_attendance_report() -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        auto_clear: bool = handle["auto_clear_snapshots_after_attendance_report"]

    return auto_clear


def set_auto_clear_after_attendance_report(should_clear: bool) -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["auto_clear_snapshots_after_attendance_report"] = should_clear

    return should_clear == get_auto_clear_after_attendance_report()


def get_important_attendance_responses_are_ephemeral() -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        responses_are_ephemeral: bool = handle[
            "important_attendance_responses_are_ephemeral"
        ]

    return responses_are_ephemeral


def set_important_attendance_responses_are_ephemeral(are_ephemeral: bool) -> bool:
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        handle["important_attendance_responses_are_ephemeral"] = are_ephemeral

    return are_ephemeral == get_important_attendance_responses_are_ephemeral()
