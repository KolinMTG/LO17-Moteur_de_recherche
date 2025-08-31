import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Dict
from functools import reduce
from TD6 import *


def union_listes(liste_de_listes: List[List[str]]) -> List[str]:
    """
    Returns the union of all sublists (without duplicates).

    Args:
        liste_de_listes (list of list): A list containing sublists whose elements will be combined.

    Returns:
        list: A list containing the union of all elements from the sublists, with duplicates removed.
    """
    resultat = set()
    for sous_liste in liste_de_listes:
        resultat |= set(sous_liste)
    return list(resultat)


def intersection_liste(liste_de_listes: List[List[str]]) -> List[str]:
    """Return the intersection of all sublists (without duplicates)."""
    if not liste_de_listes:
        return []
    resultat = set(liste_de_listes[0])
    for sous_liste in liste_de_listes[1:]:
        resultat &= set(sous_liste)
    return list(resultat)


def difference_listes(liste_de_listes: List[List[str]]) -> List[str]:
    """Return the elements of the first list that are not in any of the others (without duplicates)."""
    if not liste_de_listes:
        return []

    resultat = set(liste_de_listes[0])
    for sous_liste in liste_de_listes[1:]:
        resultat -= set(sous_liste)
    return list(resultat)


def compter_occurences(texte: str) -> Dict[str, int]:
    """Count the occurrences of each word in the text and return a dictionary with words as keys and their occurrences as values."""
    words = texte.split()
    dico_word = {}  # dico_word = {word: ocurrence}
    for word in words:
        if word in dico_word:
            dico_word[word] += 1
        else:
            dico_word[word] = 1
    return dico_word


def generer_fichier_pertinence(corpus_stem_path: str, save_path: str) -> None:
    """
    Takes as arguments the path to the stemmed corpus and the output file path.
    Generates a file in the following format:
    document; lemme1, lemme2, ...; pertinence1, pertinence2, ...
    where pertinence is the sum of the word frequency in the title and in the text.
    """

    with open(corpus_stem_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)
        root = tree.getroot()
        bulletins = root.findall("bulletin")  # retrieve all bulletins from the corpus

    with open(save_path, mode="a", encoding="utf-8") as wrt_file:
        for bulletin in bulletins:
            article_name = bulletin.find("fichier").text  # retrieve the file name
            text_texte = bulletin.find(
                "texte"
            ).text  # retrieve the text in the "texte" tag
            text_titre = bulletin.find(
                "titre"
            ).text  # retrieve the text in the "titre" tag

            # count word occurrences in text and title
            occurence_texte = compter_occurences(text_texte)
            occurence_titre = compter_occurences(text_titre)

            # compute word frequencies in text and title
            frequence_texte = {
                mot: occurence_texte[mot] / len(text_texte.split())
                for mot in occurence_texte
            }
            frequence_titre = {
                mot: occurence_titre[mot] / len(text_titre.split())
                for mot in occurence_titre
            }

            # compute pertinence as the sum of frequencies in text and title
            pertinence_mot = {
                mot: frequence_texte.get(mot, 0) + frequence_titre.get(mot, 0)
                for mot in set(frequence_texte) | set(frequence_titre)
            }

            # round pertinence to 3 decimal places
            pertinence_mot = {
                mot: round(pertinence_mot[mot], 3) for mot in pertinence_mot
            }

            # Write to file: format document; lemme1, lemme2, ...; pertinence1, pertinence2, ...
            str_to_write = (
                article_name
                + ";"
                + ",".join(pertinence_mot.keys())
                + ";"
                + ",".join([str(pertinence_mot[mot]) for mot in pertinence_mot.keys()])
                + "\n"
            )
            wrt_file.write(str_to_write)
        wrt_file.close()
    print(f"generer_fichier_pertinence: File {save_path} generated successfully.")


