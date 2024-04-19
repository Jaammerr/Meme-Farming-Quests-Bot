from pydantic import BaseModel


class QuestResult(BaseModel):

    class Steaks(BaseModel):
        total: float
        perWeek: float
        boost: dict
        lastUnstake: dict

    earned: int
    steaks: Steaks


class QuestsList(BaseModel):

    class QuestData(BaseModel):
        id: int
        type: str
        name: str
        description: str
        steaks: int

    quests: list[QuestData]
