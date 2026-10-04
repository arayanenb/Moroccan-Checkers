from settings import BOARD_SIZE, VIDE, PB, PN, SB, SN


# ============================================================
# OUTILS DE BASE
# ============================================================

def est_dans_plateau(ligne, colonne):
    return 0 <= ligne < BOARD_SIZE and 0 <= colonne < BOARD_SIZE


def case_foncee(ligne, colonne):
    return (ligne + colonne) % 2 == 1


def couleur_piece(piece):
    if piece == PB or piece == SB:
        return "blanc"

    if piece == PN or piece == SN:
        return "noir"

    return ""


def est_sultan(piece):
    return piece == SB or piece == SN


def piece_du_joueur(piece, joueur):
    return couleur_piece(piece) == joueur


def piece_adverse(piece, joueur):
    return piece != VIDE and couleur_piece(piece) != joueur


def adversaire(joueur):
    if joueur == "blanc":
        return "noir"

    return "blanc"


def creer_coup(ld, cd, la, ca, type_coup, ligne_capture, colonne_capture):
    return (ld, cd, la, ca, type_coup, ligne_capture, colonne_capture)


def meme_coup(coup1, coup2):
    return (
        coup1[0] == coup2[0] and
        coup1[1] == coup2[1] and
        coup1[2] == coup2[2] and
        coup1[3] == coup2[3] and
        coup1[4] == coup2[4] and
        coup1[5] == coup2[5] and
        coup1[6] == coup2[6]
    )


# ============================================================
# CREATION ET AFFICHAGE DU PLATEAU
# ============================================================

def creer_plateau():
    plateau = []

    for i in range(BOARD_SIZE):
        ligne = []

        for j in range(BOARD_SIZE):
            ligne.append(VIDE)

        plateau.append(ligne)

    # Noirs : 3 premières lignes, 4 pions par ligne = 12 pions
    # Centrés sur le plateau : on prend les colonnes 1,3,5,7 (pour les lignes paires)
    # et 0,2,4,6 (pour les lignes impaires)
    for i in range(3):
        if i % 2 == 0:  # Lignes paires (0, 2)
            colonnes = [1, 3, 5, 7]
        else:           # Lignes impaires (1)
            colonnes = [0, 2, 4, 6]
        
        for j in colonnes:
            plateau[i][j] = PN

    # Blancs : 3 dernières lignes, 4 pions par ligne = 12 pions
    # Symétrique des noirs
    for i in range(BOARD_SIZE - 3, BOARD_SIZE):
        if i % 2 == 0:  # Lignes paires (8)
            colonnes = [1, 3, 5, 7]
        else:           # Lignes impaires (7, 9)
            colonnes = [0, 2, 4, 6]
        
        for j in colonnes:
            plateau[i][j] = PB

    return plateau


def afficher_plateau(plateau):
    print("    ", end="")

    for j in range(BOARD_SIZE):
        print(j, end="   ")

    print()

    for i in range(BOARD_SIZE):
        print(i, " ", end="")

        for j in range(BOARD_SIZE):
            if plateau[i][j] == VIDE:
                print(".", end="   ")
            else:
                print(plateau[i][j], end="  ")

        print()


def copier_plateau(plateau):
    nouveau = []

    for i in range(BOARD_SIZE):
        ligne = []

        for j in range(BOARD_SIZE):
            ligne.append(plateau[i][j])

        nouveau.append(ligne)

    return nouveau


# ============================================================
# DEPLACEMENTS SIMPLES
# ============================================================

def chemin_libre(plateau, ld, cd, la, ca):
    if not est_dans_plateau(ld, cd):
        return False

    if not est_dans_plateau(la, ca):
        return False

    dl = la - ld
    dc = ca - cd

    if abs(dl) != abs(dc):
        return False

    if dl == 0:
        return False

    if dl > 0:
        pas_ligne = 1
    else:
        pas_ligne = -1

    if dc > 0:
        pas_colonne = 1
    else:
        pas_colonne = -1

    i = ld + pas_ligne
    j = cd + pas_colonne

    while i != la and j != ca:
        if plateau[i][j] != VIDE:
            return False

        i += pas_ligne
        j += pas_colonne

    return True


