# Pokémon Image Scraper

Ce projet est un script Python qui télécharge automatiquement les images officielles des Pokémon en utilisant l'API PokeAPI.

## Fonctionnalités

- Téléchargement des illustrations officielles des Pokémon
- Traitement par lots de 20 Pokémon pour éviter la surcharge
- Sauvegarde automatique de la progression
- Reprise possible en cas d'interruption
- Évite les téléchargements en double
- Nommage cohérent des fichiers avec ID et nom du Pokémon

## Prérequis

- Python 3.x
- Les packages Python suivants :
  - requests
  - os
  - time

## Installation

1. Clonez ce repository :
```bash
git clone https://github.com/Whoistomiki/scraping-pokemon-aws.git
cd scraping-pokemon-aws
```

2. Installez les dépendances requises :
```bash
pip install requests
```

## Utilisation

1. Exécutez le script :

```bash
python scraping.py
```

Le script va :
- Créer un dossier `pokemon_images` s'il n'existe pas
- Télécharger 20 images de Pokémon à chaque exécution
- Sauvegarder la progression dans `progress.txt`
- Afficher le statut du téléchargement en cours

2. Pour continuer le téléchargement, relancez simplement le script. Il reprendra là où il s'était arrêté.

## Architecture

Le projet est volontairement simple et contient les composants suivants :

- `scraping.py` : script Python qui appelle l'API PokeAPI, télécharge les images et enregistre la progression.
- `pokemon_images/` : dossier local où sont stockées les images téléchargées.
- `progress.txt` : fichier texte contenant l'index du dernier Pokémon traité (permet la reprise par lots).

Un schéma Draw.io (`poke_architecture.drawio.png`) a été ajouté pour visualiser l'architecture :

- scraping.py -> PokeAPI : récupère la liste et les détails des Pokémon
- scraping.py -> pokemon_images/ : enregistre les fichiers images
- scraping.py -> progress.txt : lit/écrit l'index de progression

## Choix techniques

1. Source des données

  - PokeAPI (https://pokeapi.co/) a été choisie car elle fournit une API publique stable et bien documentée. Elle évite le scraping direct d'un site web (ex. Bulbapedia) qui peut être protégé contre les bots et dont l'HTML peut changer fréquemment.

2. Traitement par lots

  - Le script traite 20 Pokémon par exécution (paramètre `batch_size`) pour limiter la charge et faciliter la reprise en cas d'interruption.

3. Gestion des erreurs

  - Les requêtes HTTP utilisent `requests` avec gestion d'exceptions (try/except) pour capturer les erreurs réseau et HTTP.
  - En cas d'erreur pendant le traitement d'un Pokémon individuel, le script logge l'erreur et passe au suivant (pas d'arrêt global).
  - La progression est sauvegardée (`progress.txt`) après chaque lot pour garantir que le prochain lancement repartira du bon index.

4. Respect de l'API

  - Une pause de 0.5 seconde est insérée entre chaque téléchargement pour rester raisonnable vis-à-vis de l'API publique.

5. Nom des fichiers

  - Les fichiers sont nommés avec l'ID pokédex (zfill(3)) et le nom en minuscule : `001_bulbasaur.png`. Cela facilite le tri et la réutilisation.

6. Extensibilité

  - Le design est simple : il est facile d'ajouter des options (taille de lot en argument, parallelisme, stockage cloud) sans modifier l'architecture de base.
