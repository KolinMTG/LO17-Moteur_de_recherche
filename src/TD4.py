import xml.etree.ElementTree as ET
import snowballstemmer
import re
import pandas as pd
from typing import Dict
import spacy
from TD3 import *
from tqdm import tqdm


def generate_nltk(corpus_filtered_path: str, save_path: str):
    """Generates a file in the format {article_name}\t{word}\t{stemmed_word}
    from the filtered corpus using the Snowball stemmer."""

    with open(corpus_filtered_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)
        root = tree.getroot()
        bulletins = root.findall(
            "bulletin"
        )  # recuperation de tous les bulletins du corpus

        with open(save_path, "w", encoding="utf-8") as wrt_file:

            for bulletin in bulletins:
                article_name = bulletin.find("fichier").text
                text = str(bulletin.find("texte").text) + str(
                    bulletin.find("titre").text
                )  # recuperation du texte et du titre
                words = re.split(
                    r"[ \-']", text
                )  # split on space, hyphen and apostrophe

                for word in words:
                    new_word = snowballstemmer.stemmer("french").stemWord(
                        word
                    )  # stem the word
                    wrt_file.write(
                        f"{article_name}\t{word}\t{new_word}\n"
                    )  # write the article name and the word
    print(f"generate_nltk : File {save_path} generated successfully.")


def preprocess(text: str) -> str:
    """Remove the punctuation and lower the text"""
    return re.sub(r"[^\w\s'-]", "", text.lower()).replace("\n", "")


def add_article_to_xml(
    save_path: str, article_dict: Dict[str, str], img_dict: Dict[str, str]
) -> None:
    """Add the article information to the XML file
    Args :
        - save_path : the path of the XML file
        - article_dict : a dictionary with the article information
        - img_dict : a dictionary with the images information

    /!\ This function is used in generate_stem_coprus /!\ """

    try:
        tree = ET.parse(save_path)  # try to open an existing XML file
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        # create a new valide XML file
        root = ET.Element("corpus")
        tree = ET.ElementTree(root)
        tree.write(save_path, encoding="utf-8", xml_declaration=True)

    article = ET.SubElement(root, "bulletin")

    for key, value in article_dict.items():
        element = ET.SubElement(article, key)
        element.text = value

    images = ET.SubElement(article, "images")
    for url, legende in img_dict.items():
        image = ET.SubElement(images, "image")
        url_element = ET.SubElement(image, "urlImage")
        url_element.text = url
        legende_element = ET.SubElement(image, "legendeImage")
        legende_element.text = legende
    tree.write(save_path, encoding="utf-8", xml_declaration=True)


def generate_stem_corpus(xml_path: str, output_path: str, stem_path: str) -> None:
    """Args :"
    xml_path : str -> path to the xml file (.xml)
    output_path : str -> path to the output xml file (.xml)
    stem_path : str -> path to the file containing the stem of the words (.txt)"""

    tree = ET.parse(xml_path)
    root = tree.getroot()
    bulletins = root.findall("bulletin")
    stem_df = pd.read_csv(
        stem_path, sep="\t", header=None, names=["Document", "Mot", "Stem"]
    )
    stem_df["Document"] = stem_df["Document"].astype(str)

    for bulletin in tqdm(bulletins, desc="Generating stem corpus, pease wait..."):

        text = bulletin.find("texte").text
        title = bulletin.find("titre").text

        text = re.split(r"[ \-']", preprocess(text))
        title = re.split(r"[ \-']", preprocess(title))
        file_name = bulletin.find("fichier").text  # name of the file in the bulletin
        words = stem_df[stem_df["Document"] == file_name]["Mot"].tolist()
        stems = stem_df[stem_df["Document"] == file_name][
            "Stem"
        ].tolist()  # all word selected for the given file

        new_text = ""
        new_title = " "

        for word in text:
            if word in words:
                new_text += (
                    str(
                        stem_df[
                            (stem_df["Document"] == file_name)
                            & (stem_df["Mot"] == word)
                        ]["Stem"].values[0]
                    )
                    + " "
                )
        try:
            for word in title:
                if word in words:
                    new_title += (
                        str(
                            stem_df[
                                (stem_df["Document"] == file_name)
                                & (stem_df["Mot"] == word)
                            ]["Stem"].values[0]
                        )
                        + " "
                    )
        except:
            continue

        article_dict = {
            "fichier": file_name,
            "texte": new_text,
            "titre": new_title,
            "date": bulletin.find("date").text,
            "rubrique": bulletin.find("rubrique").text,
            "auteur": bulletin.find("auteur").text,
            "contact": bulletin.find("contact").text,
        }

        img_dict = bulletin.find("images")
        if img_dict is not None:
            img_dict = {
                image.find("urlImage").text: image.find("legendeImage").text
                for image in img_dict
            }
        else:
            img_dict = {}

        add_article_to_xml(output_path, article_dict, {})
    print(f"generate_stem_corpus : File {output_path} generated successfully.")