def generer_fichier_inverse_balise(
    corpus_stem_path: str, save_path: str, balise: str, open_mode: str = "w"
) -> None:
    """
    Generates the inverted file for a given tag from the stemmed corpus.
    Format: word; doc1, doc2, doc3; len(doc)
    """
    with open(corpus_stem_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)
        root = tree.getroot()
        bulletins = root.findall("bulletin")  # Retrieve all bulletins from the corpus
        dico_word = {}  # dico_word = {word: [doc1, doc2, doc3]}

        with open(save_path, mode=open_mode, encoding="utf-8") as wrt_file:
            for bulletin in bulletins:
                article_name = bulletin.find("fichier").text  # Get the file name
                text = bulletin.find(balise).text  # Get the text present in the tag

                if text is not None:
                    words = text.split()
                    words = set(words)  # Use a set to avoid duplicates

                    for word in words:
                        if word in dico_word:
                            dico_word[word].append(article_name)
                        else:
                            dico_word[word] = [article_name]

            # Write the inverted file
            for word, articles in dico_word.items():
                # Write the word
                wrt_file.write(str.lower(word) + ";")
                # Write the articles
                for i, article_name in enumerate(articles):
                    if i == len(articles) - 1:
                        wrt_file.write(article_name + ";")
                    else:
                        wrt_file.write(article_name + ",")

                # Write the length of the article list
                wrt_file.write(str(len(articles)) + "\n")

            wrt_file.close()
        src_file.close()


def generer_fichier_inverse_common(save_path: str) -> None:
    """
    Reads all inverted index files in the specified directory, merges their contents by word,
    and generates a common inverted index file. For each word, combines all associated article IDs
    from the different files, removes duplicates, sorts them numerically, and writes the result
    to 'fichier_inverse_common.txt' in the same directory.
    Args:
        save_path (str): The directory path containing the inverted index files to merge.
    Returns:
        None
    Raises:
        None directly, but will print an error if file reading fails.
    Notes:
        - Assumes each input file is a CSV with columns: 'mot', 'articles', 'nb_articles'.
        - Handles both UTF-8 and ISO-8859-1 encodings for input files.
        - The output file will not have a header and will use ';' as a separator.
    """
    """Lis les fichiers inverses des différentes balises et génère un fichier inverse commun."""

    data = {}

    for nom_fichier in os.listdir(save_path):
        chemin = os.path.join(save_path, nom_fichier)
        try:
            df = pd.read_csv(
                chemin,
                sep=";",
                header=None,
                names=["mot", "articles", "nb_articles"],
                dtype=str,
                encoding="utf-8",
            )
        except UnicodeDecodeError:
            # Tentative de lecture avec encodage alternatif
            df = pd.read_csv(
                chemin,
                sep=";",
                header=None,
                names=["mot", "articles", "nb_articles"],
                dtype=str,
                encoding="ISO-8859-1",
            )

        # Fusion des articles par mot
        for _, row in df.iterrows():
            mot = row["mot"]
            articles = row["articles"].split(",")

            if mot in data:
                data[mot] = list(set(data[mot] + articles))
            else:
                data[mot] = articles

    # Construction du DataFrame final
    result = pd.DataFrame(
        [
            [mot, ",".join(sorted(set(articles), key=int)), len(set(articles))]
            for mot, articles in sorted(data.items())
        ]
    )

    result.to_csv(
        os.path.join(save_path, "fichier_inverse_common.txt"),
        sep=";",
        index=False,
        header=False,
        encoding="utf-8",
    )
    print(
        f"generer_fichier_inverse_common: File {os.path.join(save_path, 'fichier_inverse_common')} generated successfully."
    )


def generate_all_fichier_inverse(
    corpus_stem_path: str = "corpus_stem.xml",
    save_folder: str = "fichier_inverses",
    balise_list: List[str] = ["texte", "titre", "auteur", "rubrique", "date"],
):
    """Construit tout les fichier inverses, construit également le fichier pour "common" """
    os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist

    for balise in balise_list:
        save_path = os.path.join(save_folder, f"fichier_inverse_{balise}.txt")
        generer_fichier_inverse_balise(corpus_stem_path, save_path, balise)
    print(
        f"generate_all_fichier_inverse: All inverse files generated successfully in {save_folder}"
    )


def liste_articles_in_date_between(
    date_debut: str, date_fin: str, df_date: str
) -> List[str]:
    """
    Returns the set of articles (column 'docs') between date_debut and date_fin that are present in the 'mot' column of df_date.
    If date_debut is None, returns all articles between the minimum date in the df and date_fin.
    If date_fin is None, returns all articles between date_debut and the maximum date in the df.
    """
    # Convert dates to datetime format for easier comparison
    df_date["mot"] = pd.to_datetime(df_date["mot"], format="%d/%m/%Y", errors="coerce")
    df_date = df_date.dropna()  # Remove rows with invalid dates

    if date_debut is not None:
        date_debut = pd.to_datetime(date_debut, format="%d/%m/%Y", errors="coerce")
    if date_fin is not None:
        date_fin = pd.to_datetime(date_fin, format="%d/%m/%Y", errors="coerce")

    # Filter dates based on conditions
    if date_debut is not None and date_fin is not None:
        filtered_dates = df_date[
            (df_date["mot"] >= date_debut) & (df_date["mot"] <= date_fin)
        ]
    elif date_debut is not None:
        filtered_dates = df_date[df_date["mot"] >= date_debut]
    elif date_fin is not None:
        filtered_dates = df_date[df_date["mot"] <= date_fin]
    else:
        filtered_dates = df_date
    res_date = []
    for element in filtered_dates["docs"].tolist():
        res_date += element.split(",")
    return res_date


