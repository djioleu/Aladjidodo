#!/usr/bin/env python3
"""Génère les fichiers Amazon KDP du livre de coloriage décrit dans livre.json.

Usage :
    python3 generer.py prompts      -> PROMPTS.md (textes à coller dans un générateur d'images)
    python3 generer.py interieur    -> sortie/interieur.pdf
    python3 generer.py couverture   -> sortie/couverture.pdf
    python3 generer.py tout         -> les trois

Les illustrations se placent dans images/ : 01.png, 02.png, ... (ou .jpg),
et images/couverture.png pour l'illustration (en couleur) de la couverture.
Une image manquante est remplacée par un cadre « à ajouter » et le PDF est
alors nommé *-BROUILLON.pdf : ne jamais envoyer un brouillon à Amazon.

Format : broché 8,5 x 11 pouces (21,59 x 27,94 cm), intérieur noir et blanc
sans fond perdu, papier blanc. Chaque dessin est sur une page de droite avec
le dos blanc, pour que les feutres ne traversent pas sur le dessin suivant.
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, black, white
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ICI = Path(__file__).resolve().parent
IMAGES = ICI / "images"
SORTIE = ICI / "sortie"

LARGEUR, HAUTEUR = 8.5 * inch, 11 * inch
MARGE = 0.5 * inch          # KDP exige au moins 0,375" côté reliure et 0,25" ailleurs
FOND_PERDU = 0.125 * inch   # bleed de la couverture
EPAISSEUR_PAGE = 0.002252   # pouces par page, papier blanc noir et blanc
DPI = 300

pdfmetrics.registerFont(TTFont("Titre", str(ICI / "polices" / "LuckiestGuy-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Texte", str(ICI / "polices" / "PatrickHand-Regular.ttf")))

GRIS = Color(0.35, 0.35, 0.35)
# Palette de la couverture : ocre, terre, vert, indigo
OCRE = Color(0.96, 0.66, 0.16)
TERRE = Color(0.71, 0.29, 0.13)
VERT = Color(0.10, 0.48, 0.32)
INDIGO = Color(0.15, 0.17, 0.42)
CREME = Color(1.0, 0.96, 0.86)


def charger_livre():
    return json.loads((ICI / "livre.json").read_text(encoding="utf-8"))


def trouver_image(nom):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        chemin = IMAGES / f"{nom}{ext}"
        if chemin.exists():
            return chemin
    return None


def texte_centre(c, police, taille, y, texte, couleur=black, largeur_max=None, x_centre=None):
    """Écrit une ligne centrée, en réduisant la taille si elle dépasse largeur_max."""
    largeur_max = largeur_max or (LARGEUR - 2 * MARGE)
    while pdfmetrics.stringWidth(texte, police, taille) > largeur_max and taille > 8:
        taille -= 1
    c.setFillColor(couleur)
    c.setFont(police, taille)
    c.drawCentredString(x_centre if x_centre is not None else LARGEUR / 2, y, texte)


def lignes(texte, police, taille, largeur):
    """Découpe un paragraphe en lignes qui tiennent dans la largeur donnée."""
    resultat, ligne = [], ""
    for mot in texte.split():
        essai = f"{ligne} {mot}".strip()
        if pdfmetrics.stringWidth(essai, police, taille) <= largeur:
            ligne = essai
        else:
            resultat.append(ligne)
            ligne = mot
    if ligne:
        resultat.append(ligne)
    return resultat


def preparer_dessin(chemin, largeur_pts, hauteur_pts):
    """Agrandit le dessin à 300 DPI puis le passe en noir et blanc pur, pour des traits nets."""
    img = Image.open(chemin).convert("L")
    echelle = min(largeur_pts / img.width, hauteur_pts / img.height)
    l_pts, h_pts = img.width * echelle, img.height * echelle
    l_px, h_px = round(l_pts / 72 * DPI), round(h_pts / 72 * DPI)
    img = img.resize((l_px, h_px), Image.LANCZOS)
    img = img.point(lambda p: 255 if p > 160 else 0, mode="1")
    tampon = SORTIE / "tmp" / f"{chemin.stem}.png"
    tampon.parent.mkdir(parents=True, exist_ok=True)
    img.save(tampon)
    return tampon, l_pts, h_pts


def cadre_manquant(c, x, y, l, h, message):
    c.setStrokeColor(GRIS)
    c.setDash(8, 6)
    c.setLineWidth(2)
    c.roundRect(x, y, l, h, 18)
    c.setDash()
    texte_centre(c, "Texte", 28, y + h / 2, message, GRIS, x_centre=x + l / 2)


# ---------------------------------------------------------------- PROMPTS

def generer_prompts(livre):
    out = [
        f"# Prompts des illustrations — {livre['titre']}",
        "",
        "Copiez chaque prompt dans un générateur d'images dont les conditions autorisent",
        "l'usage commercial (ChatGPT, Ideogram…), choisissez le format **portrait 3:4** si",
        "possible, puis enregistrez l'image dans `images/` sous le nom indiqué (`01.png`…).",
        "",
        "Vérifiez chaque dessin : traits fermés, pas de gris, pas de texte, mains et",
        "visages corrects. Régénérez autant de fois que nécessaire.",
        "",
        "## Couverture (en couleur) → `images/couverture.png`",
        "",
        "```",
        "colorful joyful children's book cover illustration, a smiling African girl and boy "
        "hugging a baobab tree in the savanna, a lion, an elephant, a giraffe and a parrot around "
        "them, bold bright colors, wax fabric patterns, cute cartoon style, square format, no text",
        "```",
        "",
    ]
    for i, page in enumerate(livre["pages"], 1):
        out += [
            f"## {i:02d} — {page['fr']} → `images/{i:02d}.png`",
            "",
            "```",
            f"{page['prompt']}, {livre['style_prompt']}",
            "```",
            "",
        ]
    (ICI / "PROMPTS.md").write_text("\n".join(out), encoding="utf-8")
    print("PROMPTS.md créé")


# --------------------------------------------------------------- INTÉRIEUR

def page_titre(c, livre):
    texte_centre(c, "Titre", 46, HAUTEUR * 0.62, livre["titre"])
    texte_centre(c, "Titre", 28, HAUTEUR * 0.62 - 48, livre["titre_en"], GRIS)
    y = HAUTEUR * 0.45
    for ligne in lignes(livre["sous_titre"], "Texte", 24, LARGEUR - 3 * MARGE):
        texte_centre(c, "Texte", 24, y, ligne)
        y -= 30
    texte_centre(c, "Texte", 22, HAUTEUR * 0.2, livre["auteur"])
    c.showPage()


def page_copyright(c, livre):
    y = 2.2 * inch
    for ligne in (
        f"{livre['titre']} — {livre['titre_en']}",
        f"© {livre['annee']} {livre['auteur']}. Tous droits réservés. All rights reserved.",
        "Aucune partie de ce livre ne peut être reproduite sans autorisation,",
        "sauf pour un usage personnel de coloriage.",
        "Illustrations créées avec l'aide de l'intelligence artificielle.",
    ):
        texte_centre(c, "Texte", 13, y, ligne, GRIS)
        y -= 18
    c.showPage()


def page_appartient(c):
    texte_centre(c, "Titre", 40, HAUTEUR * 0.6, "Ce livre appartient à")
    texte_centre(c, "Titre", 28, HAUTEUR * 0.6 - 42, "This book belongs to", GRIS)
    c.setLineWidth(2)
    c.line(1.5 * inch, HAUTEUR * 0.42, LARGEUR - 1.5 * inch, HAUTEUR * 0.42)
    c.showPage()


def page_essai_couleurs(c):
    texte_centre(c, "Titre", 36, HAUTEUR - 1.6 * inch, "Essaie tes couleurs ici !")
    texte_centre(c, "Titre", 24, HAUTEUR - 1.6 * inch - 36, "Test your colors here!", GRIS)
    c.setLineWidth(2)
    cote, ecart = 1.1 * inch, 0.35 * inch
    x0 = (LARGEUR - (5 * cote + 4 * ecart)) / 2
    for ligne in range(4):
        for col in range(5):
            x = x0 + col * (cote + ecart)
            y = HAUTEUR - 3.4 * inch - ligne * (cote + ecart)
            if (ligne + col) % 2:
                c.circle(x + cote / 2, y - cote / 2, cote / 2)
            else:
                c.roundRect(x, y - cote, cote, cote, 12)
    c.showPage()


def page_dessin(c, numero, page):
    zone_texte = 1.5 * inch
    x, y = MARGE, MARGE + zone_texte
    l, h = LARGEUR - 2 * MARGE, HAUTEUR - 2 * MARGE - zone_texte
    chemin = trouver_image(f"{numero:02d}")
    if chemin:
        tampon, l_img, h_img = preparer_dessin(chemin, l, h)
        c.drawImage(str(tampon), x + (l - l_img) / 2, y + (h - h_img) / 2, l_img, h_img)
    else:
        cadre_manquant(c, x, y, l, h, f"Dessin {numero:02d} à ajouter")
    texte_centre(c, "Texte", 34, MARGE + 0.85 * inch, page["fr"])
    texte_centre(c, "Texte", 24, MARGE + 0.35 * inch, page["en"], GRIS)
    c.showPage()
    return chemin is not None


def page_merci(c):
    texte_centre(c, "Titre", 44, HAUTEUR * 0.66, "Bravo, artiste !")
    texte_centre(c, "Titre", 28, HAUTEUR * 0.66 - 44, "Well done, artist!", GRIS)
    y = HAUTEUR * 0.48
    for texte, couleur in (
        ("Ce livre vous a plu ? Un petit avis sur Amazon", black),
        ("aide énormément un auteur indépendant. Merci !", black),
        ("", black),
        ("Did you enjoy this book? A short review on Amazon", GRIS),
        ("helps an independent author a lot. Thank you!", GRIS),
    ):
        texte_centre(c, "Texte", 22, y, texte, couleur)
        y -= 30
    c.showPage()


def page_blanche(c):
    c.showPage()


def generer_interieur(livre):
    SORTIE.mkdir(exist_ok=True)
    temp = SORTIE / "interieur-en-cours.pdf"
    c = Canvas(str(temp), pagesize=(LARGEUR, HAUTEUR))
    c.setTitle(livre["titre"])
    c.setAuthor(livre["auteur"])

    page_titre(c, livre)
    page_copyright(c, livre)
    page_appartient(c)
    page_blanche(c)
    page_essai_couleurs(c)
    page_blanche(c)
    manquants = []
    for i, page in enumerate(livre["pages"], 1):
        if not page_dessin(c, i, page):
            manquants.append(f"{i:02d}")
        page_blanche(c)
    page_merci(c)
    page_blanche(c)
    nb_pages = c.getPageNumber() - 1
    c.save()

    nom = "interieur-BROUILLON.pdf" if manquants else "interieur.pdf"
    temp.replace(SORTIE / nom)
    print(f"sortie/{nom} : {nb_pages} pages")
    if manquants:
        print(f"  Dessins manquants ({len(manquants)}) : {', '.join(manquants)}")
    return nb_pages


# -------------------------------------------------------------- COUVERTURE

def motif_wax(c, x, y, l, h, graine=7):
    """Motif géométrique inspiré du wax, en couleurs, sur un rectangle."""
    rnd = random.Random(graine)
    c.saveState()
    chemin = c.beginPath()
    chemin.rect(x, y, l, h)
    c.clipPath(chemin, stroke=0)
    c.setFillColor(TERRE)
    c.rect(x, y, l, h, stroke=0, fill=1)
    pas = 0.9 * inch
    couleurs = [OCRE, VERT, INDIGO, CREME]
    for i in range(int(l // pas) + 2):
        for j in range(int(h // pas) + 2):
            cx, cy = x + i * pas, y + j * pas + (pas / 2 if i % 2 else 0)
            c.setFillColor(couleurs[(i + j) % 4])
            forme = rnd.choice(["cercle", "losange", "anneau"])
            if forme == "cercle":
                c.circle(cx, cy, pas * 0.3, stroke=0, fill=1)
            elif forme == "losange":
                p = c.beginPath()
                p.moveTo(cx, cy + pas * 0.35)
                p.lineTo(cx + pas * 0.25, cy)
                p.lineTo(cx, cy - pas * 0.35)
                p.lineTo(cx - pas * 0.25, cy)
                p.close()
                c.drawPath(p, stroke=0, fill=1)
            else:
                c.setStrokeColor(couleurs[(i + j + 1) % 4])
                c.setLineWidth(5)
                c.circle(cx, cy, pas * 0.25, stroke=1, fill=0)
    c.restoreState()


def bandeau(c, x, y, l, h, couleur=CREME):
    c.setFillColor(couleur)
    c.roundRect(x, y, l, h, 20, stroke=0, fill=1)


def generer_couverture(livre, nb_pages):
    dos = nb_pages * EPAISSEUR_PAGE * inch
    total_l = 2 * LARGEUR + dos + 2 * FOND_PERDU
    total_h = HAUTEUR + 2 * FOND_PERDU
    securite = FOND_PERDU + 0.25 * inch
    SORTIE.mkdir(exist_ok=True)
    temp = SORTIE / "couverture-en-cours.pdf"
    c = Canvas(str(temp), pagesize=(total_l, total_h))
    c.setTitle(f"{livre['titre']} — couverture")

    motif_wax(c, 0, 0, total_l, total_h)

    # --- 1re de couverture (à droite)
    x0 = FOND_PERDU + LARGEUR + dos
    cx = x0 + LARGEUR / 2
    marge_int = 0.55 * inch
    l_bandeau = LARGEUR - 2 * marge_int
    bandeau(c, x0 + marge_int, total_h - securite - 2.55 * inch, l_bandeau, 2.25 * inch)
    texte_centre(c, "Titre", 50, total_h - securite - 1.0 * inch, livre["titre"], TERRE,
                 l_bandeau - 30, cx)
    texte_centre(c, "Titre", 30, total_h - securite - 1.55 * inch, livre["titre_en"], INDIGO,
                 l_bandeau - 30, cx)
    texte_centre(c, "Texte", 22, total_h - securite - 2.15 * inch,
                 "Livre de coloriage bilingue  •  Bilingual coloring book", black,
                 l_bandeau - 30, cx)

    zone_l, zone_h = l_bandeau, 5.6 * inch
    zone_x, zone_y = x0 + marge_int, securite + 1.45 * inch
    illustration = trouver_image("couverture")
    if illustration:
        img = Image.open(illustration).convert("RGB")
        echelle = min(zone_l / img.width, zone_h / img.height)
        l_img, h_img = img.width * echelle, img.height * echelle
        bandeau(c, zone_x + (zone_l - l_img) / 2 - 10, zone_y + (zone_h - h_img) / 2 - 10,
                l_img + 20, h_img + 20, white)
        c.drawImage(str(illustration), zone_x + (zone_l - l_img) / 2, zone_y + (zone_h - h_img) / 2,
                    l_img, h_img)
    else:
        bandeau(c, zone_x, zone_y, zone_l, zone_h, white)
        cadre_manquant(c, zone_x + 15, zone_y + 15, zone_l - 30, zone_h - 30,
                       "Illustration de couverture")

    bandeau(c, x0 + marge_int, securite + 0.1 * inch, l_bandeau, 1.1 * inch)
    texte_centre(c, "Titre", 24, securite + 0.75 * inch, "4 - 8 ans  •  4 - 8 years", VERT,
                 l_bandeau - 30, cx)
    texte_centre(c, "Texte", 20, securite + 0.3 * inch, livre["auteur"], black, l_bandeau - 30, cx)

    # --- 4e de couverture (à gauche) ; Amazon imprime le code-barres en bas à droite
    bx = FOND_PERDU + marge_int
    bl = LARGEUR - 2 * marge_int
    haut = total_h - securite - 0.2 * inch
    bas = securite + 1.7 * inch
    bandeau(c, bx, bas, bl, haut - bas)
    y = haut - 0.7 * inch
    texte_centre(c, "Titre", 30, y, "Colorie l'Afrique !", TERRE, bl - 40, bx + bl / 2)
    y -= 0.6 * inch
    paragraphe_fr = (
        "Les lions de la savane, le marché plein de fruits, le pagne wax de maman, le taxi "
        "jaune de la ville et les contes de papi sous la lune : 30 grands dessins pour "
        "découvrir et aimer l'Afrique, avec une phrase simple en français et en anglais "
        "sur chaque page."
    )
    paragraphe_en = (
        "Lions of the savanna, a busy fruit market, mom's wax fabric, the yellow city taxi "
        "and grandpa's stories under the moon: 30 big drawings to discover and love Africa, "
        "with a simple sentence in French and English on every page."
    )
    for para, couleur in ((paragraphe_fr, black), (paragraphe_en, GRIS)):
        for ligne in lignes(para, "Texte", 20, bl - 0.8 * inch):
            c.setFillColor(couleur)
            c.setFont("Texte", 20)
            c.drawString(bx + 0.4 * inch, y, ligne)
            y -= 26
        y -= 18
    for puce in (
        "• 30 dessins uniques, un seul par page",
        "• Dos des pages blanc : pas de feutre qui traverse",
        "• Grand format 21,6 x 27,9 cm",
    ):
        c.setFillColor(VERT)
        c.setFont("Texte", 20)
        c.drawString(bx + 0.4 * inch, y, puce)
        y -= 28

    c.save()
    nom = "couverture.pdf" if illustration else "couverture-BROUILLON.pdf"
    temp.replace(SORTIE / nom)
    print(f"sortie/{nom} : {total_l / inch:.3f} x {total_h / inch:.3f} pouces "
          f"(dos {dos / inch:.3f} pouces, {nb_pages} pages)")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "tout"
    livre = charger_livre()
    if action in ("prompts", "tout"):
        generer_prompts(livre)
    if action in ("interieur", "couverture", "tout"):
        nb_pages = generer_interieur(livre)
        if action != "interieur":
            generer_couverture(livre, nb_pages)
    if action not in ("prompts", "interieur", "couverture", "tout"):
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
