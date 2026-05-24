# Construction Windows avec PyInstaller

Depuis le dossier `plast_alum_manager` :

```powershell
python -m pip install -r requirements.txt
build_windows.bat
```

L'exécutable sera créé dans :

```text
dist/TheCrownVibe - Gestion des Paiements Fournisseurs/TheCrownVibe - Gestion des Paiements Fournisseurs.exe
```

Le script détecte `main.py` comme fichier d'entrée, ajoute les dossiers `app/assets`, `app/styles`, `app/translations` et le fichier `config.py` au bundle PyInstaller. Si `app/assets/icons/app.ico` existe, il sera utilisé comme icône de l'exécutable.

Les icônes sources de l'application sont dans :

```text
app/assets/logo.png
app/assets/icons/app.png
app/assets/icons/app.ico
```

Le fichier `.ico` contient les tailles Windows 16, 32, 48, 64, 128 et 256 px.

La base de données locale est créée au premier lancement dans :

```text
dist/TheCrownVibe - Gestion des Paiements Fournisseurs/data/database.sqlite
```

Les sauvegardes, exports, uploads et logos personnalisés restent dans le dossier `data` à côté de l'exécutable.

## Raccourci bureau

Après le build :

```powershell
python create_desktop_shortcut.py
```

Le raccourci créé sur le bureau s'appelle :

```text
TheCrownVibe - Gestion des Paiements
```

Pour vérifier sans créer le raccourci :

```powershell
python create_desktop_shortcut.py --dry-run
```

Si Windows affiche encore l'ancienne icône après un rebuild ou une recréation du raccourci, exécutez :

```powershell
powershell -ExecutionPolicy Bypass -File .\refresh_icon_cache.ps1
```

## Build avancé avec fichier spec

Un fichier `the_crown_vibe_windows.spec` est fourni pour les builds PyInstaller avancés :

```powershell
python -m PyInstaller --noconfirm --clean the_crown_vibe_windows.spec
```
