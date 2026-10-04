import random

from settings import (
    BOARD_SIZE,
    PB,
    PN,
    SB,
    SN,
    NIVEAU_DEBUTANT,
    NIVEAU_INTERMEDIAIRE,
    NIVEAU_AVANCE,
    NIVEAU_EXPERT
)

from player import (
    coups_possibles,
    captures_piece,
    appliquer_coup,
    copier_plateau,
    adversaire,
    verifier_victoire,
    piece_du_joueur,
    piece_adverse,
    compter_pieces
)


# ============================================================
# FONCTION PRINCIPALE DE L'IA
# ============================================================

def choisir_coup_ia(plateau, joueur, niveau, coups_forces=None):
    if coups_forces is None:
        coups = coups_possibles(plateau, joueur)
        position_forcee = None
    else:
        coups = coups_forces
        position_forcee = position_forcee_depuis_coups(coups_forces)

    if len(coups) == 0:
        return None

    if niveau == NIVEAU_DEBUTANT:
        return choisir_coup_debutant(coups)

    if niveau == NIVEAU_INTERMEDIAIRE:
        return choisir_coup_intermediaire(plateau, joueur, coups, position_forcee)

    if niveau == NIVEAU_AVANCE:
        return choisir_coup_minimax(plateau, joueur, 2, coups, position_forcee)

    if niveau == NIVEAU_EXPERT:
        return choisir_coup_alpha_beta(plateau, joueur, 3, coups, position_forcee)

    return choisir_coup_debutant(coups)


def choisir_capture_suivante_ia(plateau, joueur, captures_suivantes, niveau):
    return choisir_coup_ia(plateau, joueur, niveau, captures_suivantes)


# ============================================================
# OUTILS
# ============================================================

def initialiser_hasard(valeur=0):
    random.seed(valeur)


def choisir_premier_coup(coups):
    if len(coups) == 0:
        return None

    coups_tries = sorted(coups)
    return coups_tries[0]


def position_forcee_depuis_coups(coups):
    if len(coups) == 0:
        return None

    ligne = coups[0][0]
    colonne = coups[0][1]

    for coup in coups:
        if coup[0] != ligne or coup[1] != colonne:
            return None

    return (ligne, colonne)


def est_capture(coup):
    return coup[4] == "capture"


def valeur_piece(piece):
    if piece == PB or piece == PN:
        return 10

    if piece == SB or piece == SN:
        return 30

    return 0


def gagnant_par_pieces(plateau):
    if compter_pieces(plateau, "blanc") == 0:
        return "noir"

    if compter_pieces(plateau, "noir") == 0:
        return "blanc"

    return None


# ============================================================
# EVALUATION DU PLATEAU
# ============================================================

def nombre_captures_disponibles(plateau, joueur):
    coups = coups_possibles(plateau, joueur)
    total = 0

    for coup in coups:
        if est_capture(coup):
            total += 1

    return total


def score_centre(plateau, joueur):
    score = 0

    for i in range(3, 7):
        for j in range(3, 7):
            piece = plateau[i][j]

            if piece_du_joueur(piece, joueur):
                score += 1

            elif piece_adverse(piece, joueur):
                score -= 1

    return score


def score_promotion_future(plateau, joueur):
    score = 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if joueur == "blanc" and piece == PB:
                score += BOARD_SIZE - 1 - i

            if joueur == "noir" and piece == PN:
                score += i

    return score


def evaluer_plateau(plateau, joueur):
    score = 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = plateau[i][j]

            if piece_du_joueur(piece, joueur):
                score += valeur_piece(piece)

            elif piece_adverse(piece, joueur):
                score -= valeur_piece(piece)

    joueur_adverse = adversaire(joueur)

    score += score_centre(plateau, joueur) * 2
    score += score_promotion_future(plateau, joueur)
    score -= score_promotion_future(plateau, joueur_adverse)

    score += nombre_captures_disponibles(plateau, joueur) * 5
    score -= nombre_captures_disponibles(plateau, joueur_adverse) * 5

    return score


# ============================================================
# SIMULATION DES COUPS
# ============================================================

def simuler_coup(plateau, coup, joueur, position_forcee=None):
    nouveau_plateau = copier_plateau(plateau)

    ok, message, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
        nouveau_plateau,
        coup,
        joueur,
        position_forcee
    )

    if not ok:
        return None, False, -1, -1, False, False, []

    return nouveau_plateau, True, ligne, colonne, capture, promotion, captures_suivantes


def score_coup_simple(plateau, coup, joueur, position_forcee=None):
    nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
        plateau,
        coup,
        joueur,
        position_forcee
    )

    if not ok:
        return -999999

    score = evaluer_plateau(nouveau_plateau, joueur)

    if capture:
        score += 20

    if promotion:
        score += 25

    if len(captures_suivantes) > 0:
        score += len(captures_suivantes) * 10

    return score