def mouvement_valide(plateau, ld, cd, la, ca, joueur):
    if not est_dans_plateau(ld, cd):
        return False

    if not est_dans_plateau(la, ca):
        return False

    piece = plateau[ld][cd]

    if not piece_du_joueur(piece, joueur):
        return False

    if plateau[la][ca] != VIDE:
        return False

    # Règle du Koul :
    # si une capture existe, le déplacement simple est interdit.
    if existe_capture(plateau, joueur):
        return False

    dl = la - ld
    dc = ca - cd

    if not est_sultan(piece):
        if abs(dc) != 1:
            return False

        if joueur == "blanc" and dl == -1:
            return True

        if joueur == "noir" and dl == 1:
            return True

        return False

    # Sultan : déplacement libre en diagonale
    if abs(dl) != abs(dc):
        return False

    return chemin_libre(plateau, ld, cd, la, ca)


# ============================================================
# CAPTURES
# ============================================================

def captures_piece(plateau, ligne, colonne, joueur):
    captures = []

    if not est_dans_plateau(ligne, colonne):
        return captures

    piece = plateau[ligne][colonne]

    if not piece_du_joueur(piece, joueur):
        return captures

    directions = [
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1)
    ]

    # Capture d'un pion normal
    if not est_sultan(piece):
        for dl, dc in directions:
            ligne_capture = ligne + dl
            colonne_capture = colonne + dc

            ligne_arrivee = ligne + 2 * dl
            colonne_arrivee = colonne + 2 * dc

            if est_dans_plateau(ligne_capture, colonne_capture) and est_dans_plateau(ligne_arrivee, colonne_arrivee):
                if piece_adverse(plateau[ligne_capture][colonne_capture], joueur):
                    if plateau[ligne_arrivee][colonne_arrivee] == VIDE:
                        coup = creer_coup(
                            ligne,
                            colonne,
                            ligne_arrivee,
                            colonne_arrivee,
                            "capture",
                            ligne_capture,
                            colonne_capture
                        )

                        captures.append(coup)

    # Capture d'un Sultan
    else:
        for dl, dc in directions:
            i = ligne + dl
            j = colonne + dc

            piece_trouvee = False
            ligne_capture = -1
            colonne_capture = -1

            while est_dans_plateau(i, j):
                case = plateau[i][j]

                if case == VIDE and not piece_trouvee:
                    i += dl
                    j += dc

                elif piece_du_joueur(case, joueur):
                    break

                elif piece_adverse(case, joueur) and not piece_trouvee:
                    piece_trouvee = True
                    ligne_capture = i
                    colonne_capture = j

                    i += dl
                    j += dc

                elif case == VIDE and piece_trouvee:
                    coup = creer_coup(
                        ligne,
                        colonne,
                        i,
                        j,
                        "capture",
                        ligne_capture,
                        colonne_capture
                    )

                    captures.append(coup)

                    i += dl
                    j += dc

                else:
                    break

    return captures


def existe_capture(plateau, joueur):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if piece_du_joueur(plateau[i][j], joueur):
                captures = captures_piece(plateau, i, j, joueur)

                if len(captures) > 0:
                    return True

    return False


def pieces_avec_capture(plateau, joueur):
    pieces = []

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if piece_du_joueur(plateau[i][j], joueur):
                captures = captures_piece(plateau, i, j, joueur)

                if len(captures) > 0:
                    pieces.append((i, j))

    return pieces


def capture_valide(plateau, ld, cd, la, ca, joueur):
    captures = captures_piece(plateau, ld, cd, joueur)

    for coup in captures:
        if coup[2] == la and coup[3] == ca:
            return True

    return False


def doit_continuer_capture(plateau, ligne, colonne, joueur):
    captures = captures_piece(plateau, ligne, colonne, joueur)

    if len(captures) > 0:
        return True

    return False


def captures_obligatoires_apres_coup(plateau, ligne, colonne, joueur):
    return captures_piece(plateau, ligne, colonne, joueur)


# ============================================================
# COUPS POSSIBLES
# ============================================================

