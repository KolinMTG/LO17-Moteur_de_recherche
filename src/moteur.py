"""Document permetant de donner des requetes en ligne de commande pour le moteur de recherche
Nous conseillons plustôt d'utiliser l'inferface graphique prévue à cet effet."""

from TD7 import treat_request


def moteur():
    print("=== Moteur de recherche ===")

    print(
        r""".____    ________  _____________               _____          __                       
|    |   \_____  \/_   \______  \             /     \   _____/  |_  ____  __ _________ 
|    |    /   |   \|   |   /    /   ______   /  \ /  \ /  _ \   __\/ __ \|  |  \_  __ \
|    |___/    |    \   |  /    /   /_____/  /    Y    (  <_> )  | \  ___/|  |  /|  | \/
|_______ \_______  /___| /____/             \____|__  /\____/|__|  \___  >____/ |__|   
        \/       \/                                 \/                 \/              """
    )

    print("Tapez votre requête ou 'q' pour quitter.\n")

    while True:
        request = input("Entrez votre requête de recherche : ").strip()

        if request.lower() == "q":
            print("Fermeture du moteur. Au revoir.")
            break

        if not request:
            print("Requête vide. Veuillez réessayer.")
            continue

        confirmation = (
            input(f"Confirmez-vous cette requête ? (o/n) : '{request}' ")
            .strip()
            .lower()
        )

        if confirmation in ("o", "oui", "y", "yes"):
            result, _ = treat_request(request)
            print("\nRésultats de la recherche :")
            if not result:
                print("Aucun résultat trouvé.")
                continue
            else:
                for article, pertinence in sorted(
                    result.items(), key=lambda x: x[1], reverse=True
                ):
                    print(
                        f"Article : {article}, Pertinence : {round(pertinence, 3)*100}"
                    )

            print("Requête traitée avec succès.")
            print("----------------------------------------")
        elif confirmation in ("n", "non"):
            print("Requête annulée. Vous pouvez en saisir une nouvelle.")
        else:
            print("Réponse non reconnue. Merci de répondre par 'o' ou 'n'.")


if __name__ == "__main__":
    moteur()