def generate_lemme_with_spacy(corpus_filtered_path: str, save_path: str) -> None:
    """Generates a file in the format {article_name}\t{word}\t{lemme}"""
    nlp = spacy.load("fr_core_news_sm")  # Load the French spaCy model

    with open(corpus_filtered_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)  # Parse the XML file
        root = tree.getroot()
        bulletins = root.findall("bulletin")  # Get all bulletins

        with open(save_path, "w", encoding="utf-8") as wrt_file:
            for bulletin in tqdm(
                bulletins, desc="Generating lemmes with spacy, please wait..."
            ):
                article_name = bulletin.find("fichier").text  # Get the article name
                texte = (
                    str(bulletin.find("texte").text or "")
                    + " "
                    + str(bulletin.find("titre").text or "")
                )  # Concatenate text and title

                words = re.split(r"[ \-']", texte)  # Split text into words

                for word in words:
                    word = word.strip()
                    if word and word.isalpha():  # ignore empty or numeric tokens
                        doc = nlp(word)  # Process the word with spaCy
                        if len(doc) > 0:
                            lemme = doc[0].lemma_  # Get the lemma
                            wrt_file.write(
                                f"{article_name}\t{word}\t{lemme}\n"
                            )  # Write to file

    print(f"generate_lemme_with_spacy : File {save_path} generated successfully.")


def count_unique_lemme(lemme_path: str) -> None:
    """Takes a lemma file as a parameter and counts the number of unique lemmas.
    Writes the result to the command terminal."""
    lemmes = {}  # dictionary: lemma -> number of occurrences
    with open(lemme_path, "r", encoding="utf-8") as f:
        for ligne in f:
            colonnes = ligne.strip().split("\t")
            if len(colonnes) >= 3:
                lemme = colonnes[2].strip().lower()
                if lemme:
                    if lemme in lemmes:
                        lemmes[lemme] += 1
                    else:
                        lemmes[lemme] = 1

    print(f"Nombre de lemmes uniques : {len(lemmes)}")  # Number of unique lemmas

    with open("lemme_sortie.txt", "w", encoding="utf-8") as out:
        for lemme in sorted(lemmes.keys()):
            out.write(f"{lemme}\t{lemmes[lemme]}\n")


def generer_fichier_inverse(corpus_stem_path: str, save_path: str) -> None:
    """
    Function that generates the inverted file from the stemmed corpus.
    format word; doc1, doc2, doc3; len(doc)"""

    # Initialize the inverted dictionary
    with open(corpus_stem_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)
        root = tree.getroot()
        bulletins = root.findall("bulletin")  # retrieve all bulletins from the corpus
        dico_word = {}
        # dico_word = {word: [doc1, doc2, doc3]}

        with open(save_path, "w", encoding="utf-8") as wrt_file:

            for bulletin in bulletins:
                article_name = bulletin.find("fichier").text  # retrieve the file name
                text = (
                    bulletin.find("texte").text + bulletin.find("titre").text
                )  # retrieve the text and the title
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
                wrt_file.write(word + ";")
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
