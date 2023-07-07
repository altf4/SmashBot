from typing import TypedDict, Literal


EffectStatus = Literal['success', 'delayEstimated', 'failTemporary', 'failPermanent']


class Effect(TypedDict):
    # duration: int
    # image: str
    effectID: str
    name: str
    description: str
    # type: str
    # category: list[str]


class Game(TypedDict):
    gameID: str
    name: str


class GamePack(TypedDict):
    gamePackID: str
    name: str
    platform: str


class User(TypedDict):
    ccUUID: str
    # image: str
    originID: str
    profile: str
    name: str


class EffectPayload(TypedDict):
    requestID: str  # UUID?
    effect: Effect
    quantity: int
    game: Game
    gamePack: GamePack
    target: User
    requester: User


class WhoAmIPayload(TypedDict):
    connectionID: str


class LoginSuccessPayload(TypedDict):
    token: str


class PacketBody(TypedDict):
    domain: Literal['pub', 'prv']
    type: str
    payload: EffectPayload | WhoAmIPayload | LoginSuccessPayload


class ResultData(TypedDict):
    gameSessionID: str  # game_session-XXX


class ResultBody(TypedDict, total=False):
    data: ResultData


class ResultPacket(TypedDict):
    result: ResultBody
