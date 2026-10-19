# Quand papa et maman étaient petits — l'imagier à colorier

50 objets de l'enfance africaine des parents (années 1990-2010), un par page, avec
leur nom en français et en anglais et une question que l'enfant pose à papa ou maman.

- `livre.json` : titres, textes de couverture et les 50 pages (nom FR, nom EN, question, description du dessin)
- `PROMPTS.md` : un prompt par objet à coller dans le générateur d'images
- `images/` : déposer `01.png` à `50.png` et `couverture.png`

Générer les PDF Amazon (108 pages, 8,5 x 11 pouces) :

```
python3 ../../livre-coloriage-racines/generer.py tout .
```

Règles pour les images : un seul objet, grand et centré, sans texte, sans logo ni marque.
