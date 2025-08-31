# Projet LO17 - Moteur de Recherche

Ce projet a pour objectif d’explorer diverses techniques de recherche d’information en développant un moteur de recherche capable d’interroger une base d’articles scientifiques à partir de requêtes en langage naturel. 
Il s’inscrit dans le cadre de l’UV LO17 de l’Université de Technologie de Compiègne (UTC) et a été mené à travers six Travaux Dirigés distincts, de TD2 à TD7.


## Structure du projet

Le projet contients differents dossiers.

### Dossier `src/`  
Ce dossier contient l’ensemble des **fichiers sources** du projet, notamment :

- `main_demo.py` : (args:input_folder) **Script principal à exécuter en premier**. Il génère automatiquement les fichiers nécessaires au bon fonctionnement du moteur de recherche, qui sont ensuite stockés dans le dossier `data/`.
- `moteur.py` : Permet d’effectuer des recherches directement via la ligne de commande, sans passer par l’interface graphique. Toutefois, il est recommandé d’utiliser plutôt l’interface graphique prévue pour faciliter l’utilisation.
- `MainWindow.py` : Contient le code de l’interface utilisateur (UI) du moteur de recherche.
- `TD2.py` à `TD7.py` : Fichiers correspondant aux **Travaux Dirigés** des différentes séances, chacun regroupant le code spécifique à une étape d’apprentissage.
- `asset/` : Répertoire regroupant les ressources graphiques utilisées pour l’interface utilisateur (images, icônes, etc.).

### Dossier `data/`
Ce dossier contient les **fichiers générés automatiquement** à partir de l’exécution de `main_demo.py`. Ces fichiers sont indispensables au bon fonctionnement du moteur de recherche.

### Dossier `BULLETINS/`  
Ce dossier doit impérativement être ajouté à la racine du projet. Il n’est pas fourni avec le reste des fichiers en raison de son volume important.

### Dossier `Documents/`
Ce dossier contient tous les documents annexes au projet, notamment le **rapport de projet** au format PDF.  
Il inclut également un dossier `Illustrations` qui regroupe différentes figures utiles à la compréhension du projet, ainsi que les images présentes dans le rapport, mais en meilleure résolution.


## Environnement de travail

Le projet est compatible avec les systèmes d’exploitation Windows 10, Windows 11 et macOS.

Le projet a été développé et testé à 100% sous **Python 3.9.13**. Il est recommandé d’utiliser un environnement virtuel pour gérer les dépendances.

Voici la liste des principales bibliothèques Python utilisées dans ce projet&nbsp;:

| Bibliothèque         | Version   | Description                                      |
|----------------------|-----------|--------------------------------------------------|
| beautifulsoup4       | 4.11.1    | Analyse et extraction de données HTML/XML         |
| black                | 22.6.0    | Formatage automatique du code Python              |
| dateparser           | 1.2.1     | Analyse de dates en langage naturel               |
| datetime             | base      | Manipulation de dates et d'heures (standard)      |
| enum                 | base      | Types énumérés (standard)                         |
| functools            | base      | Outils pour fonctions (standard)                  |
| lxml                 | 4.9.1     | Traitement XML et HTML performant                 |
| nltk                 | 3.7       | Traitement du langage naturel                     |
| numpy                | 1.24.4    | Calcul scientifique et manipulation de tableaux   |
| os                   | base      | Fonctions système (standard)                      |
| pandas               | 1.4.4     | Analyse et manipulation de données                |
| platform             | 4.3.6     | Informations sur la plateforme                    |
| pyqt5                | 5.15.9    | Interface graphique en Python                     |
| pylint               | 2.14.5    | Analyse statique du code Python                   |
| regex                | 2022.7.9  | Expressions régulières avancées                   |
| snowballstemmer      | 2.2.0     | Stemming pour plusieurs langues                   |
| spacy                | 3.8.3     | Traitement avancé du langage naturel              |
| subprocess           | base      | Gestion des processus (standard)                  |
| sys                  | base      | Accès aux variables système (standard)            |
| time                 | base      | Gestion du temps (standard)                       |
| tqdm                 | 4.64.1    | Barres de progression                             |
| typing               | base      | Indications de types (standard)                   |

**IMPORTANT** : Les modèles spacy utilisés sont les modèle small et large nommé `fr_core_news_sm` et `fr_core_news_lg`, ils sont à installer en même temps de spacy pour une bonne utilisation du programme.
Utilisez les commandes : 
```bash
python -m spacy download fr_core_news_sm
``` 
et
```bash
python -m spacy download fr_core_news_lg
```

Les modules marqués comme **base** font partie de la bibliothèque standard de Python.


## Démarrage

> **IMPORTANT** : Toutes les fonctions doivent être lancées depuis le dossier `src` afin d’assurer le bon fonctionnement des chemins relatifs. (cd src)

Voici les différentes étapes à suivre pour un test complet du projet.
1. Cloner le repository dans le dossier de votre choix.
2. **IMPORTANT** : Ajouter à la racine du projet le dossier `BULLETINS` contenant les articles scientifiques au format ".htm".
3. Exécuter le fichier `_demo_.py` pour générer le dossier `data/` en renseignant pour l'argument `input_folder` le chemin fichier `BULLETINS` cible. Essayez par exemple la commande : `python main.py --input_folder BULLETINS_DEMO`
   *(Cette étape peut prendre quelques minutes.)*
4. Utiliser `moteur.py` pour saisir une requête et rechercher les articles correspondants.
5. Utiliser `MainWindow.py` pour lancer l’interface graphique et effectuer des recherches plus conviviales.


**Remarque :**
L’exécution de `main_demo.py` génère une copie du dossier `data/` appelée `data_test/`. Par la suite, le programme utilise le dossier `data/` pré-généré afin d’éviter d’éventuels bugs liés à la génération des données.  
Cela permet, en cas d’échec de la génération, d’utiliser malgré tout le moteur de recherche et l’interface graphique. Les dossiers `data/` et `data_test/` sont totalement identiques.

## En cas de problèmes

Tout le code s'execute normalement sans bugs. En cas de problèmes, n'hésitez pas à nous contacter aux adresses mails suivantes :
- colin.manyri@etu.utc.fr
- martin.valet@etu.utc.fr

## Auteurs
Ce projet a été réalisé par Martin VALET et Colin MANYRI. (50% - 50%)