def coups_possibles(plateau, joueur):
    coups = []
    captures = []

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if piece_du_joueur(piece, joueur):
                captures_piece_actuelle = captures_piece(plateau, i, j, joueur)

                for coup in captures_piece_actuelle:
                    captures.append(coup)

    # Règle du Koul :
    # si une capture existe, le joueur doit capturer.
    if len(captures) > 0:
        return captures

    directions_pion = []

    if joueur == "blanc":
        directions_pion = [(-1, -1), (-1, 1)]
    else:
        directions_pion = [(1, -1), (1, 1)]

    directions_sultan = [
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1)
    ]

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if not piece_du_joueur(piece, joueur):
                continue

            if not est_sultan(piece):
                for dl, dc in directions_pion:
                    la = i + dl
                    ca = j + dc

                    if mouvement_valide(plateau, i, j, la, ca, joueur):
                        coup = creer_coup(
                            i,
                            j,
                            la,
                            ca,
                            "deplacement",
                            -1,
                            -1
                        )

                        coups.append(coup)

            else:
                for dl, dc in directions_sultan:
                    la = i + dl
                    ca = j + dc

                    while est_dans_plateau(la, ca) and plateau[la][ca] == VIDE:
                        coup = creer_coup(
                            i,
                            j,
                            la,
                            ca,
                            "deplacement",
                            -1,
                            -1
                        )

                        coups.append(coup)

                        la += dl
                        ca += dc

    return coups


def coups_possibles_piece(plateau, ligne, colonne, joueur):
    coups = []

    if not est_dans_plateau(ligne, colonne):
        return coups

    piece = plateau[ligne][colonne]

    if not piece_du_joueur(piece, joueur):
        return coups

    captures = captures_piece(plateau, ligne, colonne, joueur)

    if len(captures) > 0:
        return captures

    # Si une autre pièce du joueur peut capturer,
    # cette pièce n'a pas le droit de faire un déplacement simple.
    if existe_capture(plateau, joueur):
        return coups

    directions = []

    if est_sultan(piece):
        directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1)
        ]

        for dl, dc in directions:
            la = ligne + dl
            ca = colonne + dc

            while est_dans_plateau(la, ca) and plateau[la][ca] == VIDE:
                coup = creer_coup(
                    ligne,
                    colonne,
                    la,
                    ca,
                    "deplacement",
                    -1,
                    -1
                )

                coups.append(coup)

                la += dl
                ca += dc

    else:
        if joueur == "blanc":
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        for dl, dc in directions:
            la = ligne + dl
            ca = colonne + dc

            if mouvement_valide(plateau, ligne, colonne, la, ca, joueur):
                coup = creer_coup(
                    ligne,
                    colonne,
                    la,
                    ca,
                    "deplacement",
                    -1,
                    -1
                )

                coups.append(coup)

    return coups


def trouver_coup(plateau, ld, cd, la, ca, joueur):
    coups = coups_possibles(plateau, joueur)

    for coup in coups:
        if coup[0] == ld and coup[1] == cd and coup[2] == la and coup[3] == ca:
            return coup

    return None


def coup_est_autorise(coup, coups_autorises):
    for coup_possible in coups_autorises:
        if meme_coup(coup, coup_possible):
            return True

    return False


# ============================================================
# APPLICATION DES COUPS
# ============================================================

def promouvoir_sultan(plateau, ligne, colonne):
    if not est_dans_plateau(ligne, colonne):
        return False

    if plateau[ligne][colonne] == PB and ligne == 0:
        plateau[ligne][colonne] = SB
        return True

    if plateau[ligne][colonne] == PN and ligne == BOARD_SIZE - 1:
        plateau[ligne][colonne] = SN
        return True

    return False


def deplacer_piece(plateau, ld, cd, la, ca):
    if not est_dans_plateau(ld, cd):
        return False

    if not est_dans_plateau(la, ca):
        return False

    piece = plateau[ld][cd]

    if piece == VIDE:
        return False

    if plateau[la][ca] != VIDE:
        return False

    plateau[ld][cd] = VIDE
    plateau[la][ca] = piece

    promotion = promouvoir_sultan(plateau, la, ca)

    return promotion


def appliquer_capture(plateau, ld, cd, la, ca, ligne_capture, colonne_capture):
    if not est_dans_plateau(ld, cd):
        return False

    if not est_dans_plateau(la, ca):
        return False

    if not est_dans_plateau(ligne_capture, colonne_capture):
        return False

    piece = plateau[ld][cd]

    if piece == VIDE:
        return False

    if plateau[la][ca] != VIDE:
        return False

    plateau[ld][cd] = VIDE
    plateau[ligne_capture][colonne_capture] = VIDE
    plateau[la][ca] = piece

    promotion = promouvoir_sultan(plateau, la, ca)

    return promotion


