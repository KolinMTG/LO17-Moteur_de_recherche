# LO17 Project - Search Engine

This project aims to explore various information retrieval techniques by developing a search engine capable of querying a database of scientific articles using natural language queries.  
It is part of the LO17 course at the University of Technology of Compiègne (UTC) and was conducted through six separate practical sessions, from TD2 to TD7.

## Project Structure

The project contains several folders.

### `src/` Folder  
This folder contains all the **source files** of the project, including:

- `main_demo.py` (args: input_folder): **Main script to run first**. It automatically generates the files needed for the search engine to function properly, which are then stored in the `data/` folder.
- `moteur.py`: Allows performing searches directly via the command line without using the graphical interface. However, it is recommended to use the graphical interface for ease of use.
- `MainWindow.py`: Contains the code for the search engine's user interface (UI).
- `TD2.py` to `TD7.py`: Files corresponding to the **practical sessions**, each containing the code specific to a particular learning stage.
- `asset/`: Directory containing graphical resources used for the user interface (images, icons, etc.).

### `data/` Folder
This folder contains the **files automatically generated** by running `main_demo.py`. These files are essential for the proper functioning of the search engine.

### `BULLETINS/` Folder  
This folder must be added at the root of the project. It is not provided with the rest of the files due to its large size.

### `Documents/` Folder
This folder contains all additional project documents, including the **project report** in PDF format.  
It also includes an `Illustrations` folder that contains various figures useful for understanding the project, as well as images included in the report but in higher resolution.

## Working Environment

The project is compatible with Windows 10, Windows 11, and macOS.

The project was developed and fully tested with **Python 3.9.13**. It is recommended to use a virtual environment to manage dependencies.

Here is a list of the main Python libraries used in this project:

| Library             | Version   | Description                                      |
|---------------------|-----------|--------------------------------------------------|
| beautifulsoup4      | 4.11.1    | Parsing and extracting HTML/XML data            |
| black               | 22.6.0    | Automatic Python code formatting                |
| dateparser          | 1.2.1     | Parsing dates in natural language               |
| datetime            | base      | Date and time manipulation (standard library)  |
| enum                | base      | Enumerated types (standard library)            |
| functools           | base      | Function utilities (standard library)          |
| lxml                | 4.9.1     | Efficient XML and HTML processing               |
| nltk                | 3.7       | Natural language processing                     |
| numpy               | 1.24.4    | Scientific computing and array manipulation    |
| os                  | base      | Operating system functions (standard library)  |
| pandas              | 1.4.4     | Data analysis and manipulation                  |
| platform            | 4.3.6     | Platform information                             |
| pyqt5               | 5.15.9    | Python graphical user interface                 |
| pylint              | 2.14.5    | Python static code analysis                      |
| regex               | 2022.7.9  | Advanced regular expressions                     |
| snowballstemmer     | 2.2.0     | Stemming for multiple languages                  |
| spacy               | 3.8.3     | Advanced natural language processing             |
| subprocess          | base      | Process management (standard library)           |
| sys                 | base      | Access to system variables (standard library)   |
| time                | base      | Time management (standard library)              |
| tqdm                | 4.64.1    | Progress bars                                   |
| typing              | base      | Type hints (standard library)                   |

**IMPORTANT**: The SpaCy models used are the small and large French models named `fr_core_news_sm` and `fr_core_news_lg`. They must be installed together with SpaCy for proper program functionality.  
Use the following commands:  
```bash
python -m spacy download fr_core_news_sm
python -m spacy download fr_core_news_lg
```

## Getting Started

> **IMPORTANT**: All functions must be run from the `src` folder to ensure proper handling of relative paths.

Follow these steps for a complete test of the project:  
1. Clone the repository into the folder of your choice (if needed).  
2. **IMPORTANT**: Add the `BULLETINS` folder containing the scientific articles in ".htm" format to the project root.  
3. Run the `_demo_.py` file to generate the `data/` folder, specifying the `input_folder` argument with the target `BULLETINS` path. For example, try the command:  
   `python main.py --input_folder BULLETINS_DEMO`  
   *(This step may take a few minutes.)*  
4. Use `moteur.py` to enter a query and search for the corresponding articles.  
5. Use `MainWindow.py` to launch the graphical interface and perform searches in a more user-friendly way.  

**Note:**  
Running `main_demo.py` generates a copy of the `data/` folder called `data_test/`. Afterwards, the program uses the pre-generated `data/` folder to avoid potential bugs related to data generation.  
This ensures that, in case of a generation failure, the search engine and graphical interface can still be used. The `data/` and `data_test/` folders are completely identical.

## Troubleshooting

All code normally runs without bugs. If you encounter issues, feel free to contact us at the following email addresses:  
- colin.manyri@etu.utc.fr  
- martin.valet@etu.utc.fr

## Authors
This project was carried out by Martin VALET and Colin MANYRI. (50% - 50%)