def terminer_capture_simple(plateau, joueur, ligne, colonne):
    """
    Utilisé par le niveau intermédiaire.
    Il termine une chaîne de captures avec une logique simple :
    à chaque étape, il prend la capture ayant le meilleur score immédiat.
    """

    captures = captures_piece(plateau, ligne, colonne, joueur)

    while len(captures) > 0:
        meilleur_score = -999999
        meilleur_coup = None

        for coup in captures:
            score = score_coup_simple(plateau, coup, joueur, (ligne, colonne))

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

            elif score == meilleur_score:
                if meilleur_coup is None or coup < meilleur_coup:
                    meilleur_coup = coup

        ok, message, ligne, colonne, capture, promotion, captures = appliquer_coup(
            plateau,
            meilleur_coup,
            joueur,
            (ligne, colonne)
        )

        if not ok:
            break

    return plateau


def score_coup_avec_chaine(plateau, coup, joueur, position_forcee=None):
    """
    Corrige le niveau intermédiaire :
    le score ne s'arrête pas au premier saut.
    Il simule aussi la suite obligatoire des captures.
    """

    nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
        plateau,
        coup,
        joueur,
        position_forcee
    )

    if not ok:
        return -999999

    if len(captures_suivantes) > 0:
        terminer_capture_simple(nouveau_plateau, joueur, ligne, colonne)

    score = evaluer_plateau(nouveau_plateau, joueur)

    if capture:
        score += 50

    if promotion:
        score += 25

    return score


# ============================================================
# NIVEAU 1 : DEBUTANT
# ============================================================

def choisir_coup_debutant(coups):
    if len(coups) == 0:
        return None

    return random.choice(coups)


# ============================================================
# NIVEAU 2 : INTERMEDIAIRE
# ============================================================

def choisir_coup_intermediaire(plateau, joueur, coups, position_forcee=None):
    meilleur_score = -999999
    meilleurs_coups = []

    for coup in coups:
        score = score_coup_avec_chaine(plateau, coup, joueur, position_forcee)

        if est_capture(coup):
            score += 50

        if score > meilleur_score:
            meilleur_score = score
            meilleurs_coups = [coup]

        elif score == meilleur_score:
            meilleurs_coups.append(coup)

    return choisir_premier_coup(meilleurs_coups)


# ============================================================
# NIVEAU 3 : MINIMAX
# ============================================================

def choisir_coup_minimax(plateau, joueur, profondeur, coups, position_forcee=None):
    meilleur_score = -999999
    meilleurs_coups = []

    for coup in coups:
        nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
            plateau,
            coup,
            joueur,
            position_forcee
        )

        if not ok:
            continue

        if len(captures_suivantes) > 0:
            # Même tour : la profondeur ne diminue pas.
            score = minimax(
                nouveau_plateau,
                joueur,
                joueur,
                profondeur,
                (ligne, colonne)
            )
        else:
            # Tour terminé : la profondeur diminue.
            score = minimax(
                nouveau_plateau,
                joueur,
                adversaire(joueur),
                profondeur - 1,
                None
            )

        if score > meilleur_score:
            meilleur_score = score
            meilleurs_coups = [coup]

        elif score == meilleur_score:
            meilleurs_coups.append(coup)

    if len(meilleurs_coups) == 0:
        return choisir_premier_coup(coups)

    return choisir_premier_coup(meilleurs_coups)


def minimax(plateau, joueur_ia, joueur_courant, profondeur, position_forcee=None):
    gagnant = gagnant_par_pieces(plateau)

    if gagnant == joueur_ia:
        return 100000

    if gagnant == adversaire(joueur_ia):
        return -100000

    if position_forcee is None:
        gagnant = verifier_victoire(plateau, joueur_courant)

        if gagnant == joueur_ia:
            return 100000

        if gagnant == adversaire(joueur_ia):
            return -100000

        if profondeur <= 0:
            return evaluer_plateau(plateau, joueur_ia)

        coups = coups_possibles(plateau, joueur_courant)

    else:
        # Capture multiple obligatoire :
        # on continue la chaîne même si profondeur == 0.
        coups = captures_piece(
            plateau,
            position_forcee[0],
            position_forcee[1],
            joueur_courant
        )

        if len(coups) == 0:
            return minimax(
                plateau,
                joueur_ia,
                adversaire(joueur_courant),
                profondeur - 1,
                None
            )

    if len(coups) == 0:
        if joueur_courant == joueur_ia:
            return -100000

        return 100000

    if joueur_courant == joueur_ia:
        meilleur_score = -999999

        for coup in coups:
            nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
                plateau,
                coup,
                joueur_courant,
                position_forcee
            )

            if not ok:
                continue

            if len(captures_suivantes) > 0:
                score = minimax(
                    nouveau_plateau,
                    joueur_ia,
                    joueur_courant,
                    profondeur,
                    (ligne, colonne)
                )
            else:
                score = minimax(
                    nouveau_plateau,
                    joueur_ia,
                    adversaire(joueur_courant),
                    profondeur - 1,
                    None
                )

            if score > meilleur_score:
                meilleur_score = score

        return meilleur_score

    else:
        meilleur_score = 999999

        for coup in coups:
            nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
                plateau,
                coup,
                joueur_courant,
                position_forcee
            )

            if not ok:
                continue

            if len(captures_suivantes) > 0:
                score = minimax(
                    nouveau_plateau,
                    joueur_ia,
                    joueur_courant,
                    profondeur,
                    (ligne, colonne)
                )
            else:
                score = minimax(
                    nouveau_plateau,
                    joueur_ia,
                    adversaire(joueur_courant),
                    profondeur - 1,
                    None
                )

            if score < meilleur_score:
                meilleur_score = score

        return meilleur_score


