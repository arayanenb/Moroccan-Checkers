# Jeu de Dames Marocain (Moroccan Checkers) 🏆

A fully functional Moroccan Checkers (Dames Marocaines) game built in Python. It features a graphical user interface (Tkinter), an AI opponent with multiple difficulty levels, and a MySQL database to track players, statistics, and game history.

## 🎮 Features

*   **Two Game Modes:** Player vs Player (PvP) and Player vs AI (PvE).
*   **4 AI Difficulty Levels:** 
    *   *Débutant (Beginner):* Plays randomly.
    *   *Intermédiaire (Intermediate):* Uses a basic heuristic to capture pieces.
    *   *Avancé (Advanced):* Uses Minimax algorithm (depth 2).
    *   *Expert:* Uses Alpha-Beta pruning algorithm (depth 3).
*   **Moroccan Checkers Rules:** Includes the "Koul" (forced captures), "Neffakh" (penalty for refusing a capture), and "Sultan" (king promotion).
*   **Graphical Interface:** Built with Tkinter for an intuitive and visual playing experience.
*   **Database Integration:** Stores player profiles, match history, leaderboards, and detailed statistics (wins, losses, captures, promotions, playtime).
*   **Console Fallback:** If the GUI fails to load, the game automatically falls back to a console-based interface.

## ⚙️ Prerequisites

Before running the game, ensure you have:
1. **Python 3.8+** installed.
2. **MySQL Server** installed and running locally.

## 🚀 Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/gamedame.git
cd gamedame