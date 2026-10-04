# interface.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import time
from settings import *
from player import *
from enemy import *
import database as db
from main import jouer_tour_humain, jouer_tour_ia, nom_joueur

class JeuDames:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jeu de Dames Marocain")
        self.root.geometry("900x700")
        
        # Variables de jeu
        self.plateau = None
        self.joueur_courant = "blanc"
        self.tour = 1
        self.mode = None
        self.niveau_ia = None
        self.nom_blanc = None
        self.nom_noir = None
        self.id_blanc = None
        self.id_noir = None
        self.partie_en_cours = False
        
        # Variables pour les coups
        self.piece_selectionnee = None
        self.coups_possibles_piece = []
        self.position_forcee = None
        
        # Statistiques
        self.captures_blanc = 0
        self.captures_noir = 0
        self.promotions_blanc = 0
        self.promotions_noir = 0
        self.historique = []
        self.debut_partie = None
        
        # Interface
        self.create_menu()
        self.create_main_frame()
        
        # Initialiser la base de données
        db.init_database()
        
    def create_menu(self):
        """Crée le menu principal."""
        menubar = tk.Menu(self.root)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouvelle partie", command=self.nouvelle_partie)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Joueurs
        joueurs_menu = tk.Menu(menubar, tearoff=0)
        joueurs_menu.add_command(label="Gérer les joueurs", command=self.gerer_joueurs)
        menubar.add_cascade(label="Joueurs", menu=joueurs_menu)
        
        # Menu Statistiques
        stats_menu = tk.Menu(menubar, tearoff=0)
        stats_menu.add_command(label="Statistiques globales", command=self.afficher_stats_globales)
        stats_menu.add_command(label="Classement", command=self.afficher_classement)
        menubar.add_cascade(label="Statistiques", menu=stats_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_frame(self):
        """Crée le cadre principal de l'application."""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de gauche pour le plateau
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas pour le damier
        self.canvas = tk.Canvas(
            self.left_frame,
            width=10 * TAILLE_CASE,
            height=10 * TAILLE_CASE,
            bg="white"
        )
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Frame de droite pour les infos
        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        # Titre
        tk.Label(
            self.right_frame,
            text="Informations de la partie",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        # Frame pour les infos joueurs
        self.info_frame = tk.Frame(self.right_frame)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.joueur_label = tk.Label(
            self.info_frame,
            text="Joueur courant :",
            font=("Arial", 12)
        )
        self.joueur_label.pack()
        
        self.tour_label = tk.Label(
            self.info_frame,
            text="Tour : 1",
            font=("Arial", 12)
        )
        self.tour_label.pack()
        
        self.pieces_label = tk.Label(
            self.info_frame,
            text="Blancs: 12 | Noirs: 12",
            font=("Arial", 12)
        )
        self.pieces_label.pack()
        
        self.captures_label = tk.Label(
            self.info_frame,
            text="Captures: Blancs 0 | Noirs 0",
            font=("Arial", 12)
        )
        self.captures_label.pack()
        
        self.promotions_label = tk.Label(
            self.info_frame,
            text="Promotions: Blancs 0 | Noirs 0",
            font=("Arial", 12)
        )
        self.promotions_label.pack()
        
        # Boutons
        self.btn_frame = tk.Frame(self.right_frame)
        self.btn_frame.pack(fill=tk.X, pady=10)
        
        self.btn_abandonner = tk.Button(
            self.btn_frame,
            text="Abandonner",
            command=self.abandonner,
            bg="#FF4444",
            fg="white",
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.btn_abandonner.pack(side=tk.LEFT, padx=5)
        
        self.btn_neffakh = tk.Button(
            self.btn_frame,
            text="Appliquer Neffakh",
            command=self.appliquer_neffakh,
            bg="#FF8800",
            fg="white",
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.btn_neffakh.pack(side=tk.LEFT, padx=5)
        
        # Zone de chat/historique
        tk.Label(
            self.right_frame,
            text="Historique des coups",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        self.historique_text = scrolledtext.ScrolledText(
            self.right_frame,
            height=15,
            width=40
        )
        self.historique_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Message d'accueil
        self.afficher_message("Bienvenue ! Commencez une nouvelle partie.")
        
    def afficher_message(self, message):
        """Affiche un message dans la zone d'historique."""
        self.historique_text.insert(tk.END, f"{message}\n")
        self.historique_text.see(tk.END)
    
    def nouvelle_partie(self):
        """Ouvre la fenêtre de configuration de la nouvelle partie."""
        if self.partie_en_cours:
            if not messagebox.askyesno("Partie en cours", "Voulez-vous abandonner la partie en cours ?"):
                return
        
        config = tk.Toplevel(self.root)
        config.title("Configuration de la partie")
        config.geometry("400x400")
        config.transient(self.root)
        config.grab_set()
        
        # Mode de jeu
        tk.Label(config, text="Mode de jeu :", font=("Arial", 12, "bold")).pack(pady=10)
        mode_var = tk.StringVar(value="jcj")
        tk.Radiobutton(config, text="Joueur contre Joueur", variable=mode_var, value="jcj").pack()
        tk.Radiobutton(config, text="Joueur contre IA", variable=mode_var, value="jcia").pack()
        
        # Sélection des joueurs
        tk.Label(config, text="\nJoueur Blanc :", font=("Arial", 12)).pack(pady=5)
        blanc_var = tk.StringVar()
        combo_blanc = ttk.Combobox(config, textvariable=blanc_var, width=30)
        combo_blanc['values'] = self.get_liste_joueurs()
        combo_blanc.set("Sélectionner un joueur")
        combo_blanc.pack()
        
        tk.Label(config, text="Joueur Noir :", font=("Arial", 12)).pack(pady=5)
        noir_var = tk.StringVar()
        combo_noir = ttk.Combobox(config, textvariable=noir_var, width=30)
        combo_noir['values'] = self.get_liste_joueurs()
        combo_noir.set("Sélectionner un joueur")
        combo_noir.pack()
        
        # Niveau IA (visible seulement en mode JCIA)
        niveau_frame = tk.Frame(config)
        niveau_frame.pack(pady=10)
        
        tk.Label(niveau_frame, text="Niveau IA :", font=("Arial", 12)).pack()
        niveau_var = tk.IntVar(value=NIVEAU_DEBUTANT)
        
        for niveau, nom in NOMS_NIVEAUX.items():
            tk.Radiobutton(
                niveau_frame,
                text=nom,
                variable=niveau_var,
                value=niveau
            ).pack()
        
        def toggle_niveau():
            if mode_var.get() == "jcj":
                niveau_frame.pack_forget()
            else:
                niveau_frame.pack(pady=10)
        
        mode_var.trace('w', lambda *args: toggle_niveau())
        toggle_niveau()
        
        # Bouton Créer un nouveau joueur
        def creer_nouveau_joueur():
            nom = simpledialog.askstring("Nouveau joueur", "Entrez le nom du joueur :")
            if nom and nom.strip():
                nom = nom.strip()
                joueur_id = db.ajouter_joueur(nom)
                if joueur_id:
                    messagebox.showinfo("Succès", f"Joueur '{nom}' créé avec succès !")
                    combo_blanc['values'] = self.get_liste_joueurs()
                    combo_noir['values'] = self.get_liste_joueurs()
                    combo_blanc.set(nom)
                else:
                    messagebox.showerror("Erreur", "Ce nom existe déjà ou erreur de base de données.")
        
        tk.Button(
            config,
            text="Créer un nouveau joueur",
            command=creer_nouveau_joueur
        ).pack(pady=10)
        
        # Bouton Démarrer
        def demarrer():
            nom_blanc = blanc_var.get()
            nom_noir = noir_var.get()
            mode = mode_var.get()
            niveau = niveau_var.get() if mode == "jcia" else None
            
            if nom_blanc == "Sélectionner un joueur" or not nom_blanc:
                messagebox.showerror("Erreur", "Veuillez sélectionner le joueur blanc.")
                return
            if nom_noir == "Sélectionner un joueur" or not nom_noir:
                messagebox.showerror("Erreur", "Veuillez sélectionner le joueur noir.")
                return
            if nom_blanc == nom_noir:
                messagebox.showerror("Erreur", "Les deux joueurs doivent être différents.")
                return
            
            config.destroy()
            self.lancer_partie(nom_blanc, nom_noir, mode, niveau)
        
        tk.Button(config, text="Démarrer", command=demarrer, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)
    
    def get_liste_joueurs(self):
        """Récupère la liste des joueurs de la base de données."""
        joueurs = db.get_tous_les_joueurs()
        if joueurs:
            return [joueur[1] for joueur in joueurs]
        return ["Joueur1", "Joueur2"]
    
    def lancer_partie(self, nom_blanc, nom_noir, mode, niveau):
        """Lance la partie avec la configuration choisie."""
        self.partie_en_cours = True
        
        self.nom_blanc = nom_blanc
        self.nom_noir = nom_noir
        self.mode = mode
        self.niveau_ia = niveau
        
        # Récupérer les IDs des joueurs
        self.id_blanc = db.get_ou_creer_joueur(nom_blanc)
        self.id_noir = db.get_ou_creer_joueur(nom_noir)
        
        # Initialiser le jeu
        self.plateau = creer_plateau()
        self.joueur_courant = "blanc"
        self.tour = 1
        self.piece_selectionnee = None
        self.position_forcee = None
        
        self.captures_blanc = 0
        self.captures_noir = 0
        self.promotions_blanc = 0
        self.promotions_noir = 0
        self.historique = []
        self.debut_partie = time.time()
        
        # Activer les boutons
        self.btn_abandonner.config(state=tk.NORMAL)
        
        # Vider l'historique
        self.historique_text.delete(1.0, tk.END)
        self.afficher_message(f"Nouvelle partie : {nom_blanc} (blanc) vs {nom_noir} (noir)")
        if mode == MODE_JCIA:
            self.afficher_message(f"Mode : Joueur vs IA ({NOMS_NIVEAUX[niveau]})")
        else:
            self.afficher_message("Mode : Joueur vs Joueur")
        
        self.afficher_plateau()
        self.mettre_a_jour_infos()
    
    def afficher_plateau(self):
        """Dessine le plateau sur le canvas."""
        self.canvas.delete("all")
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                x1 = j * TAILLE_CASE
                y1 = i * TAILLE_CASE
                x2 = x1 + TAILLE_CASE
                y2 = y1 + TAILLE_CASE
                
                # Couleur de la case
                if (i + j) % 2 == 0:
                    color = COULEUR_CLAIR
                else:
                    color = COULEUR_FONCE
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Dessiner la pièce si présente
                piece = self.plateau[i][j]
                if piece != VIDE:
                    cx = x1 + TAILLE_CASE // 2
                    cy = y1 + TAILLE_CASE // 2
                    radius = TAILLE_CASE // 2 - 8
                    
                    # Couleur de la pièce
                    if piece in [PB, SB]:
                        color_piece = "white"
                    else:
                        color_piece = "black"
                    
                    # Dessiner le cercle
                    self.canvas.create_oval(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        fill=color_piece,
                        outline="gray",
                        width=2
                    )
                    
                    # Si c'est un Sultan, ajouter un cercle ou une couronne
                    if piece in [SB, SN]:
                        self.canvas.create_oval(
                            cx - radius//2, cy - radius//2,
                            cx + radius//2, cy + radius//2,
                            fill="gold",
                            outline="gold",
                            width=2
                        )
        
        # Mettre en surbrillance la pièce sélectionnée
        if self.piece_selectionnee:
            i, j = self.piece_selectionnee
            x1 = j * TAILLE_CASE
            y1 = i * TAILLE_CASE
            x2 = x1 + TAILLE_CASE
            y2 = y1 + TAILLE_CASE
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=COULEUR_SELECTION,
                width=4
            )
            
            # Afficher les coups possibles
            for coup in self.coups_possibles_piece:
                la, ca = coup[2], coup[3]
                x1 = ca * TAILLE_CASE + 5
                y1 = la * TAILLE_CASE + 5
                x2 = x1 + TAILLE_CASE - 10
                y2 = y1 + TAILLE_CASE - 10
                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=COULEUR_MOUVEMENT,
                    outline="green",
                    width=2,
                    tags="move"
                )
    
    def on_click(self, event):
        """Gère les clics sur le plateau."""
        if not self.partie_en_cours:
            return
        
        col = event.x // TAILLE_CASE
        row = event.y // TAILLE_CASE
        
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return
        
        # Vérifier si c'est le tour de l'IA (l'IA joue toute seule, pas de clic possible)
        if self.mode == MODE_JCIA and self.joueur_courant == "noir":
            return
        
        piece = self.plateau[row][col]
        
        # Si une pièce est déjà sélectionnée
        if self.piece_selectionnee:
            # Vérifier si on clique sur un mouvement possible
            for coup in self.coups_possibles_piece:
                if coup[2] == row and coup[3] == col:
                    self.executer_coup(coup)
                    return
            
            # Désélectionner si on clique ailleurs
            self.piece_selectionnee = None
            self.coups_possibles_piece = []
            self.afficher_plateau()
            return
        
        # Sélectionner une pièce
        if piece_du_joueur(piece, self.joueur_courant):
            # Vérifier si cette pièce a des coups possibles
            coups = coups_possibles_piece(self.plateau, row, col, self.joueur_courant)
            if coups:
                self.piece_selectionnee = (row, col)
                self.coups_possibles_piece = coups
                self.afficher_plateau()
    
    def executer_coup(self, coup):
        """Exécute un coup et continue la partie."""
        if not self.partie_en_cours:
            return
        
        # Déterminer la position forcée
        position_forcee = self.position_forcee
        
        # Appliquer le coup
        ok, msg, ligne, colonne, capture, promotion, captures_suivantes = appliquer_coup(
            self.plateau,
            coup,
            self.joueur_courant,
            position_forcee
        )
        
        if not ok:
            self.afficher_message(f"Erreur : {msg}")
            return
        
        # Enregistrer le coup
        nom_joueur = self.nom_blanc if self.joueur_courant == "blanc" else self.nom_noir
        self.historique.append(f"{nom_joueur} : {coup_en_texte(coup)}")
        self.afficher_message(f"{nom_joueur} : {coup_en_texte(coup)}")
        
        # Mettre à jour les statistiques
        if capture:
            if self.joueur_courant == "blanc":
                self.captures_blanc += 1
            else:
                self.captures_noir += 1
        
        if promotion:
            if self.joueur_courant == "blanc":
                self.promotions_blanc += 1
            else:
                self.promotions_noir += 1
        
        # Désélectionner la pièce
        self.piece_selectionnee = None
        self.coups_possibles_piece = []
        
        # Vérifier les captures suivantes
        if len(captures_suivantes) > 0:
            self.position_forcee = (ligne, colonne)
            self.afficher_plateau()
            self.mettre_a_jour_infos()
            self.afficher_message("Capture multiple obligatoire !")

            # Si c'est l'IA qui doit continuer la chaîne de captures,
            # il faut relancer son tour, sinon la partie se bloque.
            if self.mode == MODE_JCIA and self.joueur_courant == "noir":
                self.root.after(500, self.tour_ia)
            return
        
        self.position_forcee = None
        
        # Vérifier la victoire
        gagnant = verifier_victoire(self.plateau, self.joueur_courant)
        if gagnant:
            self.fin_partie(gagnant)
            return
        
        # Changer de joueur
        self.joueur_courant = adversaire(self.joueur_courant)
        self.tour += 1
        
        self.afficher_plateau()
        self.mettre_a_jour_infos()
        
        # Si c'est le tour de l'IA, jouer automatiquement
        if self.mode == MODE_JCIA and self.joueur_courant == "noir":
            self.root.after(500, self.tour_ia)
    
    def tour_ia(self):
        """Exécute le tour de l'IA."""
        if not self.partie_en_cours:
            return
        
        if self.joueur_courant != "noir":
            return
        
        # Si une capture multiple est en cours, l'IA doit continuer
        # avec la même pièce (position_forcee), pas en choisir une nouvelle.
        if self.position_forcee is not None:
            coups_forces = captures_piece(
                self.plateau,
                self.position_forcee[0],
                self.position_forcee[1],
                "noir"
            )

            if len(coups_forces) == 0:
                self.fin_partie("blanc")
                return

            coup = choisir_coup_ia(self.plateau, "noir", self.niveau_ia, coups_forces)
        else:
            # Vérifier si l'IA a des coups possibles
            coups = coups_possibles(self.plateau, "noir")
            if len(coups) == 0:
                self.fin_partie("blanc")
                return

            # Choisir un coup
            coup = choisir_coup_ia(self.plateau, "noir", self.niveau_ia, None)
        
        if coup is None:
            self.fin_partie("blanc")
            return
        
        # Exécuter le coup
        self.executer_coup(coup)
    
    def mettre_a_jour_infos(self):
        """Met à jour les informations affichées."""
        nom_courant = self.nom_blanc if self.joueur_courant == "blanc" else self.nom_noir
        self.joueur_label.config(
            text=f"Joueur courant : {nom_courant} ({self.joueur_courant})"
        )
        self.tour_label.config(text=f"Tour : {self.tour}")
        
        pieces_blanc = compter_pieces(self.plateau, "blanc")
        pieces_noir = compter_pieces(self.plateau, "noir")
        self.pieces_label.config(text=f"Blancs: {pieces_blanc} | Noirs: {pieces_noir}")
        
        self.captures_label.config(
            text=f"Captures: Blancs {self.captures_blanc} | Noirs {self.captures_noir}"
        )
        self.promotions_label.config(
            text=f"Promotions: Blancs {self.promotions_blanc} | Noirs {self.promotions_noir}"
        )
        
        # Activer/désactiver le bouton Neffakh
        if existe_capture(self.plateau, self.joueur_courant):
            self.btn_neffakh.config(state=tk.NORMAL)
        else:
            self.btn_neffakh.config(state=tk.DISABLED)
    
    def appliquer_neffakh(self):
        """Applique la règle du Neffakh."""
        if not self.partie_en_cours:
            return
        
        if not existe_capture(self.plateau, self.joueur_courant):
            self.afficher_message("Aucune capture obligatoire à punir.")
            return
        
        ok = appliquer_neffakh(self.plateau, self.joueur_courant, self.position_forcee)
        if ok:
            nom_joueur = self.nom_blanc if self.joueur_courant == "blanc" else self.nom_noir
            self.afficher_message(f"Neffakh appliqué ! Une pièce de {nom_joueur} a été retirée.")
            self.historique.append(f"{nom_joueur} : Neffakh appliqué")
            
            self.piece_selectionnee = None
            self.coups_possibles_piece = []
            self.position_forcee = None
            
            # Vérifier la victoire
            gagnant = verifier_victoire(self.plateau, self.joueur_courant)
            if gagnant:
                self.fin_partie(gagnant)
                return
            
            # Changer de joueur
            self.joueur_courant = adversaire(self.joueur_courant)
            self.tour += 1
            
            self.afficher_plateau()
            self.mettre_a_jour_infos()
            
            # Si c'est le tour de l'IA
            if self.mode == MODE_JCIA and self.joueur_courant == "noir":
                self.root.after(500, self.tour_ia)
        else:
            self.afficher_message("Impossible d'appliquer Neffakh.")
    
    def abandonner(self):
        """Abandonne la partie."""
        if self.partie_en_cours:
            if messagebox.askyesno("Abandon", "Voulez-vous vraiment abandonner ?"):
                perdant_nom = self.nom_blanc if self.joueur_courant == "blanc" else self.nom_noir
                gagnant = adversaire(self.joueur_courant)
                self.historique.append(f"{perdant_nom} abandonne.")
                self.fin_partie(gagnant, "abandon")
    
    def fin_partie(self, gagnant, statut="normale"):
        """Termine la partie et enregistre les résultats."""
        if not self.partie_en_cours:
            return
        
        self.partie_en_cours = False
        self.btn_abandonner.config(state=tk.DISABLED)
        self.btn_neffakh.config(state=tk.DISABLED)
        self.piece_selectionnee = None
        
        # Afficher le résultat
        if gagnant == "blanc":
            gagnant_nom = self.nom_blanc
            perdant_nom = self.nom_noir
            message = f"🏆 Victoire de {gagnant_nom} (Blancs) !"
        elif gagnant == "noir":
            gagnant_nom = self.nom_noir
            perdant_nom = self.nom_blanc
            message = f"🏆 Victoire de {gagnant_nom} (Noirs) !"
        else:
            gagnant_nom = None
            perdant_nom = None
            message = "🤝 Match nul !"
        
        self.afficher_message(f"\n{'='*40}")
        self.afficher_message(message)
        self.afficher_message(f"Durée : {int(time.time() - self.debut_partie)} secondes")
        
        # Enregistrer dans la base de données
        data = {
            'joueur_blanc_id': self.id_blanc,
            'joueur_noir_id': self.id_noir,
            'mode_jeu': self.mode,
            'niveau_ia': NOMS_NIVEAUX.get(self.niveau_ia, None),
            'duree': int(time.time() - self.debut_partie),
            'gagnant': gagnant,
            'perdant': adversaire(gagnant) if gagnant else None,
            'statut': statut,
            'captures_blanc': self.captures_blanc,
            'captures_noir': self.captures_noir,
            'promotions_blanc': self.promotions_blanc,
            'promotions_noir': self.promotions_noir,
            'historique': "\n".join(self.historique)
        }
        db.enregistrer_partie(data)
        self.afficher_message("Partie enregistrée dans la base de données.")
        
        messagebox.showinfo("Fin de partie", message)
    
    def gerer_joueurs(self):
        """Ouvre la fenêtre de gestion des joueurs."""
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Gestion des joueurs")
        fenetre.geometry("600x400")
        fenetre.transient(self.root)
        
        # Liste des joueurs
        tk.Label(fenetre, text="Liste des joueurs", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_liste = tk.Frame(fenetre)
        frame_liste.pack(fill=tk.BOTH, expand=True, padx=10)
        
        scrollbar = tk.Scrollbar(frame_liste)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame_liste, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Charger les joueurs
        joueurs = db.get_tous_les_joueurs()
        for joueur_id, nom in joueurs:
            listbox.insert(tk.END, nom)
        
        # Frame pour les actions
        actions_frame = tk.Frame(fenetre)
        actions_frame.pack(pady=10)
        
        def ajouter_joueur():
            nom = simpledialog.askstring("Ajouter un joueur", "Nom du joueur :")
            if nom and nom.strip():
                if db.ajouter_joueur(nom.strip()):
                    listbox.insert(tk.END, nom.strip())
                    messagebox.showinfo("Succès", "Joueur ajouté !")
                else:
                    messagebox.showerror("Erreur", "Ce nom existe déjà.")
        
        def voir_stats():
            selection = listbox.curselection()
            if selection:
                nom = listbox.get(selection[0])
                joueur_id = db.get_joueur_id(nom)
                if joueur_id:
                    self.afficher_stats_joueur(joueur_id)
            else:
                messagebox.showinfo("Info", "Sélectionnez un joueur.")
        
        def supprimer_joueur():
            # Note: Fonctionnalité de suppression à implémenter avec prudence
            pass
        
        tk.Button(actions_frame, text="Ajouter joueur", command=ajouter_joueur, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Voir statistiques", command=voir_stats, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Fermer", command=fenetre.destroy, bg="#FF4444", fg="white").pack(side=tk.LEFT, padx=5)
    
    def afficher_stats_joueur(self, joueur_id):
        """Affiche les statistiques d'un joueur."""
        stats = db.get_statistiques_joueur(joueur_id)
        if not stats:
            messagebox.showerror("Erreur", "Impossible de récupérer les statistiques.")
            return
        
        fenetre = tk.Toplevel(self.root)
        fenetre.title(f"Statistiques - {stats['nom']}")
        fenetre.geometry("500x400")
        
        tk.Label(fenetre, text=f"Statistiques de {stats['nom']}", font=("Arial", 16, "bold")).pack(pady=10)
        
        frame = tk.Frame(fenetre)
        frame.pack(padx=20, pady=10)
        
        stats_data = [
            ("Total parties", stats['total_parties']),
            ("Victoires", stats['victoires']),
            ("Défaites", stats['defaites']),
            ("Abandons", stats['abandons']),
            ("Total captures", stats['total_captures']),
            ("Total promotions", stats['total_promotions']),
            ("Temps total (sec)", stats['total_temps'])
        ]
        
        if stats['total_parties'] > 0:
            taux = stats['victoires'] / stats['total_parties'] * 100
            stats_data.append(("Taux de victoire", f"{taux:.1f}%"))
        
        for label, valeur in stats_data:
            frame_row = tk.Frame(frame)
            frame_row.pack(fill=tk.X, pady=2)
            tk.Label(frame_row, text=f"{label}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame_row, text=str(valeur), width=15, anchor=tk.W).pack(side=tk.LEFT)
        
        # Voir l'historique
        tk.Button(
            fenetre,
            text="Voir l'historique des parties",
            command=lambda: self.afficher_historique_joueur(joueur_id)
        ).pack(pady=10)
    
    def afficher_historique_joueur(self, joueur_id):
        """Affiche l'historique des parties d'un joueur."""
        historique = db.get_historique_joueur(joueur_id)
        if not historique:
            messagebox.showinfo("Historique", "Aucune partie trouvée.")
            return
        
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Historique des parties")
        fenetre.geometry("800x400")
        
        # Créer un tableau
        tree = ttk.Treeview(fenetre, columns=("date", "blanc", "noir", "gagnant", "statut", "duree"), show="headings")
        tree.heading("date", text="Date")
        tree.heading("blanc", text="Blanc")
        tree.heading("noir", text="Noir")
        tree.heading("gagnant", text="Gagnant")
        tree.heading("statut", text="Statut")
        tree.heading("duree", text="Durée (s)")
        
        tree.column("date", width=150)
        tree.column("blanc", width=100)
        tree.column("noir", width=100)
        tree.column("gagnant", width=80)
        tree.column("statut", width=100)
        tree.column("duree", width=70)
        
        scrollbar = ttk.Scrollbar(fenetre, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        for partie in historique:
            gagnant_nom = partie['gagnant'] if partie['gagnant'] else "Nul"
            if partie['gagnant'] == 'blanc':
                gagnant_nom = partie['joueur_blanc']
            elif partie['gagnant'] == 'noir':
                gagnant_nom = partie['joueur_noir']
            
            tree.insert("", tk.END, values=(
                partie['date_heure'].strftime("%d/%m/%Y %H:%M"),
                partie['joueur_blanc'],
                partie['joueur_noir'],
                gagnant_nom,
                partie['statut'],
                partie['duree']
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def afficher_stats_globales(self):
        """Affiche les statistiques globales."""
        stats = db.get_stats_globales()
        if not stats:
            messagebox.showinfo("Stats", "Aucune statistique disponible.")
            return
        
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Statistiques globales")
        fenetre.geometry("400x300")
        
        tk.Label(fenetre, text="Statistiques globales", font=("Arial", 16, "bold")).pack(pady=10)
        
        frame = tk.Frame(fenetre)
        frame.pack(padx=20, pady=10)
        
        stats_data = [
            ("Total parties", stats['total_parties']),
            ("Durée moyenne (s)", f"{stats['duree_moyenne']:.1f}" if stats['duree_moyenne'] else "N/A"),
            ("Captures moyennes", f"{stats['captures_moyennes']:.1f}" if stats['captures_moyennes'] else "N/A"),
            ("Promotions moyennes", f"{stats['promotions_moyennes']:.1f}" if stats['promotions_moyennes'] else "N/A")
        ]
        
        for label, valeur in stats_data:
            frame_row = tk.Frame(frame)
            frame_row.pack(fill=tk.X, pady=2)
            tk.Label(frame_row, text=f"{label}:", width=25, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame_row, text=str(valeur), width=15, anchor=tk.W).pack(side=tk.LEFT)
    
    def afficher_classement(self):
        """Affiche le classement des joueurs."""
        classement = db.get_classement()
        if not classement:
            messagebox.showinfo("Classement", "Aucun joueur classé.")
            return
        
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Classement général")
        fenetre.geometry("600x400")
        
        tk.Label(fenetre, text="Classement général", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Créer un tableau
        tree = ttk.Treeview(fenetre, columns=("rang", "nom", "parties", "victoires", "defaites", "taux"), show="headings")
        tree.heading("rang", text="#")
        tree.heading("nom", text="Joueur")
        tree.heading("parties", text="Parties")
        tree.heading("victoires", text="Victoires")
        tree.heading("defaites", text="Défaites")
        tree.heading("taux", text="Taux %")
        
        tree.column("rang", width=40)
        tree.column("nom", width=150)
        tree.column("parties", width=80)
        tree.column("victoires", width=80)
        tree.column("defaites", width=80)
        tree.column("taux", width=80)
        
        scrollbar = ttk.Scrollbar(fenetre, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        for i, joueur in enumerate(classement, 1):
            tree.insert("", tk.END, values=(
                i,
                joueur['nom'],
                joueur['total_parties'],
                joueur['victoires'],
                joueur['defaites'],
                joueur['taux_victoire']
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def run(self):
        """Lance l'application."""
        self.root.mainloop()

if __name__ == "__main__":
    jeu = JeuDames()
    jeu.run()