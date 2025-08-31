import spacy
import re
import dateparser
from typing import List, Dict, Tuple
from datetime import datetime
from TD5 import *


# * mot clé à capturer :

# * dates (trouvable grace à leurs formats)
# * "titre"
# * "rubrique"
# * "auteur"
# * "articles"

# * logique
# * "ou"
# * "et"
# * "soit" ... "soit" ... (équivalent de "ou")
# * "pas" ... (équivalent de "non")


class Requete:
    """
    Class representing a search query.

    Args:
        The different arguments represent the various tags/fields of an article.
        The "common" element is considered applicable to any tag/field.
    """

    def __init__(
        self,
        date_debut: str = None,
        date_fin: str = None,
        common: List[str] = [None],
        titre: List[str] = [None],
        texte: List[str] = [None],
        rubrique: List[str] = [None],
        auteur: List[str] = [None],
    ):
        """
        Initializes a search query object.

        Args:
            date_debut (str): Start date of the query.
            date_fin (str): End date of the query.
            common (List[str]): Keywords common to any field.
            titre (List[str]): Keywords for the title field.
            texte (List[str]): Keywords for the text/content field.
            rubrique (List[str]): Keywords for the section/category field.
            auteur (List[str]): Keywords for the author field.
        """
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.common = common
        self.titre = titre
        self.texte = texte
        self.rubrique = rubrique
        self.auteur = auteur

    def __str__(self):
        """Returns a string representation of the query object."""
        return (
            f"Requete(date_debut={self.date_debut}, date_fin={self.date_fin},"
            f" common={self.common}, titre={self.titre}, texte={self.texte},"
            f" rubrique={self.rubrique}, auteur={self.auteur})"
        )


def extraire_type_mot(texte: str) -> List[Tuple[str, str]]:
    """Returns a dictionary of (word, word_type) pairs from the given query using the spacy module"""
    nlp = spacy.load("fr_core_news_lg")
    doc = nlp(texte)
    list_result = [(mot.text, mot.tag_) for mot in doc]
    return list_result


def normaliser_date(date_str: str) -> str:
    """
    Converts various French date formats into the standard DD/MM/YYYY format.

    Args:
        date_str (str): A date string in various possible formats (e.g., "12 05 2023", "05/2023", "2023").

    Returns:
        str: The normalized date string in "DD/MM/YYYY" format, or None if the input cannot be parsed.

    Notes:
        - Accepts dates with spaces or slashes as separators.
        - Handles full dates, month/year, and year-only formats.
        - Uses French language parsing for date interpretation.
    """
    """Convertie tout type de date en format JJ/MM/AAAA"""
    date_str = date_str.replace(" ", "/")
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        return date_str
    if re.match(r"^\d{2}/\d{4}$", date_str):  # cas mois/année
        date_str = f"1/{date_str}"
    if re.match(r"^\d{4}$", date_str):  # cas mois seul
        date_str = f"1/1/{date_str}"
    date = dateparser.parse(date_str, languages=["fr"])
    if not date:
        return None
    return date.strftime("%d/%m/%Y")


