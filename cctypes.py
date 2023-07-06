from typing import TypedDict, Optional
from enum import Enum


class RequestType(Enum):
    TEST = 0x00
    START = 0x01
    STOP = 0x02
    PLAYER_INFO = 0xE0
    LOGIN = 0xF0
    KEEP_ALIVE = 0xFF


class Request(TypedDict):
    id: int
    type: int  # RequestType
    code: Optional[str]
    message: Optional[str]
    duration: Optional[int]
    quantity: Optional[int]
    viewer: Optional[str]
    cost: Optional[int]


class ResponseType(Enum):
    EFFECT_REQUEST = 0x00  # Effect Instance Messages
    EFFECT_STATUS = 0x01  # Effect Class Messages
    LOGIN = 0xF0  # Ask a connecting client to login
    LOGIN_SUCCESS = 0xF1  # Tell a connecting client that login was successful
    DISCONNECT = 0xFE  # Tell a client/server that they are being disconnected
    KEEP_ALIVE = 0xFF


class EffectStatus(Enum):
    # Effect Instance Messages
    SUCCESS = 0x00  # Effect triggered successfully
    FAILURE = 0x01  # Effect failed to trigger but is still available to use
    UNAVAILABLE = 0x02  # Effect failed to trigger and should be hidden from the menu
    RETRY = 0x03  # Effect failed to trigger and should be retried in a few seconds
    PAUSED = 0x06  # The timed effect has been paused (i.e. because the game was paused)
    RESUMED = 0x07  # The timed effect has been resumed (i.e. because the game was unpaused)
    FINISHED = 0x08  # The timed effect has finished
    # Effect Class Messages
    VISIBLE = 0x80  # The effect should be visible in the menu
    NOT_VISIBLE = 0x81  # The effect should not be visible in the menu
    SELECTABLE = 0x82  # The effect should be selectable in the menu
    NOT_SELECTABLE = 0x83  # The effect should not be selectable in the menu
    # System Status Messages
    NOT_READY = 0xFF  # The client is not ready to receive messages


class Response(TypedDict, total=False):
    id: int
    type: int  # ResponseType
    code: Optional[str]
    status: Optional[int]  # EffectStatus
    message: Optional[str]
    timeRemaining: Optional[int]  # Time remaining on a timed effect in milliseconds
