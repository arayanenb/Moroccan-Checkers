# test_db.py
import database as db

print("Test de connexion à la base de données...")

# Tester la connexion
conn = db.get_connection()
if conn:
    print("✅ Connexion réussie !")
    conn.close()
else:
    print("❌ Échec de connexion. Vérifiez vos identifiants.")
    exit()

# Tester l'initialisation
print("Vérification des tables...")
if db.init_database():
    print("✅ Tables vérifiées/créées avec succès !")
else:
    print("❌ Erreur lors de l'initialisation.")

# Tester l'ajout d'un joueur
print("Test d'ajout d'un joueur...")
joueur_id = db.ajouter_joueur("Testeur")
if joueur_id:
    print(f"✅ Joueur ajouté avec ID: {joueur_id}")
else:
    print("❌ Erreur lors de l'ajout du joueur (peut-être déjà existant)")

# Lister les joueurs
print("Liste des joueurs :")
joueurs = db.get_tous_les_joueurs()
for j_id, nom in joueurs:
    print(f"  - {nom} (ID: {j_id})")

print("\n✅ Test terminé !")