def appliquer_coup(plateau, coup, joueur, position_forcee=None):
    if coup is None:
        return False, "Coup vide.", -1, -1, False, False, []

    ld = coup[0]
    cd = coup[1]
    la = coup[2]
    ca = coup[3]
    type_coup = coup[4]
    ligne_capture = coup[5]
    colonne_capture = coup[6]

    if position_forcee is not None:
        ligne_forcee = position_forcee[0]
        colonne_forcee = position_forcee[1]

        if ld != ligne_forcee or cd != colonne_forcee:
            return False, "La même pièce doit continuer la capture.", -1, -1, False, False, []

        coups_autorises = captures_piece(plateau, ligne_forcee, colonne_forcee, joueur)

    else:
        coups_autorises = coups_possibles(plateau, joueur)

    if not coup_est_autorise(coup, coups_autorises):
        return False, "Coup non autorisé.", -1, -1, False, False, []

    capture_faite = False
    promotion = False

    if type_coup == "capture":
        promotion = appliquer_capture(
            plateau,
            ld,
            cd,
            la,
            ca,
            ligne_capture,
            colonne_capture
        )

        capture_faite = True

    else:
        promotion = deplacer_piece(plateau, ld, cd, la, ca)

    captures_suivantes = []

    if capture_faite:
        captures_suivantes = captures_obligatoires_apres_coup(
            plateau,
            la,
            ca,
            joueur
        )

    return True, "Coup appliqué.", la, ca, capture_faite, promotion, captures_suivantes


def jouer_coup(plateau, coup, joueur, position_forcee=None):
    return appliquer_coup(plateau, coup, joueur, position_forcee)


# ============================================================
# REGLE DU NEFFAKH
# ============================================================

def appliquer_neffakh(plateau, joueur, position_forcee=None):
    if position_forcee is not None:
        ligne = position_forcee[0]
        colonne = position_forcee[1]

        if not est_dans_plateau(ligne, colonne):
            return False

        if not piece_du_joueur(plateau[ligne][colonne], joueur):
            return False

        captures = captures_piece(plateau, ligne, colonne, joueur)

        if len(captures) == 0:
            return False

        plateau[ligne][colonne] = VIDE
        return True

    pieces = pieces_avec_capture(plateau, joueur)

    if len(pieces) == 0:
        return False

    ligne = pieces[0][0]
    colonne = pieces[0][1]

    plateau[ligne][colonne] = VIDE

    return True


# ============================================================
# STATISTIQUES DE BASE DU PLATEAU
# ============================================================

def compter_pieces(plateau, joueur):
    total = 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if piece_du_joueur(plateau[i][j], joueur):
                total += 1

    return total


def compter_sultans(plateau, joueur):
    total = 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if joueur == "blanc" and piece == SB:
                total += 1

            if joueur == "noir" and piece == SN:
                total += 1

    return total


def compter_pions(plateau, joueur):
    total = 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if joueur == "blanc" and piece == PB:
                total += 1

            if joueur == "noir" and piece == PN:
                total += 1

    return total


# ============================================================
# VICTOIRE ET BLOCAGE
# ============================================================

def verifier_victoire(plateau, joueur_courant):
    if compter_pieces(plateau, "blanc") == 0:
        return "noir"

    if compter_pieces(plateau, "noir") == 0:
        return "blanc"

    if len(coups_possibles(plateau, joueur_courant)) == 0:
        return adversaire(joueur_courant)

    return None


def partie_bloquee(plateau, joueur):
    coups = coups_possibles(plateau, joueur)

    if len(coups) == 0:
        return True

    return False


# ============================================================
# HISTORIQUE SIMPLE DES COUPS
# ============================================================

def coup_en_texte(coup):
    if coup is None:
        return ""

    ld = coup[0]
    cd = coup[1]
    la = coup[2]
    ca = coup[3]
    type_coup = coup[4]

    texte = type_coup
    texte += " : "
    texte += "(" + str(ld) + "," + str(cd) + ")"
    texte += " -> "
    texte += "(" + str(la) + "," + str(ca) + ")"

    return texte