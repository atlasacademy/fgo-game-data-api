from hashlib import sha1

import orjson

from ..schemas.rayshift import Deck, QuestDetail


def get_deck_hash_data(decks: list[Deck]) -> list[list[int]]:
    return [[svt.npcId for svt in deck.svts] for deck in decks]


def get_quest_enemy_hash_v1(quest_detail: QuestDetail) -> str:
    enemy_data = {
        "enemyDeck": get_deck_hash_data(quest_detail.enemyDeck),
        "shiftDeck": get_deck_hash_data(quest_detail.shiftDeck),
    }
    all_npc_ids = [npc_id for stage in enemy_data["enemyDeck"] for npc_id in stage] + [
        npc_id for stage in enemy_data["shiftDeck"] for npc_id in stage
    ]

    enemy_count_hash = len(all_npc_ids) % 100
    npc_id_hash = sum(i % 100 for i in all_npc_ids) // len(all_npc_ids)
    sha1_hash = sha1(orjson.dumps(enemy_data)).hexdigest()[:7]

    return f"1_{enemy_count_hash:>02}{npc_id_hash:>02}_{sha1_hash}"


def get_quest_enemy_hash(version: int, quest_detail: QuestDetail) -> str:
    if version == 1:
        return get_quest_enemy_hash_v1(quest_detail)

    raise NotImplementedError("Unknown quest enemy hash version")
