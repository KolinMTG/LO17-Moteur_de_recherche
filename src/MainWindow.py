import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QScrollArea,
    QShortcut,
    QFrame,
    QMessageBox,
    QComboBox,
)
from PyQt5.QtGui import QKeySequence, QIcon, QMovie
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QSize
from enum import Enum
import os
import platform
import subprocess
import re
from typing import Dict
from datetime import datetime
import time

from TD2 import *
from TD7 import *


class SortBy(Enum):
    """Enum pour les critères de tri des résultats."""

    RELEVANCE = 1
    DATE_ASC = 2
    DATE_DESC = 3

    def __str__(self):
        return self.name.replace("_", " ").title()


class SearchWorker(QObject):
    finished = pyqtSignal(dict, object, dict)  # articles, objet_request, date_articles
    error = pyqtSignal(str)

    def __init__(self, request):
        super().__init__()
        self.request = request

    def run(self):
        try:
            start_time = time.time()
            articles, objet_request = treat_request(self.request)
            date_articles = self.get_date_for_articles(articles)
            elapsed_time = time.time() - start_time

            self.finished.emit(articles, objet_request, date_articles)
        except Exception as e:
            self.error.emit(str(e))

    def get_date_for_articles(self, articles: Dict[str, int]) -> Dict[str, str]:
        """Fonction qui renvoie un dictionnaire de chemins d'articles et leurs dates."""
        date_articles = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for article_name in articles.keys():
            article_path = os.path.join(
                base_dir, "..", "BULLETINS", f"{article_name}.htm"
            )
            with open(article_path, "r", encoding="utf-8") as fi:
                f = fi.read()
                date_articles[article_name] = date(f)
        return date_articles


