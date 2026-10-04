import time

from settings import (
    MODE_JCJ,
    MODE_JCIA,
    NIVEAU_DEBUTANT,
    NIVEAU_INTERMEDIAIRE,
    NIVEAU_AVANCE,
    NIVEAU_EXPERT,
    MAX_TOURS
)

from player import (
    creer_plateau,
    afficher_plateau,
    coups_possibles,
    appliquer_coup,
    appliquer_neffakh,
    verifier_victoire,
    compter_pieces,
    compter_sultans,
    adversaire,
    coup_en_texte
)

from enemy import (
    choisir_coup_ia,
    choisir_capture_suivante_ia
)


#SAISIE UTILISATEUR


def lire_texte(message):
    try:
        return input(message)
    except EOFError:
        print()
        print("Entrée console fermée.")
        return None
    except KeyboardInterrupt:
        print()
        print("Partie interrompue par l'utilisateur.")
        return None


def lire_entier(message):
    while True:
        valeur = lire_texte(message)

        if valeur is None:
            return None

        try:
            return int(valeur)
        except ValueError:
            print("Veuillez entrer un nombre valide.")


def choisir_mode():
    while True:
        print("===================================")
        print("       JEU DE DAMES MAROCAIN       ")
        print("===================================")
        print("1 - Joueur contre Joueur")
        print("2 - Joueur contre Intelligence Artificielle")
        print()

        choix = lire_entier("Choisir le mode : ")

        if choix is None:
            return None

        if choix == 1:
            return MODE_JCJ

        if choix == 2:
            return MODE_JCIA

        print("Choix invalide. Veuillez choisir 1 ou 2.")


def choisir_niveau_ia():
    while True:
        print()
        print("=== Niveau de l'intelligence artificielle ===")
        print("1 - Débutant")
        print("2 - Intermédiaire")
        print("3 - Avancé")
        print("4 - Expert")
        print()

        choix = lire_entier("Choisir le niveau : ")

        if choix is None:
            return None

        if choix == NIVEAU_DEBUTANT:
            return NIVEAU_DEBUTANT

        if choix == NIVEAU_INTERMEDIAIRE:
            return NIVEAU_INTERMEDIAIRE

        if choix == NIVEAU_AVANCE:
            return NIVEAU_AVANCE

        if choix == NIVEAU_EXPERT:
            return NIVEAU_EXPERT

        print("Choix invalide. Veuillez choisir un niveau entre 1 et 4.")


def saisir_nom(message, nom_defaut):
    nom = lire_texte(message)

    if nom is None:
        return None

    if nom == "":
        return nom_defaut

    return nom


def choisir_joueurs(mode):
    nom_blanc = saisir_nom("Nom du joueur blanc : ", "Joueur Blanc")

    if nom_blanc is None:
        return None, None

    if mode == MODE_JCJ:
        nom_noir = saisir_nom("Nom du joueur noir : ", "Joueur Noir")

        if nom_noir is None:
            return None, None

    else:
        nom_noir = "Ordinateur"

    return nom_blanc, nom_noir


def nom_joueur(joueur, nom_blanc, nom_noir):
    if joueur == "blanc":
        return nom_blanc

    return nom_noir


# AFFICHAGE


def afficher_infos_partie(plateau, tour, joueur_courant, nom_blanc, nom_noir):
    print()
    print("===================================")
    print("Tour :", tour)
    print("Joueur courant :", nom_joueur(joueur_courant, nom_blanc, nom_noir), "-", joueur_courant)
    print("Pièces blanches :", compter_pieces(plateau, "blanc"))
    print("Pièces noires   :", compter_pieces(plateau, "noir"))
    print("Sultans blancs  :", compter_sultans(plateau, "blanc"))
    print("Sultans noirs   :", compter_sultans(plateau, "noir"))
    print("===================================")
    print()

    afficher_plateau(plateau)


def afficher_coups(coups, autoriser_neffakh):
    print()
    print("Coups possibles :")

    for i in range(len(coups)):
        print(i, "-", coup_en_texte(coups[i]))

    print()
    print("Entrez le numéro du coup.")
    print("Entrez A pour abandonner.")

    if autoriser_neffakh:
        print("Entrez N pour refuser la capture et appliquer le Neffakh.")

    print()


