import re
import string
from enum import Enum
from typing import Iterable, Literal, Optional, TypeVar, Union

from pydantic import HttpUrl
from pydantic.tools import parse_obj_as

from ..data.custom_mappings import TRANSLATION_OVERRIDE, TRANSLATIONS, Translation
from ..schemas.common import Language, NiceTrait
from ..schemas.enums import TRAIT_NAME, Trait


TValue = TypeVar("TValue")
TLookup = TypeVar("TLookup")


full_width_uppercase_lookup = {chr(0xFF21 + i): chr(65 + i) for i in range(26)}
half_width_uppercase_lookup = set(string.ascii_uppercase)


def get_translation(
    language: Language,
    text: str,
    override_file: Optional[Translation] = None,
    override_id: Optional[str] = None,
) -> str:
    if text == "":
        return ""

    if language == Language.jp:
        return text

    if (
        override_file
        and override_id
        and override_id in TRANSLATION_OVERRIDE.get(override_file, {})
    ):  # pragma: no cover
        return TRANSLATION_OVERRIDE[override_file][override_id]

    if override_file == Translation.ENEMY and text[:-1] in TRANSLATIONS:
        translated_string = TRANSLATIONS[text[:-1]]
        if text[-1] in full_width_uppercase_lookup:
            corresponding_half_width = full_width_uppercase_lookup[text[-1]]
            return f"{translated_string} {corresponding_half_width}"
        elif text[-1] in half_width_uppercase_lookup and text[-2] != "":
            return f"{translated_string} {text[-1]}"

    return TRANSLATIONS.get(text, text)


def get_np_name(td_name: str, td_ruby: str, language: Language) -> str:
    if language == Language.jp:
        return td_name

    to_translate = td_ruby if td_ruby not in ("", "-") else td_name
    translation = get_translation(language, to_translate)

    if to_translate == translation:
        return td_name

    return translation


VOICE_NAME_REGEX = re.compile(r"^(.*?)(\d+)$", re.DOTALL)


def get_voice_name(
    voice_name: str,
    language: Language,
    override_file: Union[
        Literal[Translation.VOICE], Literal[Translation.OVERWRITE_VOICE]
    ],
) -> str:
    if language == Language.en:
        if match := VOICE_NAME_REGEX.match(voice_name):
            name, number = match.groups()
            translated_name = get_translation(language, name, override_file)
            return f"{translated_name.rstrip()} {number}"
        else:
            return get_translation(language, voice_name, override_file)

    return voice_name


def get_nice_trait(individuality: int) -> NiceTrait:
    """Return the corresponding NiceTrait object given the individuality"""
    if individuality >= 0:
        return NiceTrait(
            id=individuality, name=TRAIT_NAME.get(individuality, Trait.unknown)
        )

    return NiceTrait(
        id=-individuality,
        name=TRAIT_NAME.get(-individuality, Trait.unknown),
        negative=True,
    )


def get_traits_list(input_idv: Iterable[int]) -> list[NiceTrait]:
    """
    Return the corresponding list NiceTrait objects given the individuality list
    """
    return [get_nice_trait(individuality) for individuality in input_idv]


def get_traits_list_list(input_idvs: Iterable[Iterable[int]]) -> list[list[NiceTrait]]:
    return [get_traits_list(vals) for vals in input_idvs]


FORMATTING_BRACKETS = {"[g][o]": "", "[/o][/g]": "", " [{0}] ": " ", "[{0}]": ""}


def strip_formatting_brackets(detail_string: str) -> str:
    """Remove formatting codes such as [g][o] from detail string"""
    for k, v in FORMATTING_BRACKETS.items():
        detail_string = detail_string.replace(k, v)
    return detail_string


def nullable_to_string(nullable: Optional[str]) -> str:
    """Returns an empty string is the input is None"""
    if nullable is None:
        return ""
    else:
        return nullable


def fmt_url(url_fmt: str, **kwargs: int | str | HttpUrl) -> HttpUrl:
    url: HttpUrl = parse_obj_as(HttpUrl, url_fmt.format(**kwargs))
    return url


TFlagEnum = TypeVar("TFlagEnum", bound=Enum)


def get_flags(flag: int, flag_enums: dict[int, TFlagEnum]) -> list[TFlagEnum]:
    return [flag_value for flag_id, flag_value in flag_enums.items() if flag_id & flag]
