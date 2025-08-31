import os
from typing import Dict, List
from xml.dom import minidom
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from tqdm import tqdm


# ? TD2
def numero(html_doc: str):
    """Extract the bulletin number from the HTML file"""

    soup = BeautifulSoup(html_doc, "html.parser")
    for p in soup.find_all("title"):
        s = str(p)
        s2 = s.split(";")
        return s2[1][:-3]


# ? TD2
def date(html_doc: str) -> str:
    """Extract the date of the HTML opened file"""

    soup = BeautifulSoup(html_doc, "html.parser")
    for p in soup.find_all("title"):
        s = str(p)
        s2 = s.split(";")
        date = s2[0]
        t = date.split(">")
        t = t[1]
        t = t.split("&")
        date = t[0]
        liste_date = date.split("/")
        date = liste_date[2][:-1] + "/" + liste_date[1] + "/" + liste_date[0]
        return date


# ? TD2
def rubrique(html_doc: str):
    """Extract the rubrique from the HTML file"""

    try:
        soup = BeautifulSoup(html_doc, "html.parser")
        body = soup.body
        tableau = body.find_all("table")
        tr = tableau[1].find_all("tr")
        c = tr[2]
        content = c.find_all("td")[0].find("span", class_="style42")
        return str(content).split(">")[1][:-4]
    except Exception:
        return "None"


# ? TD2
def titre(html_doc: str) -> str:
    """This function takes a file name as input and returns the title of the HTML page
    The file must be opened in read mode"""

    soup = BeautifulSoup(html_doc, "html.parser")
    for p in soup.find_all("title"):
        s = str(p)

        s2 = s.split("&gt;")

        title = s2[-1]

        t = title.split("<")

        title = t[0]

        title = title.replace("&amp;", "&")
        return title


# ? TD2
def auteur(html_doc: str):
    """find the autor of the article"""

    soup = BeautifulSoup(html_doc, "html.parser")
    table = soup.find("table")
    tr_indice = 0
    for tr in table.find_all("tr"):
        p_indice = 0
        if tr_indice == 6:
            for p in tr.find_all("p"):
                if p_indice == 17:
                    s = str(p)
                    try:
                        s = s.split(">ADIT - ")[1].split(" - ")[0]
                    except Exception:
                        try:
                            s = s.split(">ADIT-")[1].split(" - ")[0]
                        except Exception:
                            return None
                p_indice += 1
        tr_indice += 1
    return s


# ? TD2
def texte(html_doc: str) -> str:
    """Extract the text from the HTML file"""

    soup = BeautifulSoup(html_doc, "html.parser")
    body = soup.body
    tableau = body.find_all("table")
    tr = tableau[1].find_all("tr")
    c = tr[2]
    content = c.find_all("td")[0]
    contenu = ""
    content = content.find_all("span", class_="style95")
    for element in content:
        contenu = contenu + str(element.get_text())
    return contenu


# ? TD2
def images(html_doc: str) -> Dict[str, str]:
    """Extract the images from the HTML file
    Return a dictionary with the URL as key and the legend as value"""

    soup = BeautifulSoup(html_doc, "html.parser")
    body = soup.body
    tableau = body.find_all("table")
    tr = tableau[1].find_all("tr")
    c = tr[2]
    content = c.find_all("td")[0]
    soup2 = BeautifulSoup(str(content), "html.parser")
    dictionnaire = {}
    for p in soup2.find_all("img"):
        legende = ""
        parent = p.find_parent("div", style="text-align: center")
        if parent.find("span", class_="style21"):
            legende = (
                str(parent.find("span", class_="style21"))
                .split("<strong>")[1]
                .split("<")[0]
            )

        s = str(p).split(" ")
        for element in s:
            if element.startswith("src="):
                e = element.split("=")
                url = e[1]
                dictionnaire[url[1:-1]] = legende
    return dictionnaire


# ? TD2
def contact(html_doc: str):
    """return all contact informations : mail, tel, adresse"""

    soup = BeautifulSoup(html_doc, "html.parser")
    body = soup.body
    tableau = body.find_all("table")
    tr = tableau[1].find_all("tr")
    trouve = 0
    for element in tr:
        if (
            str(element).startswith(
                '<tr>\n<td bgcolor="#6584a3" valign="top" width="148">'
            )
        ) and trouve == 0:
            c = element
            trouve = 1
    contact = c.find("span", class_="style85")
    infos_brutes = str(contact).split('<span class="style85">')[1].split("</span>")[0]
    soup2 = BeautifulSoup(infos_brutes, "html.parser")
    return soup2.get_text()


#! ------------------------------------------------------- #!
#! ------- stockage des données dans un fichier XML ------ #!
#! ------------------------------------------------------- #!

# format de stockage des données proposé :
# voir rapport

# ? TD2
def prettify_xml(elem: ET.Element) -> str:
    """Use this function before writing the XML file to make it more readable"""
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# ? TD2
def add_article_to_xml(
    save_path: str, article_dict: Dict[str, str], img_dict: Dict[str, str]
) -> None:
    """Add the article information to the XML file
    Args :
        - save_path : the path of the XML file
        - article_dict : a dictionary with the article information
        - img_dict : a dictionary with the images information"""

    try:
        tree = ET.parse(save_path)  # Try to open an existing XML file
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        # Create a new XML file if it doesn't exist or is invalid
        root = ET.Element("corpus")
        tree = ET.ElementTree(root)
        tree.write(save_path, encoding="utf-8", xml_declaration=True)

    article = ET.SubElement(root, "bulletin")  # Add a new bulletin node

    # Add article information as sub-elements
    for key, value in article_dict.items():
        element = ET.SubElement(article, key)
        element.text = value

    # Add images and their legends
    images = ET.SubElement(article, "images")
    for url, legende in img_dict.items():
        image = ET.SubElement(images, "image")
        url_element = ET.SubElement(image, "urlImage")
        url_element.text = url
        legende_element = ET.SubElement(image, "legendeImage")
        legende_element.text = legende

    tree.write(save_path, encoding="utf-8", xml_declaration=True)  # Save changes


# ? TD2
def process_all_files(dir_path: str, save_path: str) -> None:
    """For each file in the directory (dir_path), extract the information and save it in the XML file (save_path)"""

    for file in tqdm(
        sorted(os.listdir(dir_path)), desc="Processing files", unit="file"
    ):
        if file.endswith(".html") or file.endswith(".htm"):
            with open(os.path.join(dir_path, file), "r", encoding="utf-8") as fi:
                f = fi.read()
                article_dict = {
                    "fichier": file[:-4],
                    "numero": numero(f),
                    "date": date(f),
                    "rubrique": rubrique(f),
                    "titre": titre(f),
                    "auteur": auteur(f),
                    "texte": texte(f),
                    "contact": contact(f),
                }

                img_dict = images(f)
                add_article_to_xml(save_path, article_dict, img_dict)
            fi.close()
    print(f"process_all_files : All files processed and converted to XML {save_path}")
