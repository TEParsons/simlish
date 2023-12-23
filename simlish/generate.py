import pandas as pd
import numpy as np
from .utils import load_language_profile, ipa_chars, start_char, end_char

def random_word(language="en_UK", levels=1):
    words, weights = load_language_profile(language, levels=levels)

    # function to try one build
    def try_build():
        # start off with last char as start char
        word = start_char
        # pad word with start chars
        for n in range(levels):
            word = start_char + word
        # work one phoneme at a time...
        while not word.endswith(end_char):
            # get weights according to previous chars
            p = 1
            for lvl, this_weights in enumerate(weights):
                lvl += 1
                p *= this_weights.loc[word[-lvl]]
            # normalize weights
            p = p.div(p.sum()).fillna(0)
            # choose next letter
            word += np.random.choice(
                ipa_chars + [end_char], 
                p=p
            )
        # remove start and end chars
        word = word.replace(start_char, "").replace(end_char, "")

        return word

    # keep trying to build until it's a word not in the lexicon
    word = words[0]
    while word in words:
        word = try_build()

    return word


def random_sentence(language="en_UK", length=20, levels=1):
    """
    Create a sentence of random simlish words, modelled on a particular language.
    
    #### Args
    > ##### `language: str = "en_UK"`
    > Language to write in

    > ##### `length: int`
    > Number of words to use

    > ##### `levels: int = 1`
    > Number of previous phonemes to consider when generating each new phoneme. High level means better prediction, but will take longer.
    
    #### Returns
    > ##### `str`
    > Random sentence, in IPA, matching the chosen language.
    """
    sentence = []
    # generate each word
    for i in range(length):
        sentence.append(
            random_word(language, levels=levels)
        )
    
    return " ".join(sentence)