def find_doc_by_word(word_to_find: str, df: pd.DataFrame) -> list[str]:
    """
    Returns the list of document numbers where the word appears.
    Args:
        word_to_find (str): The word to search for.
        df (pd.DataFrame): The DataFrame containing the inverted index.
    Returns:
        list[str]: List of document numbers where the word is found.
    """
    row = df.loc[df["mot"] == word_to_find, "docs"]
    if row.empty:
        return []
    return row.iloc[0].split(",")


def find_article_for_words(tokens: list[str], df) -> list:
    """
    Evaluates a boolean query with the words AND, OR, NOT, respecting logical priorities.
    Args:
        tokens (list[str]): List of tokens representing the boolean query.
        df (pd.DataFrame): The DataFrame containing the inverted index.
    Returns:
        list: List of document numbers matching the boolean query.
    """

    def get_all_documents():
        """
        Returns all available documents in the DataFrame.
        Returns:
            list[str]: List of all document names (without .txt extension).
        """
        return [f[:-4] for f in os.listdir("BULLETINS") if f.endswith(".txt")]

    def difference_liste_globale(l):
        """
        Returns the difference between the complete set of documents and the provided list.
        Args:
            l (list): List of documents to exclude.
        Returns:
            list: List of documents not in l.
        """
        return list(set(get_all_documents()) - set(l))

    def intersection_listes(listes):
        """
        Returns the intersection of multiple lists of documents.
        Args:
            listes (list of list): Lists to intersect.
        Returns:
            list: Intersection of all lists.
        """
        if not listes:
            return []
        return list(set(listes[0]).intersection(*listes[1:]))

    def union_listes(listes):
        """
        Returns the union of multiple lists of documents.
        Args:
            listes (list of list): Lists to union.
        Returns:
            list: Union of all lists.
        """
        return list(set().union(*listes))

    def eval_not(i):
        """
        Evaluates the NOT operation for the token at position i.
        Args:
            i (int): Current token index.
        Returns:
            tuple: (List of documents, next token index)
        """
        mot = tokens[i + 1]
        return difference_liste_globale(find_doc_by_word(mot, df)), i + 2

    def eval_term(i):
        """
        Evaluates a term or NOT operation at position i.
        Args:
            i (int): Current token index.
        Returns:
            tuple: (List of documents, next token index)
        """
        if tokens[i] == "not":
            return eval_not(i)
        else:
            return find_doc_by_word(tokens[i], df), i + 1

    def eval_and(i):
        """
        Evaluates AND operations starting at position i.
        Args:
            i (int): Current token index.
        Returns:
            tuple: (List of documents, next token index)
        """
        left, i = eval_term(i)
        while i < len(tokens) and tokens[i] == "and":
            right, i = eval_term(i + 1)
            left = intersection_listes([left, right])
        return left, i

    def eval_or(i):
        """
        Evaluates OR operations starting at position i.
        Args:
            i (int): Current token index.
        Returns:
            tuple: (List of documents, next token index)
        """
        left, i = eval_and(i)
        while i < len(tokens) and tokens[i] == "or":
            right, i = eval_and(i + 1)
            left = union_listes([left, right])
        return left, i

    result, _ = eval_or(0)
    print("resultat de la requete : ", result)
    return result