class ResearchLine(QWidget):
    """Element composé d'un TextEdit et d'un bouton permetant de lancer la recherche."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Créer un bouton pour lancer la recherche
        self.search_button = QPushButton("Lancer la recherche", self)
        self.search_button.clicked.connect(parent.launch_search)

        # shortcut pour le bouton
        self.shortcut = QShortcut(QKeySequence("Return"), self)
        self.shortcut.activated.connect(parent.launch_search)

        # Créer un champ de texte pour la recherche
        self.search_text = QLineEdit(self)
        self.search_text.setPlaceholderText("Entrez votre recherche ici...")

        # Créer un layout vertical
        layout = QHBoxLayout()
        layout.addWidget(self.search_text)
        layout.addWidget(self.search_button)

        # Appliquer le layout au widget
        self.setLayout(layout)


class DocDisplay(QWidget):
    """Classe qui affiche un article avec son nom, titre, date et texte."""

    def __init__(
        self,
        file_path: str = "",
        article_name: str = "",
        title: str = "",
        rubrique: str = "",
        date: str = "",
        text: str = "",
        relevance_score: float = 0.0,
        words_to_highlight: list[str] = [],
    ):
        super().__init__()

        self.file_path = file_path

        # ---------- Ligne du haut ----------
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.setCursor(Qt.PointingHandCursor)

        name_label = QLabel(f"<b>{article_name}</b>")
        title_label = QLabel(f"<b>[{rubrique}] - {title}</b>")
        date_label = QLabel(f"<i>{date}</i>")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_layout.addWidget(name_label)
        top_layout.addWidget(title_label)
        top_layout.addWidget(date_label)

        # ---------- Ligne du milieu ----------
        text_label = QLabel()
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # ---------- Ligne du bas ----------
        relevance_label = QLabel(f"Score: {relevance_score:.2f}")
        relevance_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Ajout des mots du titre à ceux à mettre en gras
        highlight_words = set(words_to_highlight)
        highlight_words.update(self.tokenize(title))

        # Appliquer le highlighting
        highlighted_text = self.highlight_text(text, highlight_words)
        text_label.setText(highlighted_text)

        # ---------- Layout final ----------
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(relevance_label)
        layout.addWidget(text_label)
        layout.setSpacing(5)
        self.setLayout(layout)

    def tokenize(self, text: str) -> list[str]:
        """Découpe un texte en mots alphanumériques (minuscules)."""
        return re.findall(r"\b\w+\b", text.lower())

    def highlight_text(self, text: str, words_to_highlight: set[str]) -> str:
        """Met en gras les mots présents dans words_to_highlight."""

        def replacer(match):
            word = match.group(0)
            if word.lower() in words_to_highlight:
                return f"<b>{word}</b>"
            return word

        return re.sub(r"\b\w+\b", replacer, text)

    def open_file(self, path: str) -> None:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_file(self.file_path)


# Classe ResultDisplay qui contient une scroll area
class ResultDisplay(QWidget):
    """Classe qui affiche les résultats de la recherche dans une scroll area."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résultats")
        self.setMinimumSize(1180, 720)

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

    def add_doc(self, doc: QWidget):
        """Ajoute un DocDisplay dans sont Area avec ligne séparatrice."""
        self.content_layout.addWidget(doc)

        # Ligne séparatrice
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.content_layout.addWidget(separator)

    def clear_docs(self):
        """Supprime tous les widgets affichés (DocDisplay + lignes)."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application,
    composé d'une barre de recherche, d'un bouton et d'une zone de résultats (class ResultDisplay)."""

    def __init__(self):
        super().__init__()

        # Initialiser les attributs
        self.articles: Dict[
            str, int
        ] = {}  #! dictionnaire de chemins d'articles et leurs score de pertinence
        self.date_articles: Dict[
            str, str
        ] = {}  #! dictionnaire de chemins d'articles et leurs dates

        # Initialiser la fenêtre principale
        self.setWindowTitle("Moteur de recherche LO17")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon(r"asset/logo_utc.jpg"))

        # Initialiser l'UI
        self.init_ui()

    def init_ui(self):
        # Créer un widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Créer un layout vertical
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # ajouter le ResearchLine
        self.research_line = ResearchLine(self)

        layout_H1 = QHBoxLayout()
        layout_H1.addWidget(self.research_line)

        # ajouter un QMovie pour l'animation de chargement
        # Création du QLabel pour le spinner
        self.spinner_label = QLabel(self)

        # Charger le gif animé
        self.spinner_movie = QMovie(
            r"asset/loading.gif"
        )  # Assure-toi que le chemin est correct
        self.spinner_movie.setScaledSize(QSize(32, 32))
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.hide()  # Cacher par défaut

        layout_H1.addWidget(self.spinner_label)

        layout_H = QHBoxLayout()
        # ajout d'un label pour le temps de reponse
        self.response_info_label = QLabel("")
        self.response_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # ajout d'un element de séléction pour tri des résultats
        self.sort_label = QLabel("Trier par:")
        self.sort_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sort_combo_box = QComboBox()
        self.sort_combo_box.addItems([sort_by.name for sort_by in SortBy])
        self.sort_combo_box.currentTextChanged.connect(self.display_results)
        self.sort_combo_box.setCurrentIndex(0)

        layout_H.addWidget(self.sort_label)
        layout_H.addWidget(self.sort_combo_box)
        layout_H.addStretch()
        layout_H.addWidget(self.response_info_label)

        layout.addLayout(layout_H1)
        layout.addLayout(layout_H)

        # ajout de la zone de résultats
        self.result_display = ResultDisplay()
        layout.addWidget(self.result_display)

    def launch_search(self):
        request = self.research_line.search_text.text()
        if not request:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une recherche.")
            return

        self.spinner_label.show()
        self.spinner_movie.start()

        # Créer le thread et le worker
        self.thread = QThread()
        self.worker = SearchWorker(request)
        self.worker.moveToThread(self.thread)

        # Connexions signal-slot
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_search_finished(self, articles, objet_request, date_articles):
        # Stopper l'indicateur de chargement
        self.spinner_movie.stop()
        self.spinner_label.hide()

        self.articles = articles
        self.date_articles = date_articles

        # Choix du tri
        if objet_request.date_debut and not objet_request.date_fin:
            self.sort_combo_box.setCurrentText(SortBy.DATE_ASC.name)
        else:
            self.sort_combo_box.setCurrentText(SortBy.RELEVANCE.name)

        self.display_results()
        self.response_info_label.setText(f"<b>{len(articles)}</b> résultats trouvés.")

    def on_search_error(self, error_msg):
        # Stopper l'indicateur de chargement
        self.spinner_movie.stop()
        self.spinner_label.hide()
        QMessageBox.critical(self, "Oups !", f"Une erreur s'est produite : {error_msg}")
        self.response_info_label.setText("Erreur lors de la recherche.")

    def display_results(self):
        if self.articles == {}:
            self.result_display.clear_docs()
            QMessageBox.information(self, "Aucun résultat", "Aucun résultat trouvé.")
            return
        else:
            self.result_display.clear_docs()
            if self.sort_combo_box.currentText() == SortBy.DATE_ASC.name:
                for article_name, _ in sorted(
                    self.date_articles.items(),
                    key=lambda item: datetime.strptime(item[1], "%d/%m/%Y"),
                ):
                    # Créer un DocDisplay avec des données fictives

                    doc = self.article_name_to_docdisplay(
                        article_name
                    )  #! fonction à DEFINIR, renvoie un DocDisplay avec les données de l'article
                    # Ajouter le DocDisplay à la zone de résultats
                    self.result_display.add_doc(doc)
            elif self.sort_combo_box.currentText() == SortBy.DATE_DESC.name:
                for article_name, _ in sorted(
                    self.date_articles.items(),
                    key=lambda item: datetime.strptime(item[1], "%d/%m/%Y"),
                    reverse=True,
                ):
                    # Créer un DocDisplay avec des données fictives
                    doc = self.article_name_to_docdisplay(article_name)
                    # Ajouter le DocDisplay à la zone de résultats
                    self.result_display.add_doc(doc)

            elif self.sort_combo_box.currentText() == SortBy.RELEVANCE.name:
                # Trier par pertinence (exemple fictif)
                for article_name, relevance_score in sorted(
                    self.articles.items(), key=lambda item: item[1], reverse=True
                ):
                    # Créer un DocDisplay avec des données fictives
                    doc = self.article_name_to_docdisplay(
                        article_name, relevance_score * 100
                    )
                    # Ajouter le DocDisplay à la zone de résultats
                    self.result_display.add_doc(doc)

    def article_name_to_docdisplay(
        self, article_name: str, relevance_score: float = 0.0, limit_caracters=400
    ) -> DocDisplay:
        """Fonction qui renvoie un DocDisplay avec les données un numéro d'article."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "BULLETINS", f"{article_name}.htm")

        with open(file_path, "r", encoding="utf-8") as fi:
            f = fi.read()

        return DocDisplay(
            file_path=file_path,
            article_name=article_name,
            title=titre(f),
            rubrique=rubrique(f),
            date=date(f),
            text=texte(f)[:limit_caracters] + "..."
            if len(texte(f)) > limit_caracters
            else texte(f),
            relevance_score=relevance_score,
            words_to_highlight=[],  #! liste de mots à mettre en gras
        )


# Point d'entrée du programme
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(r"asset/logo_utc.jpg"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # base_dir = os.path.join("..", os.path.dirname(os.path.abspath(__file__)))
    # print("BASE DIR --------------------------------------")
    # print(base_dir)
