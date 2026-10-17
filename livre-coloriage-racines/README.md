# L'Afrique de mes racines — livre de coloriage pour Amazon KDP

Livre de coloriage bilingue français-anglais (4-8 ans) : 30 dessins sur l'Afrique,
vendu sur Amazon à la diaspora et au public occidental.

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `livre.json` | Titre, nom d'auteur et les 30 pages (phrase FR, phrase EN, description du dessin) |
| `PROMPTS.md` | Les textes à coller dans un générateur d'images, page par page |
| `FICHE-AMAZON.md` | Titre, description, mots-clés, catégories et prix à copier dans KDP |
| `generer.py` | Fabrique les PDF prêts pour Amazon |
| `images/` | Vos dessins : `01.png` à `30.png` + `couverture.png` |
| `sortie/` | Les PDF générés (`interieur.pdf`, `couverture.pdf`) |

## Les étapes

1. **Créer les comptes (gratuit)**
   - Compte Amazon KDP : https://kdp.amazon.com
   - Compte Payoneer ou Wise pour recevoir l'argent (le Cameroun n'est pas payé
     directement par Amazon). Utilisez le **même nom** que sur votre pièce d'identité partout.
   - Remplissez le questionnaire fiscal dans KDP.

2. **Choisir votre nom d'auteur** et le mettre dans `livre.json` et `FICHE-AMAZON.md`.

3. **Créer les 31 images** avec les textes de `PROMPTS.md`, et les ranger dans `images/`.
   Vérifiez chaque dessin : traits fermés, pas de gris, pas de texte, mains et visages
   corrects. C'est l'étape la plus importante : un livre aux dessins ratés reçoit de
   mauvais avis.

4. **Générer les PDF** :
   ```
   python3 generer.py tout
   ```
   Il faut Python 3 avec `reportlab` et `Pillow` (`pip install reportlab pillow`).
   Si un nom de fichier finit par `-BROUILLON`, c'est qu'il manque des images.

5. **Publier sur KDP** en suivant `FICHE-AMAZON.md`, puis **commander une copie
   d'auteur** pour vérifier l'impression avant de faire de la publicité.

6. **Faire connaître le livre** : vidéos TikTok de coloriage en accéléré, groupes
   Facebook de la diaspora, parents et écoles. Puis créer d'autres livres de la même
   série (contes, animaux, métiers…) en dupliquant ce dossier.
