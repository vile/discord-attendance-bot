import shelve
from discord import Member


def get_instructors() -> list[int]:
    with shelve.open("database") as handle:
        return handle["instructors"] if "instructors" in handle else []


def add_instructor(user_id: Member.id) -> bool:
    if user_id in get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.append(user_id)
        handle["instructors"] = temp_instructors

    return user_id in get_instructors()


def remove_instructor(user_id: Member.id) -> bool:
    if not user_id in get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.remove(user_id)
        handle["instructors"] = temp_instructors

    return not user_id in get_instructors()


def take_member_snapshot(member_ids: list[int]) -> None:
    with shelve.open("database") as handle:
        temp_snapshots: list[dict] = handle["snapshots"]
        snapshot: list[int] = member_ids
        temp_snapshots.append(snapshot)
        handle["snapshots"] = temp_snapshots


def get_attendance_rate() -> float:
    with shelve.open("database") as handle:
        attendance_rate: float = handle["minimum_attendance_rate"]

    return attendance_rate


def set_attendace_rate(rate: float) -> bool:
    with shelve.open("database") as handle:
        handle["minimum_attendance_rate"] = rate

    return rate == get_attendance_rate()


def get_snapshot_interval() -> int:
    with shelve.open("database") as handle:
        snapshot_interval: int = handle["snapshot_interval"]

    return snapshot_interval


def set_snapshot_interval(interval: int) -> bool:
    with shelve.open("database") as handle:
        handle["snapshot_interval"] = interval

    return interval == get_snapshot_interval()