def afficher_resultat(
    gagnant,
    nom_blanc,
    nom_noir,
    captures_blanc,
    captures_noir,
    promotions_blanc,
    promotions_noir,
    historique,
    duree,
    statut_fin
):
    print()
    print("========== FIN DE PARTIE ==========")

    if statut_fin == "interrompue":
        print("Partie interrompue.")
    elif gagnant == "blanc":
        print("Gagnant :", nom_blanc, "(blanc)")
        print("Perdant :", nom_noir, "(noir)")
    elif gagnant == "noir":
        print("Gagnant :", nom_noir, "(noir)")
        print("Perdant :", nom_blanc, "(blanc)")
    else:
        print("Match nul.")

    print()
    print("Durée :", int(duree), "secondes")
    print("Captures blanches :", captures_blanc)
    print("Captures noires   :", captures_noir)
    print("Promotions blanches :", promotions_blanc)
    print("Promotions noires   :", promotions_noir)

    print()
    print("Historique des coups :")

    for i in range(len(historique)):
        print(i + 1, "-", historique[i])

    print("===================================")



# OUTILS DE COUPS


def liste_contient_capture(coups):
    for coup in coups:
        if coup[4] == "capture":
            return True

    return False


def choisir_coup_humain(coups, autoriser_neffakh):
    if len(coups) == 0:
        return None, "aucun"

    afficher_coups(coups, autoriser_neffakh)

    while True:
        choix = lire_texte("Votre choix : ")

        if choix is None:
            return None, "interruption"

        if choix == "A" or choix == "a":
            return None, "abandon"

        if autoriser_neffakh and (choix == "N" or choix == "n"):
            return None, "neffakh"

        try:
            indice = int(choix)

            if 0 <= indice < len(coups):
                return coups[indice], "ok"

            print("Numéro invalide.")

        except ValueError:
            print("Veuillez entrer un numéro valide.")


# TOUR HUMAIN

def jouer_tour_humain(plateau, joueur, historique, nom_blanc, nom_noir):
    captures_total = 0
    promotions_total = 0

    coups = coups_possibles(plateau, joueur)

    if len(coups) == 0:
        return captures_total, promotions_total, False, False

    autoriser_neffakh = liste_contient_capture(coups)

    coup, action = choisir_coup_humain(coups, autoriser_neffakh)

    if action == "interruption":
        return captures_total, promotions_total, False, True

    if action == "abandon":
        return captures_total, promotions_total, True, False

    if action == "neffakh":
        ok_neffakh = appliquer_neffakh(plateau, joueur)

        if ok_neffakh:
            historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " refuse une capture : Neffakh appliqué.")
        else:
            historique.append("Neffakh demandé mais aucune pièce n'a été retirée.")

        return captures_total, promotions_total, False, False

    ok, message, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
        plateau,
        coup,
        joueur
    )

    if not ok:
        print(message)
        return captures_total, promotions_total, False, False

    historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " : " + coup_en_texte(coup))

    if capture:
        captures_total += 1

    if promotion:
        promotions_total += 1

    while len(captures_suivantes) > 0:
        print()
        print("Capture multiple obligatoire avec la même pièce.")
        afficher_plateau(plateau)

        coup_suivant, action = choisir_coup_humain(captures_suivantes, True)

        if action == "interruption":
            return captures_total, promotions_total, False, True

        if action == "abandon":
            return captures_total, promotions_total, True, False

        if action == "neffakh":
            ok_neffakh = appliquer_neffakh(plateau, joueur, (ligne, colonne))

            if ok_neffakh:
                historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " refuse de continuer la capture : Neffakh appliqué.")
            else:
                historique.append("Neffakh demandé mais aucune pièce n'a été retirée.")

            break

        ok, message, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
            plateau,
            coup_suivant,
            joueur,
            (ligne, colonne)
        )

        if not ok:
            print(message)
            break

        historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " : " + coup_en_texte(coup_suivant))

        if capture:
            captures_total += 1

        if promotion:
            promotions_total += 1

    return captures_total, promotions_total, False, False


# ============================================================
# TOUR IA
# ============================================================

