from ...data.gamedata import masters
from ...schemas.common import Region


def get_illustrator_name(region: Region, illustratorId: int) -> str:
    if illustratorId in masters[region].mstIllustratorId:
        return masters[region].mstIllustratorId[illustratorId].name
    else:
        return ""
