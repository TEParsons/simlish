import pandas as pd
import numpy as np
from .utils import load_language_profile, ipa_chars, start_char, end_char

def random_word(language="en_UK"):
    words, weights, lengths = load_language_profile(language)

    # function to try one build
    def try_build():
        # start off with last char as start char
        word = start_char
        # work one phoneme at a time...
        while not word.endswith(end_char) and len(word) < len(lengths.columns):
            word += np.random.choice(
                ipa_chars + [end_char], 
                p=weights.loc[word[-1]]
            )
        # remove start and end chars
        word = word[1:-1]

        return word

    # keep trying to build until it's a word not in the lexicon
    word = words[0]
    while word in words:
        word = try_build()

    return word


def random_sentence(length, language="en_UK"):
    """
    Create a sentence of random simlish words, modelled on a particular language.
    
    #### Args
    > ##### `length: int`
    > Number of words to use
    
    > ##### `language: str = "en_UK"`
    > Language to write in
    
    #### Returns
    > ##### `str`
    > Random sentence, in IPA, matching the chosen language.
    """
    sentence = []
    # generate each word
    for i in range(length):
        sentence.append(
            random_word(language)
        )
    
    return " ".join(sentence)