def jouer_tour_ia(plateau, joueur, niveau, historique, nom_blanc, nom_noir):
    captures_total = 0
    promotions_total = 0

    coup = choisir_coup_ia(plateau, joueur, niveau)

    if coup is None:
        return captures_total, promotions_total

    print()
    print("L'IA joue :", coup_en_texte(coup))

    ok, message, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
        plateau,
        coup,
        joueur
    )

    if not ok:
        print(message)
        return captures_total, promotions_total

    historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " : " + coup_en_texte(coup))

    if capture:
        captures_total += 1

    if promotion:
        promotions_total += 1

    while len(captures_suivantes) > 0:
        coup_suivant = choisir_capture_suivante_ia(
            plateau,
            joueur,
            captures_suivantes,
            niveau
        )

        if coup_suivant is None:
            break

        print("L'IA continue :", coup_en_texte(coup_suivant))

        ok, message, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
            plateau,
            coup_suivant,
            joueur,
            (ligne, colonne)
        )

        if not ok:
            print(message)
            break

        historique.append(nom_joueur(joueur, nom_blanc, nom_noir) + " : " + coup_en_texte(coup_suivant))

        if capture:
            captures_total += 1

        if promotion:
            promotions_total += 1

    return captures_total, promotions_total


# ============================================================
# BOUCLE PRINCIPALE (VERSION CONSOLE)
# ============================================================

def lancer_partie():
    mode = choisir_mode()

    if mode is None:
        print("Partie interrompue avant le début.")
        return

    niveau_ia = None

    if mode == MODE_JCIA:
        niveau_ia = choisir_niveau_ia()

        if niveau_ia is None:
            print("Partie interrompue avant le début.")
            return

    nom_blanc, nom_noir = choisir_joueurs(mode)

    if nom_blanc is None or nom_noir is None:
        print("Partie interrompue avant le début.")
        return

    plateau = creer_plateau()

    joueur_courant = "blanc"
    tour = 1

    captures_blanc = 0
    captures_noir = 0

    promotions_blanc = 0
    promotions_noir = 0

    historique = []

    gagnant = None
    statut_fin = "normale"

    debut = time.time()

    while tour <= MAX_TOURS:
        afficher_infos_partie(
            plateau,
            tour,
            joueur_courant,
            nom_blanc,
            nom_noir
        )

        gagnant = verifier_victoire(plateau, joueur_courant)

        if gagnant is not None:
            break

        abandon = False
        interruption = False

        if mode == MODE_JCIA and joueur_courant == "noir":
            captures, promotions = jouer_tour_ia(
                plateau,
                joueur_courant,
                niveau_ia,
                historique,
                nom_blanc,
                nom_noir
            )

        else:
            captures, promotions, abandon, interruption = jouer_tour_humain(
                plateau,
                joueur_courant,
                historique,
                nom_blanc,
                nom_noir
            )

        if interruption:
            statut_fin = "interrompue"
            break

        if abandon:
            gagnant = adversaire(joueur_courant)
            historique.append(nom_joueur(joueur_courant, nom_blanc, nom_noir) + " abandonne.")
            break

        if joueur_courant == "blanc":
            captures_blanc += captures
            promotions_blanc += promotions
        else:
            captures_noir += captures
            promotions_noir += promotions

        joueur_suivant = adversaire(joueur_courant)

        # Correction importante :
        # on vérifie la victoire après le coup, même si c'était le tour MAX_TOURS.
        gagnant = verifier_victoire(plateau, joueur_suivant)
        
        if gagnant is not None:
            break

        joueur_courant = joueur_suivant
        tour += 1

    if tour > MAX_TOURS and gagnant is None and statut_fin != "interrompue":
        statut_fin = "max_tours"

    fin = time.time()
    duree = fin - debut

    print()
    afficher_plateau(plateau)

    afficher_resultat(
        gagnant,
        nom_blanc,
        nom_noir,
        captures_blanc,
        captures_noir,
        promotions_blanc,
        promotions_noir,
        historique,
        duree,
        statut_fin
    )


# ============================================================
# POINT D'ENTRÉE - LANCE L'INTERFACE GRAPHIQUE PAR DÉFAUT
# ============================================================

if __name__ == "__main__":
    # Lancer l'interface graphique par défaut
    try:
        from interface import JeuDames
        print("🔄 Lancement de l'interface graphique...")
        jeu = JeuDames()
        jeu.run()
    except ImportError as e:
        print(f"⚠️ Interface graphique non disponible: {e}")
        print("🔄 Lancement en mode console...")
        lancer_partie()
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'interface: {e}")
        print("🔄 Lancement en mode console...")
        lancer_partie()