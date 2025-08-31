import re
import pandas as pd
import numpy as np
from typing import *
from TD4 import *


def convert_lemmes_to_lexique(lemmes_path: str, lexique_path: str) -> None:
    """Takes as argument the path to two files
    - nltk file in the form num_doc, word, lemma
    - lexicon file in the form word, lemma (with unique word,lemma pairs)"""
    df = pd.read_csv(lemmes_path, sep="\s+", names=["num_article", "mot", "lemme"])

    # Keep only the 'mot' and 'lemme' columns
    lexique = df[["mot", "lemme"]].drop_duplicates()
    lexique.to_csv(lexique_path, sep="\t", index=False, header=False)
    print(f"convert_lemmes_to_lexique: File {lexique_path} generated successfully.")


def pre_process(phrase: str) -> str:
    """Pre-process the phrase to remove unwanted characters and lower the case."""
    phrase = re.sub(r"[^\w\s'-]", "", phrase.lower()).replace("\n", "")
    phrase = re.sub(r"[\(\)\[\]]", "", phrase)
    return phrase


def word_in_lexique(mot_teste: str, df: pd.DataFrame) -> List[str]:
    """
    Function that checks if the word is in the lexicon and returns the associated lemma(s).
    If not found, returns the word(s) from the lexicon with the highest number of common letters.
    If no common letters, returns [None].
    """
    # Check if the word exists in the lexicon
    if (df["mot"] == mot_teste).any():
        # Return the lemma associated with the word
        return [df.loc[df["mot"] == mot_teste, "lemme"].iloc[0]]
    else:
        # Dictionary to store the number of common letters for each lexicon word
        dictionnaire_score = {}
        for mot_lexique in df["mot"]:
            if isinstance(mot_lexique, str) and isinstance(mot_teste, str):
                # Compute the number of common letters between the tested word and the lexicon word
                dictionnaire_score[mot_lexique] = nb_lettre_commune(
                    mot_teste, mot_lexique
                )
        # Find the maximum number of common letters
        max_val = max(dictionnaire_score.values())
        # Return all words with the maximum number of common letters, or [None] if no common letters
        return (
            [mot for mot, val in dictionnaire_score.items() if val == max_val]
            if max_val > 0
            else [None]
        )


#! -------------------------------------- !#
#! Calcule de la distance de Levenshtein  !#
#! -------------------------------------- !#


def nb_lettre_commune(mot1: str, mot2: str) -> int:
    """Renvoie le nombre de lettres en commun entre les deux mots.
    Cette fonction est utilisé pour le calcul de la distance de Levenshtein."""
    i = 0
    while i < min(len(mot1), len(mot2)) and mot1[i] == mot2[i]:
        i += 1
    score = i
    return score


def Levenshtein(mot1: str, mot2: str) -> int:
    """Levenshtein distance between two words."""
    dist = np.zeros((len(mot1) + 1, len(mot2) + 1), dtype=int)

    # Initialize the first row and column
    for i in range(len(mot1) + 1):
        dist[i][0] = i
    for j in range(len(mot2) + 1):
        dist[0][j] = j

    for i in range(1, len(mot1) + 1):
        for j in range(1, len(mot2) + 1):
            if mot1[i - 1] == mot2[j - 1]:
                cost = 0
            else:
                cost = 1
            dist[i][j] = min(
                dist[i - 1][j] + 1, dist[i][j - 1] + 1, dist[i - 1][j - 1] + cost
            )

    return dist[len(mot1)][len(mot2)]


def phrase_to_dict_lexique(
    phrase: str, lexique_path: str
) -> Dict[str, Union[str, None]]:
    """
    Convert a phrase into a dictionary with words as keys and their lemmas as values.
    If a word is not found in the lexicon, tries to find the closest match.
    """
    # Pre-process the phrase: lowercase and remove unwanted characters
    phrase = pre_process(phrase)
    # Load the lexicon as a DataFrame
    df = pd.read_csv(lexique_path, sep="\t", header=None, names=["mot", "lemme"])
    # Split the phrase into words
    liste = phrase.split(" ")
    dictionnaire_phrase = {}
    for mot in liste:
        # Try to find the lemma(s) for the word in the lexicon
        result = word_in_lexique(mot, df)
        new_lemme = None
        if result == [None]:
            # No match found in the lexicon
            new_lemme = None
        elif len(result) == 1:
            # Only one lemma found
            new_lemme = result[0]
        else:
            # Multiple candidate lemmas found
            # Choose the lemma whose associated word is closest to the input word using Levenshtein distance
            min_dist = float("inf")
            best_lemme = None
            for lemme_candidat in result:
                mots_associes = df[df["lemme"] == lemme_candidat]["mot"].unique()
                for mot_associe in mots_associes:
                    dist = Levenshtein(mot, mot_associe)
                    if dist < min_dist:
                        min_dist = dist
                        best_lemme = lemme_candidat
            new_lemme = best_lemme
        # Add the word and its lemma (or None) to the dictionary
        dictionnaire_phrase[mot] = new_lemme
    return dictionnaire_phrase


if __name__ == "__main__":
    lexique_path = "lexique.txt"
    phrase = "le physicien Mathias Dupond qui dirige les opérations de recherche en lien avec la physique (ondes, télécommunications) a racheté une start up crée par Georges."
    print(phrase_to_dict_lexique(phrase, lexique_path))
    # convert_nltk_to_lexique("nltk.txt", "lexique.txt")
