import re
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from TD2 import *


# ? TD3 P1 Q1
def preprocess(text: str) -> str:
    """Remove the punctuation and lower the text"""
    return re.sub(r"[^\w\s'-]", "", text.lower()).replace("\n", "")


def segment(corpus_path: str, save_path: str):
    """Take in args 2 paths, one to the corpus and the other to save the XML file"""

    with open(corpus_path, "r", encoding="utf-8") as src_file:
        tree = ET.parse(src_file)
        root = tree.getroot()
        bulletins = root.findall(
            "bulletin"
        )  # recuperation de tous les bulletins du corpus

        with open(save_path, "w", encoding="utf-8") as wrt_file:

            for bulletin in bulletins:
                article_name = bulletin.find(
                    "fichier"
                ).text  # recuperation du nom du fichier
                #! modif tf_idf pour le titre
                #! text = bulletin.find("texte").text+bulletin.find("titre").text #recuperation du texte et du titre
                text = bulletin.find("texte").text  # recuperation du texte
                text = preprocess(text)
                words = re.split(
                    r"[ \-']", text
                )  # split on space, hyphen and apostrophe

                for word in words:
                    wrt_file.write(
                        f"{article_name}\t{word}\n"
                    )  # write the article name and the word

            wrt_file.close()
        src_file.close()
    print(f"segment : File {save_path} generated successfully.")


# ? TD3 P1 Q2
def substitue(colonne: str, fichier: str, newfile: str):
    """Take in args 2 paths, one to the corpus and the other to save the XML file
    Replace the words in the file with the words in the column file
    Args :
        - colonne : the path of the column file
        - fichier : the path of the file to be modified
        - newfile : the path of the new file to be created"""

    colonnes_df = pd.read_csv(colonne, sep="\t", header=None, names=["old", "new"])
    colonnes_dict = dict(zip(colonnes_df["old"], colonnes_df["new"]))

    file = pd.read_csv(fichier, sep="\t", header=None, names=["Document", "Mot"])
    file["Mot"] = file["Mot"].replace(colonnes_dict)
    file = file[file["Mot"].notna() & (file["Mot"] != "")]
    file.to_csv(newfile, sep="\t", index=False, header=False)


# ? TD3 P2 Q1
def generate_tf_file(words_file: str, tf_file: str):
    """Generate the tf file from the words file : Format "Document \t word \t tf"""
    words_df = pd.read_csv(words_file, sep="\t", header=None, names=["Document", "Mot"])
    # define the differents columns dtype as string
    words_df["Document"] = words_df["Document"].astype(str)
    words_df["Mot"] = words_df["Mot"].astype(str)
    # add the tf column
    words_df["tf"] = (
        words_df.groupby(["Document", "Mot"])["Mot"].transform("count").astype(int)
    )
    with open(tf_file, "w", encoding="utf-8") as f:
        for _, row in words_df.iterrows():
            f.write(f"{row['Document']}\t{row['Mot']}\t{row['tf']}\n")

    print(f"generate_tf_file: File {tf_file} generated successfully.")


# ? TD3 P2 Q2
def generate_idft_file(words_file: str, dfi_file: str) -> None:
    """Generate a docuement with the format "word \t idft"""
    file = pd.read_csv(words_file, sep="\t", header=None, names=["doc", "word"])
    unique_word_doc = file.drop_duplicates()
    unique_word_doc["dfi"] = unique_word_doc.groupby("word")["doc"].transform("count")
    unique_word_doc = unique_word_doc.drop(columns=["doc"]).drop_duplicates()
    N = file["doc"].nunique()
    unique_word_doc["dfi"] = np.log10(N / unique_word_doc["dfi"])  # calule de idft
    unique_word_doc.rename(columns={"dfi": "idft"}, inplace=True)

    with open(dfi_file, "w", encoding="utf-8") as f:
        for _, row in unique_word_doc.iterrows():
            f.write(f"{row['word']}\t{row['idft']}\n")
    print(f"generate_idft_file: File {dfi_file} generated successfully.")


