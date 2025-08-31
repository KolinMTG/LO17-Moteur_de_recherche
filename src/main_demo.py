from TD7 import *
import os
import sys
#! CONSTANTS PATHS

if len(sys.argv) > 1:
    input_folder = sys.argv[1]
else:
    input_folder = "BULLETINS"

base_dir = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.join(base_dir, "..", input_folder)
data_path = "data_test"

if not os.path.exists(dir_path):
    print(f"Error: The input folder '{dir_path}' does not exist.")
    sys.exit(1)

if not os.path.exists(os.path.join(base_dir, "..", data_path)):
    os.makedirs(os.path.join(base_dir, "..", data_path))

save_path = os.path.join(base_dir, "..", data_path, "corpus_base.xml")
corpus_base_path = os.path.join(base_dir, "..", data_path, "corpus_base.xml")
segment_path = os.path.join(base_dir, "..", data_path, "segment.txt")
tf_path = os.path.join(base_dir, "..", data_path, "tf.txt")
idft_path = os.path.join(base_dir, "..", data_path, "idft.txt")
tf_idft_path = os.path.join(base_dir, "..", data_path, "tf_idft.txt")
tf_idft_filtered_path = os.path.join(base_dir, "..", data_path, "tf_idft_filtered.txt")
corpus_filtered_path = os.path.join(base_dir, "..", data_path, "corpus_filtered.xml")
lemme_nltk_path = os.path.join(base_dir, "..", data_path, "lemme_nltk.txt")
lemme_spacy_path = os.path.join(base_dir, "..", data_path, "lemme_spacy.txt")
corpus_stem_path = os.path.join(base_dir, "..", data_path, "corpus_stem.xml")
lexique_path = os.path.join(base_dir, "..", data_path, "lexique.txt")
lexique_folder_path = os.path.join(base_dir, "..", data_path, "fichiers_inverse")
pertinence_file_path = os.path.join(base_dir, "..", data_path, "fichier_pertinence.txt")


def generate_TD2_file():
    """génère toutes les fichier de data du TD2"""
    print("Generating TD2 files... This may take a while. Please wait.")
    process_all_files(dir_path, save_path)
    print("TD2 files generated successfully.")


def generate_TD3_file():
    """génère toutes les fichier de data du TD2"""
    seuil = 2

    # exectute the functions
    segment(corpus_base_path, segment_path)
    generate_tf_file(segment_path, tf_path)
    generate_idft_file(segment_path, idft_path)
    generate_tf_idft_file(tf_path, idft_path, tf_idft_path)
    filter_words_in_tf_idft(tf_idft_path, tf_idft_filtered_path, limit=seuil)
    transform_xml(corpus_base_path, corpus_filtered_path, tf_idft_filtered_path)


def generate_TD4_file():
    """génère toutes les fichier de data du TD2"""
    generate_nltk(corpus_filtered_path, lemme_nltk_path)
    generate_lemme_with_spacy(corpus_filtered_path, lemme_spacy_path)
    generate_stem_corpus(
        corpus_filtered_path, corpus_stem_path, lemme_spacy_path
    )  #!génération avec spacy


def generate_TD5_file():
    """génère toutes les fichier de data du TD2"""
    convert_lemmes_to_lexique(lemme_spacy_path, lexique_path)


def generate_TD6_file():
    """génère toutes les fichier de data du TD2"""
    pass


def generate_TD7_file():
    """génère toutes les fichier de data du TD2"""
    generate_all_fichier_inverse(corpus_stem_path, lexique_folder_path)
    generer_fichier_inverse_common(lexique_folder_path)
    generer_fichier_pertinence(corpus_stem_path, pertinence_file_path)


if __name__ == "__main__":
    generate_TD2_file()
    print("TD2 files generated successfully. File : 1/6")
    generate_TD3_file()
    print("TD3 files generated successfully. File : 2/6")
    generate_TD4_file()
    print("TD4 files generated successfully. File : 3/6")
    generate_TD5_file()
    print("TD5 files generated successfully. File : 4/6")
    generate_TD6_file()
    print("TD6 files generated successfully. File : 5/6")
    generate_TD7_file()
    print("TD7 files generated successfully. File : 6/6")
    print("------------------------------------------------")
    print("All files generated successfully.")
    print("------------------------------------------------")
