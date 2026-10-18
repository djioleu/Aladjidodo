# Continuer cette session sur votre PC Windows

Objectif : reprendre **cette même conversation** sur votre ordinateur, pour que Claude
puisse piloter Gemini dans votre Chrome et mettre les images dans le livre tout seul.

## 1. Installer les outils (une seule fois)

Ouvrez **PowerShell** (touche Windows, tapez « PowerShell », Entrée) et collez :

```powershell
winget install -e --id Git.Git
winget install -e --id Python.Python.3.12
irm https://claude.ai/install.ps1 | iex
```

Puis **fermez PowerShell et rouvrez-le** pour que les nouveaux programmes soient reconnus.

## 2. Récupérer le projet et ouvrir la session

Dans le nouveau PowerShell, collez :

```powershell
cd $HOME\Documents
git clone https://github.com/djioleu/aladjidodo.git Aladjidodo
cd Aladjidodo
git checkout ccr-9f42c93c-ph2iyk
py -m pip install reportlab pillow
claude --teleport session_01BtCTRm9KE4XhrUdWboPPEE
```

- Si GitHub demande de vous connecter, une fenêtre s'ouvre : connectez-vous.
- Au premier lancement, `claude` vous demande de vous connecter à votre compte Claude.
- Si `--teleport` avec le numéro ne marche pas, tapez seulement `claude --teleport`
  et choisissez la session « TikTok video » dans la liste.

## 3. Relier Chrome

Dans Claude (dans PowerShell), tapez :

```
/chrome
```

et suivez les indications pour connecter l'extension Claude in Chrome.

## 4. Lancer le travail

Ouvrez gemini.google.com dans Chrome (connecté à votre compte Google), puis écrivez à Claude :

```
Lis livre-coloriage-racines/INSTRUCTIONS-GEMINI.md. Utilise Chrome pour générer
toutes les images dans Gemini, range-les dans livre-coloriage-racines/images/
(01.png à 30.png et couverture.png), vérifie-les, puis lance
py livre-coloriage-racines/generer.py tout
```