# ? TD3 P2 Q3
def generate_tf_idft_file(tf_file: str, idft_file: str, tf_idft_file: str) -> None:
    """Generate a docuement with the format "document \t word \t tf*idft"""

    tf_df = pd.read_csv(tf_file, sep="\t", header=None, names=["Document", "Mot", "tf"])
    idft_df = pd.read_csv(idft_file, sep="\t", header=None, names=["Mot", "idft"])

    tf_idft_df = pd.merge(tf_df, idft_df, on="Mot").drop_duplicates()
    tf_idft_df["tf_idft"] = tf_idft_df["tf"] * tf_idft_df["idft"]
    tf_idft_df.sort_values(by=["Document", "tf_idft"], ascending=False, inplace=True)
    with open(tf_idft_file, "w", encoding="utf-8") as f:
        for _, row in tf_idft_df.iterrows():
            f.write(f"{row['Document']}\t{row['Mot']}\t{row['tf_idft']}\n")
    print(f"generate_tf_idft_file: File {tf_idft_file} generated successfully.")


# ? TD3 End Part
def filter_words_in_tf_idft(
    tf_idft_path: str, output_path: str, limit: float = 2
) -> None:
    """generate a file with the words that have a tf_idft > limit and save it in the output_path with the format document \t word \t tf_idft"""
    tf_idft_df = pd.read_csv(
        tf_idft_path, sep="\t", header=None, names=["Document", "Mot", "tf_idft"]
    )
    tf_idft_df = tf_idft_df[tf_idft_df["tf_idft"] > limit]
    tf_idft_df.to_csv(output_path, sep="\t", index=False, header=False)
    print(f"filter_words_in_tf_idft: File {output_path} generated successfully.")


# ? TD3 End Part
def transform_xml(xml_path: str, output_path: str, filtered_tf_idft_path: str) -> None:
    """Args :"
    xml_path : str -> path to the xml file (.xml)
    output_path : str -> path to the output xml file (.xml)
    filtered_tf_idft_path : str -> path to the filtered tf_idft file (.txt)
    """

    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()
    bulletins = root.findall("bulletin")
    # Read the filtered tf_idft file into a DataFrame
    filtered_tf_idft = pd.read_csv(
        filtered_tf_idft_path,
        sep="\t",
        header=None,
        names=["Document", "Mot", "tf_idft"],
    )

    filtered_tf_idft["Document"] = filtered_tf_idft["Document"].astype(str)

    for bulletin in bulletins:
        file_name = bulletin.find("fichier").text  # name of the file in the bulletin
        # Get all words selected for the given file
        filtered_words = filtered_tf_idft[filtered_tf_idft["Document"] == file_name][
            "Mot"
        ].tolist()  # all word selected for the given file
        #! modification de la gestion des titres avec tf-idf
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
        ]

        # Preprocess and split the text and title
        text = re.split(r"[ \-']", preprocess(bulletin.find("texte").text))
        title = re.split(r"[ \-']", preprocess(bulletin.find("titre").text))

        new_text = ""
        new_title = ""

        # Filter the text using the filtered words
        for word in text:
            if word in filtered_words:
                new_text += word + " "
        # for word in title:
        #     if word in filtered_words:
        #         new_title += word + " "

        # Filter the title by removing contractions
        for word in title:
            if word not in contractions_to_remove:
                new_title += word + " "

        # Create a dictionary for the article fields
        article_dict = {
            "fichier": file_name,
            "texte": new_text,
            "titre": new_title,
            "date": bulletin.find("date").text,
            "rubrique": bulletin.find("rubrique").text,
            "auteur": bulletin.find("auteur").text,
            "contact": bulletin.find("contact").text,
        }

        # Handle images if present
        img_dict = bulletin.find("images")
        if img_dict is not None:
            img_dict = {
                image.find("urlImage").text: image.find("legendeImage").text
                for image in img_dict
            }
        else:
            img_dict = {}

        # Add the article to the output XML using a function from TD2.py
        add_article_to_xml(
            output_path, article_dict, {}
        )  # fonction de TD2.py pour ajouter l'article dans le fichier XML
    print(f"transform_xml: File {output_path} generated successfully.")