# ============================================================
# NIVEAU 4 : ALPHA-BETA
# ============================================================

def choisir_coup_alpha_beta(plateau, joueur, profondeur, coups, position_forcee=None):
    meilleur_score = -999999
    meilleurs_coups = []

    alpha = -999999
    beta = 999999

    for coup in coups:
        nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
            plateau,
            coup,
            joueur,
            position_forcee
        )

        if not ok:
            continue

        if len(captures_suivantes) > 0:
            score = alpha_beta(
                nouveau_plateau,
                joueur,
                joueur,
                profondeur,
                alpha,
                beta,
                (ligne, colonne)
            )
        else:
            score = alpha_beta(
                nouveau_plateau,
                joueur,
                adversaire(joueur),
                profondeur - 1,
                alpha,
                beta,
                None
            )

        if score > meilleur_score:
            meilleur_score = score
            meilleurs_coups = [coup]

        elif score == meilleur_score:
            meilleurs_coups.append(coup)

        if score > alpha:
            alpha = score

    if len(meilleurs_coups) == 0:
        return choisir_premier_coup(coups)

    return choisir_premier_coup(meilleurs_coups)


def alpha_beta(plateau, joueur_ia, joueur_courant, profondeur, alpha, beta, position_forcee=None):
    gagnant = gagnant_par_pieces(plateau)

    if gagnant == joueur_ia:
        return 100000

    if gagnant == adversaire(joueur_ia):
        return -100000

    if position_forcee is None:
        gagnant = verifier_victoire(plateau, joueur_courant)

        if gagnant == joueur_ia:
            return 100000

        if gagnant == adversaire(joueur_ia):
            return -100000

        if profondeur <= 0:
            return evaluer_plateau(plateau, joueur_ia)

        coups = coups_possibles(plateau, joueur_courant)

    else:
        # Capture multiple obligatoire :
        # on ne coupe pas la chaîne à cause de la profondeur.
        coups = captures_piece(
            plateau,
            position_forcee[0],
            position_forcee[1],
            joueur_courant
        )

        if len(coups) == 0:
            return alpha_beta(
                plateau,
                joueur_ia,
                adversaire(joueur_courant),
                profondeur - 1,
                alpha,
                beta,
                None
            )

    if len(coups) == 0:
        if joueur_courant == joueur_ia:
            return -100000

        return 100000

    if joueur_courant == joueur_ia:
        meilleur_score = -999999

        for coup in coups:
            nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
                plateau,
                coup,
                joueur_courant,
                position_forcee
            )

            if not ok:
                continue

            if len(captures_suivantes) > 0:
                score = alpha_beta(
                    nouveau_plateau,
                    joueur_ia,
                    joueur_courant,
                    profondeur,
                    alpha,
                    beta,
                    (ligne, colonne)
                )
            else:
                score = alpha_beta(
                    nouveau_plateau,
                    joueur_ia,
                    adversaire(joueur_courant),
                    profondeur - 1,
                    alpha,
                    beta,
                    None
                )

            if score > meilleur_score:
                meilleur_score = score

            if meilleur_score > alpha:
                alpha = meilleur_score

            if beta <= alpha:
                break

        return meilleur_score

    else:
        meilleur_score = 999999

        for coup in coups:
            nouveau_plateau, ok, ligne, colonne, capture, promotion, captures_suivantes = simuler_coup(
                plateau,
                coup,
                joueur_courant,
                position_forcee
            )

            if not ok:
                continue

            if len(captures_suivantes) > 0:
                score = alpha_beta(
                    nouveau_plateau,
                    joueur_ia,
                    joueur_courant,
                    profondeur,
                    alpha,
                    beta,
                    (ligne, colonne)
                )
            else:
                score = alpha_beta(
                    nouveau_plateau,
                    joueur_ia,
                    adversaire(joueur_courant),
                    profondeur - 1,
                    alpha,
                    beta,
                    None
                )

            if score < meilleur_score:
                meilleur_score = score

            if meilleur_score < beta:
                beta = meilleur_score

            if beta <= alpha:
                break

        return meilleur_score