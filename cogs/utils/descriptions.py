from typing import Final

# fmt: off
ATTENDANCE_START_SESSION: Final[str] = "Start an attendance session, an instructor must be present in the VC at all times"
ATTENDANCE_STOP_SESSION: Final[str] = "Stop the active attendance session"
ATTENDANCE_GET_ATTENDANCE: Final[str] = "Get an attendance report for your last active attendance session"
ATTENDANCE_CLEAR_ATTENDANCE: Final[str] = "Permanently delete all snapshots from the last active attendance session"

ATTENDANCE_START_SESSION_CHANNEL: Final[str] = "The VC to start taking attendance in"

INSTRUCTOR_ADD: Final[str] = "Add a user to the instructor whitelist"
INSTRUCTOR_REMOVE: Final[str] = "Remove an existing instructor from the instructor whitelist"
INSTRUCTOR_SHOW: Final[str] = "Show the current list of users on the instructor whitelist"

INSTRUCTOR_ADD_MEMBER: Final[str] = "Non-instructor user to add to the instructor whitelist"
INSTRUCTOR_REMOVE_MEMBER: Final[str] = "Existing instructor user to remove from the instructor whitelist"

SETTINGS_GET_MINIMUM_ATTENDANCE: Final[str] = "Get the current minimum attendance rate"
SETTINGS_SET_MINIMUM_ATTENDANCE: Final[str] = "Set the minimum attendance rate"
SETTINGS_GET_INTERVAL: Final[str] = "Get the current snapshot interval"
SETTINGS_SET_INTERVAL: Final[str] = "Set the snapshot interval"
SETTINGS_GET_AUTO_CLEAR: Final[str] = "Get the current auto clear settings"
SETTINGS_SET_AUTO_CLEAR: Final[str] = "Enable or disable snapshot auto clear for a specific event"

SETTINGS_SET_MINIMUM_ATTENDANCE_RATE: Final[str] = "The minimum number, in percentage (0.1 = 10%), of snapshots a user needs to be present in to be counted as in attendance"
SETTINGS_SET_INTERVAL_INTERVAL: Final[str] = "The time interval, in seconds, a snapshot should be taken of the members lists in the session VC"
SETTINGS_SET_AUTO_CLEAR_ON_EVENT: Final[str] = "The event to enable or disable auto clear for"
SETTINGS_SET_AUTO_CLEAR_SHOULD_CLEAR: Final[str] = "Whether or not snapshot data should be auto cleared on this event"
