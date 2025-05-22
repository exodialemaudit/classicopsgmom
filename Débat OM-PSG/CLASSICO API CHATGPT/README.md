# Football Debate: OM vs PSG 🏆

Une application interactive qui simule des débats passionnés entre supporters de l'OM et du PSG, alimentés par l'IA.

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd projetinfoL1-main
```

2. Créez un environnement virtuel (recommandé) :
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🎮 Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. L'interface web s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:5000`

## 🎯 Fonctionnalités

### Formats de débat disponibles :
- **Duel des Géants** : Rounds punchy chronométrés
- **Choc Ultime** : Mode clash avec provocations
- **Analytique 360°** : Analyse factuelle et tactique
- **Happy Hour** : Débat décontracté et humoristique

### Personnalités disponibles :
- Standard
- Passionné
- Analytique
- Humoristique
- Provocateur

## ⚙️ Configuration

Dans l'interface web, vous pouvez configurer :
- Le sujet du débat
- Le format de débat
- Le nombre de tours
- La personnalité des supporters OM et PSG

## 🛠️ Structure du projet

```
projetinfoL1-main/
├── frontend/
│   └── app.py          # Interface Streamlit
├── football_debate/    # Moteur de débat
├── debates/           # Dossier pour les débats sauvegardés
├── main.py            # Point d'entrée de l'application
└── requirements.txt   # Dépendances Python
```