def find_file(request: Requete, path_fichier_inverse_doc: str) -> List[str]:
    """Function that returns the names of the files corresponding to the query.
    /!\ Provide the name of the folder in which to search for the inverted files.
    There is one inverted file per tag in the folder. Format: fichier_inverse_<balise>.txt"""

    print("-------------------------------------------------")
    print("Request : ", request)
    print("-------------------------------------------------")
    #! Read the inverted files, for each tag
    dict_df = {}
    for filename in os.listdir(path_fichier_inverse_doc):
        if filename.endswith(".txt"):
            # Read the CSV file, put it as a DataFrame in a dictionary
            dict_df[re.split(r"[_\.]", filename)[-2]] = pd.read_csv(
                os.path.join(path_fichier_inverse_doc, filename),
                sep=";",
                header=None,
                names=["mot", "docs", "occurences"],
            )

    dict_article = {}  # dictionary of the form {balise: [article1, article2, article3]}
    #! Handle date
    if request.date_debut is not None or request.date_fin is not None:
        dict_article["date"] = liste_articles_in_date_between(
            request.date_debut, request.date_fin, dict_df["date"]
        )
    else:
        dict_article["date"] = None

    #! Handle common words
    dict_article["common"] = (
        find_article_for_words(request.common, dict_df["common"])
        if len(request.common) > 0
        else None
    )

    #! Handle other tags

    for balise in ["texte", "titre", "auteur", "rubrique"]:
        if len(request.__getattribute__(balise)) > 0:
            dict_article[balise] = find_article_for_words(
                request.__getattribute__(balise), dict_df[balise]
            )
        else:
            dict_article[balise] = None

    #! Intersection of articles for each tag if the article list is not None
    liste_article_res = [
        set(articles) for articles in dict_article.values() if articles is not None
    ]

    return (
        list(reduce(lambda x, y: x.intersection(y), liste_article_res))
        if len(liste_article_res) > 0
        else []
    )


def get_pertinence_score(
    path_fichier_pertinence: str, liste_articles: List[str], requete: Requete
) -> Dict[str, float]:
    """Returns the pertinence score for each article in a given list of articles, for a given query."""
    df_pertinence = pd.read_csv(
        path_fichier_pertinence,
        sep=";",
        header=None,
        names=["document", "lemmes", "pertinence"],
        dtype={"document": str, "lemmes": str, "pertinence": str},
    )
    liste_mot_requete = list(
        set(requete.common + requete.texte + requete.titre)
    )  # concatenation of the query word lists
    dico_pertinence = {}
    for article in liste_articles:
        row = df_pertinence.loc[df_pertinence["document"] == article]
        if not row.empty:
            # Retrieve the lemmes and their pertinence
            lemmes = row.iloc[0]["lemmes"].split(",")
            pertinences_mots = row.iloc[0]["pertinence"].split(",")
            pertinences_mots = [float(pertinence) for pertinence in pertinences_mots]
            print(
                [
                    pertinences_mots[lemmes.index(mot)]
                    for mot in liste_mot_requete
                    if mot in lemmes
                ]
            )
            if len(liste_mot_requete) == 0:
                pertinence_article = 0
            else:
                pertinence_article = sum(
                    [
                        pertinences_mots[lemmes.index(mot)]
                        for mot in liste_mot_requete
                        if mot in lemmes
                    ]
                ) / len(liste_mot_requete)
            dico_pertinence[article] = pertinence_article
    return dico_pertinence


#! test
def treat_request(request: str) -> Tuple[Dict[str, int], Requete]:
    """
    Given a query, returns as a dictionary {article: pertinence score} the different articles found for the query and the Requete class.
    """
    requete_associe = convert_str_to_requete(request)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    article_res = find_file(
        requete_associe, os.path.join(base_dir, "..", "data", "fichiers_inverse")
    )  # returns a dictionary of words and their occurrences

    pertinence_score = get_pertinence_score(
        os.path.join(base_dir, "..", "data", "fichier_pertinence.txt"),
        article_res,
        requete_associe,
    )
    print("-------------------------------------------------")
    print("Result of the query: ", article_res)
    print("-------------------------------------------------")
    return pertinence_score, requete_associe


if __name__ == "__main__":
    # utilisation de la fonction pour chaques balises :
    # generer_fichier_pertinence(r"C:\Users\colin\Documents\ETUDE\UTC semestre 4\LO17\lo17\data\corpus_stem.xml", r"C:\Users\colin\Documents\ETUDE\UTC semestre 4\LO17\lo17\data\fichier_pertinence.txt")
    # generate_all_fichier_inverse(r"C:\Users\colin\Documents\ETUDE\UTC semestre 4\LO17\lo17\data\corpus_stem.xml", r"C:\Users\colin\Documents\ETUDE\UTC semestre 4\LO17\lo17\data\fichiers_inverse")
    generer_fichier_inverse_common(
        r"C:\Users\colin\Documents\ETUDE\UTC semestre 4\LO17\lo17\data\fichiers_inverse"
    )
