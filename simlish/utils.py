
import pandas as pd
from pathlib import Path
import logging


ipa_chars = [
    "a",
    "ä",
    "ɑ",
    "ɒ",
    "æ",
    "b",
    "ḇ",
    "β",
    "c",
    "č",
    "ɔ",
    "ɕ",
    "ç",
    "d",
    "ḏ",
    "",
    "ḍ",
    "",
    "ð",
    "e",
    "ə",
    "ɚ",
    "ɛ",
    "ɝ",
    "f",
    "g",
    "ḡ",
    "h",
    "ʰ",
    "ḥ",
    "ḫ",
    "ẖ",
    "i",
    "ɪ",
    "ỉ",
    "ɨ",
    "j",
    "",
    "ʲ",
    "ǰ",
    "k",
    "ḳ",
    "ḵ",
    "l",
    "ḷ",
    "ɬ",
    "ɫ",
    "m",
    "n",
    "ŋ",
    "ṇ",
    "ɲ",
    "ɴ",
    "o",
    "ŏ",
    "ɸ",
    "θ",
    "p",
    "p̅",
    "þ",
    "",
    "q",
    "r",
    "ɹ",
    "ɾ",
    "ʀ",
    "ʁ",
    "ṛ",
    "s",
    "š",
    "ś",
    "",
    "",
    "ṣ",
    "",
    "ʃ",
    "t",
    "ṭ",
    "",
    "ṯ",
    "",
    "ʨ",
    "tʂ",
    "u",
    "ʊ",
    "ŭ",
    "ü",
    "v",
    "ʌ",
    "ɣ",
    "w",
    "ʍ",
    "x",
    "χ",
    "y",
    "",
    "ʸ",
    "ʎ",
    "z",
    "ẓ",
    "",
    "ž",
    "ʒ",
    "’",
    "‘",
    "ʔ",
    "ʕ",
    "",
]


    # some shorthand for analysing weights

start_char = "^"
end_char = "$"


def get_user_dir():
    """
    Get the user's directory for this module.

    #### Returns
    > ##### `pathlib.Path`
    > Path to the user's directory for this module.
    """
    # construct path to home directory
    user_dir = Path.home() / ".simlish"
    # make sure it exists
    if not user_dir.is_dir():
        user_dir.mkdir()
    
    return user_dir


def get_module_dir():
    """
    Get the root directory for this module.
    
    #### Returns
    > ##### `pathlib.Path`
    > Path to this module's root directory
    """
    # get parent of this file
    module_dir = Path(__file__).parent
    # make absolute
    module_dir = module_dir.absolute()

    return Path(module_dir)


def load_language_profile(language, levels=1):
    # try user dir then module dir
    for folder in (get_user_dir(), get_module_dir()):
        # look for profiles folder
        profiles_dir = folder / "profiles"
        # look for language folder
        language_dir = profiles_dir / language
        # if it exists, break
        if language_dir.is_dir():
            break
    # if we found no language, error
    assert language_dir.is_dir()
    # load words
    words = (language_dir / "words.csv").read_text(encoding="utf8").split("\n")
    # load weights for each level
    weights = []
    for lvl in range(levels):
        # account for zero indexing
        lvl += 1
        # construct weights file name
        weights_file = language_dir / f"weights{lvl}.csv"
        # if there isn't one, populate
        if not weights_file.is_file():
            logging.warning(
                f"Running language {language} at level {lvl} for the first time, there may be a considerable delay while the weights array is generated..."
            )
            from .setup import populate_language_profile
            populate_language_profile(language=language, levels=lvl)
        # load and append weights from file
        weights.append(
            pd.read_csv(
                str(weights_file),
                header=0, index_col=0
            )
        )
    
    return words, weights
