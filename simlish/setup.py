import git
import re
import pandas as pd
import numpy as np
from pathlib import Path
from .utils import get_user_dir, get_module_dir, ipa_chars, start_char, end_char


def download_language_words(language):
    """
    Downlaod a language from open-dict-data on GitHub and parse it to the necessary format
    
    #### Args
    > ##### `language: str`
    > Name of the language, as used in the folder structure of open-dict-data/ipa-dict on GitHub

    #### Returns
    > ##### `list[str]`
    > List of all words in the given language, in IPA syntax
    """
    # get user dir
    user_dir = get_user_dir()
    # construct path to repo folder
    repo_dir = user_dir / "ipa-dict"
    # make sure it exists
    if not repo_dir.is_dir():
        repo_dir.mkdir()
    # clone repo if there isn't one
    if not (repo_dir / ".git").is_dir():
        # if we don't have a repo yet, clone it
        git.Repo.clone_from(url="https://github.com/open-dict-data/ipa-dict", to_path=str(repo_dir))
    # make repo object
    repo = git.Repo(path=str(repo_dir))
    # pull repo
    repo.remotes.origin.fetch()
    repo.remotes.origin.pull()
    # get requested language file
    file = repo_dir / "data" / f"{language}.txt"
    # read in content
    content = file.read_text(encoding="utf8")
    # remove punctuation
    content = re.sub(pattern=r"[^{}\n\t/]".format("".join(ipa_chars)), repl="", string=content)
    # remove extra //
    content = re.sub(pattern=r"/.*(/).*/", repl="", string=content)
    # get words in IPA
    words = re.findall(pattern=r"(?<=/).*(?=/)", string=content)
    # find folder for this language
    profile_dir = get_user_dir() / "profiles" / language
    # make sure it exists
    if not profile_dir.is_dir():
        profile_dir.mkdir(parents=True)
    # save file
    words_file = profile_dir / "words.csv"
    words_file.write_text("\n".join(words), encoding="utf8")

    return words
    


def populate_language_profile(language, levels=1, words=None):
    """
    Create a full profile for the given language from a list of IPA words.
    
    #### Args
    > ##### `language: str`
    > Name of the language (e.g. en_UK)
    
    > ##### `words: list[str], Path`
    > List of words in IPA format, or path to a csv file containing list of words.
    """
    # find folder for this language
    profile_dir = get_user_dir() / "profiles" / language
    words_file = profile_dir / "words.csv"
    # make sure it exists
    if not profile_dir.is_dir():
        profile_dir.mkdir(parents=True)
    # make sure it has words
    if not (profile_dir / "words.csv").is_file():
        if isinstance(words, (list, tuple)):
            # if words are a list, save them
            words_file.write_text("\n".join(words), encoding="utf8")
        else:
            # otherwise, get words from module
            words_file.write_text(
                (get_module_dir() / "profiles" / language / "words.csv").read_text(encoding="utf8"),
                encoding="utf8"
            )
    # load words if not given
    if words is None:
        words = words_file.read_text(encoding="utf8").split("\n")
    # calculate weights for each level
    for lvl in range(levels):
        # account for zero indices
        lvl += 1
        # construct weights file path
        weights_file = profile_dir / f"weights{lvl}.csv"
        # load/calculate weights
        if weights_file.is_file():
            # if already defined, just load existing weights
            weights = pd.read_csv(str(weights_file), header=0, index_col=0)
        else:
            # setup pandas array
            weights = pd.DataFrame(
                0,
                columns=ipa_chars + [end_char], index=[start_char] + ipa_chars, 
            )
            # iterate through words
            for word in words:
                # pad word with start/end chars
                for n in range(lvl):
                    word = start_char + word + end_char
                # iterate through chars
                for i in range(len(word)):
                    # skip start char
                    if word[i] == start_char:
                        continue
                    # get last char
                    last_char = word[i-lvl]
                    # get this char
                    this_char = word[i]
                    # add to probability of this_char following last_char
                    weights[this_char][last_char] += 1
            # normalize rows
            weights = weights.div(weights.sum(axis=1), axis=0).fillna(0)
            # save weights
            weights.to_csv(
                str(weights_file), index=True, header=True
            )


def install_language(language):
    """
    Install a language model from GitHub.
    
    #### Args
    > ##### `language: str`
    > Name of the language (e.g. en_UK)
    
    """
    words = None
    for profile_dir in (get_user_dir(), get_module_dir()):
        words_file = profile_dir / language / "words.csv"
        if words_file.is_file():
            # if words are already downloaded folder, use them
            words = words_file.read_text(encoding="utf8").split("\n")
    if words is None:
        # if no words downloaded, get them from github
        words = download_language_words(language)
    # fill out from words
    populate_language_profile(language, words=words)
