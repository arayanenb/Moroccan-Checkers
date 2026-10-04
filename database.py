import mysql.connector
from mysql.connector import Error

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'database': 'jeu_dames',
    'user': 'root',
    'password': 'Aray nb9.'
}

def get_connection():
    #Établit la connexion à la base de données
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def init_database():
    #Crée les tables nécessaires si elles n'existent pas.
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    # Table des joueurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS joueurs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(50) UNIQUE NOT NULL,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_parties INT DEFAULT 0,
            victoires INT DEFAULT 0,
            defaites INT DEFAULT 0,
            abandons INT DEFAULT 0,
            total_captures INT DEFAULT 0,
            total_promotions INT DEFAULT 0,
            total_temps INT DEFAULT 0
        )
    """)
    
    # Table des parties
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            joueur_blanc_id INT,
            joueur_noir_id INT,
            mode_jeu VARCHAR(10),
            niveau_ia VARCHAR(20),
            date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
            duree INT,
            gagnant VARCHAR(10),
            perdant VARCHAR(10),
            statut VARCHAR(20),
            captures_blanc INT DEFAULT 0,
            captures_noir INT DEFAULT 0,
            promotions_blanc INT DEFAULT 0,
            promotions_noir INT DEFAULT 0,
            historique TEXT,
            FOREIGN KEY (joueur_blanc_id) REFERENCES joueurs(id),
            FOREIGN KEY (joueur_noir_id) REFERENCES joueurs(id)
        )
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    return True

def ajouter_joueur(nom):
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO joueurs (nom) VALUES (%s)",
            (nom,)
        )
        connection.commit()
        joueur_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return joueur_id
    except Error as e:
        print(f"Erreur lors de l'ajout du joueur: {e}")
        cursor.close()
        connection.close()
        return None

def get_joueur_id(nom):
    #Récupère l'ID d'un joueur à partir de son nom
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id FROM joueurs WHERE nom = %s",
        (nom,)
    )
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if result:
        return result[0]
    return None

def get_ou_creer_joueur(nom):
    #Récupère l'ID d'un joueur ou le crée s'il n'existe pas
    joueur_id = get_joueur_id(nom)
    if joueur_id is None:
        joueur_id = ajouter_joueur(nom)
    return joueur_id

def get_tous_les_joueurs():
    #Récupère la liste de tous les joueurs
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor()
    cursor.execute("SELECT id, nom FROM joueurs ORDER BY nom")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def enregistrer_partie(data):

    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO parties (
                joueur_blanc_id, joueur_noir_id, mode_jeu, niveau_ia,
                duree, gagnant, perdant, statut,
                captures_blanc, captures_noir,
                promotions_blanc, promotions_noir,
                historique
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['joueur_blanc_id'], data['joueur_noir_id'],
            data['mode_jeu'], data['niveau_ia'],
            data['duree'], data['gagnant'], data['perdant'], data['statut'],
            data['captures_blanc'], data['captures_noir'],
            data['promotions_blanc'], data['promotions_noir'],
            data['historique']
        ))
        connection.commit()
        
        # Mise à jour des statistiques des joueurs
        if data['gagnant'] == 'blanc':
            gagnant_id = data['joueur_blanc_id']
            perdant_id = data['joueur_noir_id']
        elif data['gagnant'] == 'noir':
            gagnant_id = data['joueur_noir_id']
            perdant_id = data['joueur_blanc_id']
        else:
            gagnant_id = None
            perdant_id = None
        
        if gagnant_id is not None:
            cursor.execute(
                "UPDATE joueurs SET total_parties = total_parties + 1, victoires = victoires + 1 WHERE id = %s",
                (gagnant_id,)
            )
            cursor.execute(
                "UPDATE joueurs SET total_parties = total_parties + 1, defaites = defaites + 1 WHERE id = %s",
                (perdant_id,)
            )
            
            # Mise à jour des captures et promotions
            if data['gagnant'] == 'blanc':
                cursor.execute(
                    "UPDATE joueurs SET total_captures = total_captures + %s, total_promotions = total_promotions + %s WHERE id = %s",
                    (data['captures_blanc'], data['promotions_blanc'], gagnant_id)
                )
                cursor.execute(
                    "UPDATE joueurs SET total_captures = total_captures + %s, total_promotions = total_promotions + %s WHERE id = %s",
                    (data['captures_noir'], data['promotions_noir'], perdant_id)
                )
            else:
                cursor.execute(
                    "UPDATE joueurs SET total_captures = total_captures + %s, total_promotions = total_promotions + %s WHERE id = %s",
                    (data['captures_noir'], data['promotions_noir'], gagnant_id)
                )
                cursor.execute(
                    "UPDATE joueurs SET total_captures = total_captures + %s, total_promotions = total_promotions + %s WHERE id = %s",
                    (data['captures_blanc'], data['promotions_blanc'], perdant_id)
                )
            
            cursor.execute(
                "UPDATE joueurs SET total_temps = total_temps + %s WHERE id IN (%s, %s)",
                (data['duree'], gagnant_id, perdant_id)
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Erreur lors de l'enregistrement de la partie: {e}")
        cursor.close()
        connection.close()
        return False

def get_statistiques_joueur(joueur_id):
    #Récupère les statistiques d'un joueur
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            nom,
            total_parties,
            victoires,
            defaites,
            abandons,
            total_captures,
            total_promotions,
            total_temps
        FROM joueurs WHERE id = %s
    """, (joueur_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def get_classement():
    #Récupère le classement général des joueurs
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            nom,
            total_parties,
            victoires,
            defaites,
            ROUND(victoires / NULLIF(total_parties, 0) * 100, 2) as taux_victoire
        FROM joueurs
        WHERE total_parties > 0
        ORDER BY taux_victoire DESC, victoires DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def get_historique_joueur(joueur_id):
    #Récupère l'historique des parties d'un joueur
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.id,
            j1.nom as joueur_blanc,
            j2.nom as joueur_noir,
            p.mode_jeu,
            p.niveau_ia,
            p.date_heure,
            p.duree,
            p.gagnant,
            p.statut,
            p.captures_blanc,
            p.captures_noir,
            p.promotions_blanc,
            p.promotions_noir
        FROM parties p
        JOIN joueurs j1 ON p.joueur_blanc_id = j1.id
        JOIN joueurs j2 ON p.joueur_noir_id = j2.id
        WHERE p.joueur_blanc_id = %s OR p.joueur_noir_id = %s
        ORDER BY p.date_heure DESC
    """, (joueur_id, joueur_id))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def get_stats_globales():
    #Récupère les statistiques globales.
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            COUNT(*) as total_parties,
            AVG(duree) as duree_moyenne,
            AVG(captures_blanc + captures_noir) as captures_moyennes,
            AVG(promotions_blanc + promotions_noir) as promotions_moyennes
        FROM parties
    """)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result