def pretreat_text(text: str) -> str:
    """
    Removes special characters except "-", converts text to lowercase,
    and removes 'l'' and 'd'' before words.

    Args:
        text (str): The input text to preprocess.

    Returns:
        str: The preprocessed text.
    """
    text = text.lower()
    liste = text.split(" ")
    mots_traités = []
    for element in liste:
        if len(element) > 2 and element[0] in ["d", "l"] and element[1] in ["'", "’"]:
            element = element[2:]
        mots_traités.append(element)

    text = " ".join(mots_traités)
    text = text.replace("/", " ")
    text = re.sub(r"[^\w\s\-']", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_logical_operators(phrase: str) -> str:
    """
    Decomposes a string into a list of words separated by logical operators (NOT, AND, OR).
    Replaces French logical operator words with their corresponding logical operator in English.
    Removes specified words that should be suppressed from the result.
    Returns a string of keywords and logical operators suitable for constructing a query.

    Args:
        phrase (str): The input string to be processed.

    Returns:
        str: The processed string with logical operators replaced and unwanted words removed.
    """
    logical_operators = {
        "et": "AND",
        "ou": "OR",
        "soit": "OR",
        "pas": "NOT",
        "non": "NOT",
        "ne": "NOT",
        "ni": "AND NOT",
        "sans": "AND NOT",
        "sauf": "AND NOT",
        "excepté": "AND NOT",
    }
    word_to_suppress = ["l'", "d'", "mais"]
    liste_mots = phrase.split()
    liste_res = []
    for words in liste_mots:
        if words in logical_operators.keys():
            liste_res.append(logical_operators[words])
        else:
            liste_res.append(words)
    liste_res = [
        word for word in liste_res if word not in word_to_suppress
    ]  # remove the words to suppress
    return " ".join(liste_res)


def keep_useful_words(str_to_test: str) -> List[str]:
    """
    Extracts and returns a list of useful words from the input string, filtering out common contractions,
    certain stopwords, and handling logical operators and specific patterns.
    The function processes the input string by:
    - Extracting word-type pairs using `extraire_type_mot`.
    - Keeping logical operators ("AND", "OR", "NOT").
    - Skipping the word "qui".
    - Handling specific verbs ("parlant", "mentionnant", etc.) to mark the next word as "common".
    - Special handling for the word "rubrique" followed by certain patterns.
    - Including words with specific POS tags (NOUN, PROPN, NUM, ADJ, ADV, CCONJ, DET), excluding pronouns.
    - Removing words found in a predefined list of contractions and common words.
    - Replacing "à" with "a" in the result.
    Args:
        str_to_test (str): The input string to process.
    Returns:
        List[str]: A list of filtered and processed words considered useful for further analysis.
    """

    logical_operator = ["AND", "OR", "NOT"]
    list_type_word = extraire_type_mot(str_to_test)
    list_result = []
    contractions_to_remove = [
        "du",
        "des",
        "au",
        "aux",
        "le",
        "la",
        "les",
        "un",
        "une",
        "de",
        "d",
        "l",
        "année",
        "ville",
        "cité",
        "terme",
        "mois",
        "domaine",
        "est",
    ]
    next_is_common = False

    for i in range(len(list_type_word)):
        mot, tag = list_type_word[i]
        if mot in logical_operator:
            list_result.append(mot)
        elif mot == "qui":
            continue
        elif mot in [
            "parlant",
            "mentionnant",
            "évoquant",
            "parlent",
            "évoquent",
            "mentionnent",
        ]:
            next_is_common = True
        elif next_is_common:
            if mot not in contractions_to_remove:
                list_result.append("common")
                list_result.append(mot)
                next_is_common = False
        elif mot == "rubrique" and i + 3 < len(list_type_word):
            if list_type_word[i + 1][0] == "est":
                list_result.append(mot)
                list_result.extend([list_type_word[i + 2][0], list_type_word[i + 3][0]])
            else:
                list_result.append(mot)
                list_result.extend([list_type_word[i + 1][0], list_type_word[i + 2][0]])
        elif tag in [
            "NOUN",
            "PROPN",
            "NUM",
            "ADJ",
            "ADV",
            "CCONJ",
            "DET",
        ] and tag not in ["PRON"]:
            if mot not in contractions_to_remove:
                list_result.append(mot)
    print("keep_useful_words", list_type_word)
    for i, element in enumerate(list_result):
        if element == "à":
            list_result[i] = "a"
    print("Keep_useful_words", list_result)
    return list_result


def convert_dates(str_list: List[str], keyword_date: str = "#d#") -> List[str]:
    """
    Converts date expressions in a list of keywords to the standard DD/MM/YYYY format.
    Adds a keyword (default "#d#") before each detected date.

    Args:
        str_list (List[str]): List of keywords, possibly containing date expressions.
        keyword_date (str): Keyword to insert before each detected date.

    Returns:
        List[str]: List of keywords with dates normalized and marked.
    """
    str_list_res = []
    counter = 0
    while counter < len(str_list):
        # If the current word is a French month name, replace it with its numeric value
        if str_list[counter] in [
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ]:
            mois_map = {
                "janvier": "01",
                "février": "02",
                "mars": "03",
                "avril": "04",
                "mai": "05",
                "juin": "06",
                "juillet": "07",
                "août": "08",
                "septembre": "09",
                "octobre": "10",
                "novembre": "11",
                "décembre": "12",
            }
            str_list[counter] = mois_map[str_list[counter]]
        # If the current word is a digit, check if it is a year or a day
        if str_list[counter].isdigit():

            print(str_list[counter])

            # If it's a 4-digit year and not in the future
            if (
                len(str_list[counter]) == 4
                and int(str_list[counter]) <= datetime.now().year
            ):
                normalised = normaliser_date(str_list[counter])
                if normalised:
                    str_list_res += [keyword_date, normalised]

            # If it's a possible day (1 or 2 digits, <= 31)
            if (
                len(str_list[counter]) == 1
                or len(str_list[counter]) == 2
                and int(str_list[counter]) <= 31
            ):
                # Try to parse as "day month year" or "day month"
                trois_elements = str_list[counter : counter + 3]
                deux_elements = str_list[counter : counter + 2]

                normaliser_date_3 = normaliser_date(" ".join(trois_elements))
                normaliser_date_2 = normaliser_date(" ".join(deux_elements))

                if normaliser_date_3:
                    # Group elements as DD/MM/YYYY and add to result
                    str_list_res += [keyword_date, normaliser_date_3]
                    # Skip the next two elements (already grouped)
                    counter += 2
                elif normaliser_date_2:
                    # Group elements as MM/YYYY and add to result
                    str_list_res += [keyword_date, normaliser_date_2]
                    counter += 1

        else:
            # If not a date, keep the word as is
            str_list_res.append(str_list[counter])

        counter += 1
    return str_list_res


def convert_to_dict(requete: List[str]) -> Dict[str, str]:
    """Convertie une liste de mots clés en un dictionnaire de requête"""

    word_to_find = [
        "articles",
        "article",
        "titre",
        "texte",
        "rubrique",
        "rubriques",
        "auteurs",
        "auteur",
        "#d#",
        "mot",
        "mots",
    ]

    dico_requete = {}
    dico_requete["date_debut"] = None
    dico_requete["date_fin"] = None
    dico_requete["common"] = []  # les mots en commun entre les champs
    dico_requete["titre"] = []
    dico_requete["texte"] = []
    dico_requete["rubrique"] = []
    dico_requete["auteur"] = []

    activ_key = {"titre": False, "texte": False, "rubrique": False, "auteur": False}

    force_common = False

    if "article" in requete:
        start_index = requete.index("article") + 1
    elif "articles" in requete:
        start_index = requete.index("articles") + 1
    else:
        start_index = 0
    requete = requete[start_index:]

    def make_activ(keys: List[str] = activ_key.keys()):
        """Met à jours les clés activ_key en fonction de la clé activée"""
        for key in activ_key.keys():
            if key in keys:
                activ_key[key] = True
            else:
                activ_key[key] = False

    counter = 0
    while counter < len(requete):
        # print(counter,requete[counter])
        if requete[counter] == "#d#":
            if counter + 1 < len(requete):
                if dico_requete["date_debut"] is None:
                    dico_requete["date_debut"] = requete[counter + 1]
                else:
                    dico_requete["date_fin"] = requete[counter + 1]
                counter += 2
                continue

        if requete[counter] == "common":
            force_common = True
            counter += 1
            continue

        elif requete[counter] == "titre":
            activ_key["titre"] = True
            counter += 1

        elif requete[counter] == "texte":
            make_activ(["texte", "titre"])
            counter += 1

        elif requete[counter] in ("rubrique", "rubriques"):
            make_activ(["rubrique"])
            force_common = False
            counter += 1

        elif requete[counter] in ("auteur", "auteurs"):
            make_activ(["auteur"])
            counter += 1

        # else:
        #     make_activ()
        if counter < len(requete):
            if force_common:
                dico_requete["common"].append(requete[counter])
            else:
                for key, activ_bool in activ_key.items():
                    if activ_bool:
                        dico_requete[key].append(
                            requete[counter]
                        )  # on ajoute le mot à la liste de la clé activée
            counter += 1

    # Retirer les doublons dans common
    dico_requete["common"] = list(dict.fromkeys(dico_requete["common"]))

    # pour toutes les clé dont les values ne sont pas remplis, on les remplit avec tout les mots non présent dans les autres clés
    # on remplit également l'élement "common" avec ces éléments
    for _, mot in enumerate(requete):
        if (
            mot not in dico_requete["titre"]
            and mot not in dico_requete["texte"]
            and mot not in dico_requete["rubrique"]
            and mot not in dico_requete["auteur"]
        ):
            dico_requete["common"].append(
                mot
            )  # on ajoute le mot à la liste de la clé common

    #! ajout des mots trouvés au dictionnaire de la requête
    if dico_requete["date_debut"] is not None:
        word_to_find.append(dico_requete["date_debut"])  # ajout de la date de début
    if dico_requete["date_fin"] is not None:
        word_to_find.append(dico_requete["date_fin"])  # ajout de la date de fin
    for key in dico_requete.keys():  # pour chaque clé du dictionnaire, on ajoute le mot
        if key != "date_debut" and key != "date_fin":
            dico_requete[key] = [
                mot for mot in dico_requete[key] if mot not in word_to_find
            ]  # on enlève les mots clés de la liste
    print(dico_requete)

    #! transforme chaque champs de dico_requete en une liste de mots séparés par des opérateurs logiques
    #! on enlève le dernier élément de la liste si c'est un opérateur logique (évite les erreurs de syntaxe)
    #! on ajoute un "AND" entre chaque mot si il n'y a pas d'opérateur logique entre deux mots
    logical_ops = ["AND", "OR", "NOT"]
    for key in dico_requete.keys():
        if (
            dico_requete[key] != []
            and dico_requete[key] != None
            and key != "date_debut"
            and key != "date_fin"
        ):  # si la liste est vide, on la remplit avec un mot vide
            dico_requete[key] = (
                dico_requete[key][:-1]
                if dico_requete[key][-1] in logical_ops
                else dico_requete[key]
            )  # on enlève le dernier élément de la liste si c'est un mot vide

            for i in range(len(dico_requete[key]) - 1):
                liste_modif = []
                for i in range(len(dico_requete[key])):
                    liste_modif.append(dico_requete[key][i])
                    # Check if the current and next elements are not logical operators
                    if i < len(dico_requete[key]) - 1:
                        if (
                            dico_requete[key][i] not in logical_ops
                            and dico_requete[key][i + 1] not in logical_ops
                        ):
                            liste_modif.append("AND")
                # dico_requete[key] = liste_modif
                dico_requete[key] = liste_modif if liste_modif else dico_requete[key]
    return dico_requete


def convert_to_requete(dico_requete: Dict[str, str]) -> Requete:
    """Convertie un dictionnaire de requête en un objet Requete,
    permet une meilleur manipulation de la requête par la suite
    (voir TD7.py et MainWindow.py)"""
    return Requete(
        date_debut=dico_requete["date_debut"],
        date_fin=dico_requete["date_fin"],
        common=dico_requete["common"],  # les mots en commun entre les champs
        titre=dico_requete["titre"],
        texte=dico_requete["texte"],
        rubrique=dico_requete["rubrique"],
        auteur=dico_requete["auteur"],
    )


def request_to_mot_lexique(requete: Requete) -> Requete:
    """
    Transforms each field of the given Requete object by converting its elements to lexicon words using Levenshtein distance.

    For each attribute in the Requete object (except for special attributes, 'rubrique', and 'auteur'):
        - Removes the string "common" from list attributes.
        - Removes trailing logical operators ("and", "or", "not") from list attributes.
        - Joins the list into a phrase and applies a lemmatization function (using a lexicon file) to map words to their base forms.
        - Updates the attribute with the lemmatized words, excluding any None values.

    After processing, ensures that no attribute list ends with a logical operator.

    Args:
        requete (Requete): The request object whose fields are to be transformed.

    Returns:
        Requete: The modified request object with fields mapped to lexicon words.
    """
    """Applique une transformation sur chaques champs de la requete pour les transformer en mot du lexiques avec Levenshtein"""
    for attr in dir(requete):
        if (
            not attr.startswith("__") and attr != "rubrique" and attr != "auteur"
        ):  # Ignore special attributes and 'rubrique', 'auteur'
            element = getattr(requete, attr)
            if isinstance(element, list) and len(element) > 0:
                for e in element[:]:
                    if e == "common":
                        element.remove(e)
                if element[-1] in ["and", "or", "not"]:
                    element = element[:-1]
                # Keep only words that are in the lexicon
                element_phrase = " ".join(element)
                # Apply the TD5 function to transform words to lemma
                base_dir = os.path.dirname(os.path.abspath(__file__))
                dico_mot = phrase_to_dict_lexique(
                    element_phrase, os.path.join(base_dir, "..", "data", "lexique.txt")
                )
                setattr(
                    requete, attr, [mot for mot in dico_mot.values() if mot is not None]
                )
    # For each attribute of the request, if the last element is in ["and", "or", "not"], remove it
    for attr in dir(requete):
        if not attr.startswith("__"):
            element = getattr(requete, attr)
            if isinstance(element, list) and len(element) > 0:
                if element[-1] in ["and", "or", "not"]:
                    element.pop()
                    setattr(requete, attr, element)
    # For each attribute of the request, if the last element is in ["and", "or", "not"], remove it
    return requete


#! -------------------------------------------------------- !#
#! ---------------------- FINAL FUNCTION ------------------ !#
#! -------------------------------------------------------- !#
def convert_str_to_requete(str_to_convert: str) -> Requete:
    """
    Converts a string into a Requete object.

    This function processes the input string through several steps:
    - Preprocesses the text (removes special characters, lowercases, etc.).
    - Replaces French logical operators with their English equivalents.
    - Keeps only useful words for the query.
    - Detects and normalizes date expressions.
    - Converts the list of keywords into a dictionary structure.
    - Converts the dictionary into a Requete object.
    - Maps words to their lexicon forms using lemmatization.

    Args:
        str_to_convert (str): The input string to convert.

    Returns:
        Requete: The resulting Requete object.
    """
    pretreated = pretreat_text(str_to_convert)
    logical_filtered = find_logical_operators(pretreated)
    kept_words = keep_useful_words(logical_filtered)
    dated_words = convert_dates(kept_words)
    dico = convert_to_dict(dated_words)
    requete_obj = convert_to_requete(dico)
    final_requete = request_to_mot_lexique(requete_obj)
    return final_requete


if __name__ == "__main__":

    # # Exemple d'utilisation de la fonction extraire_texte
    # text_path = "new_requetes.txt"

    # print(pretreat_text("Je voudrais les articles qui parlent d’airbus ou du projet Taxibot."))
    print(
        pretreat_text("Je voudrais les articles de la rubrique focus parlant d’avion")
    )
