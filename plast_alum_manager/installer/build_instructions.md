# Construction Windows avec PyInstaller

Depuis le dossier `plast_alum_manager` :

```powershell
python -m pip install -r requirements.txt
build_windows.bat
```

L'exécutable sera créé dans :

```text
dist/PLAST ALUM - Gestion des Paiements Fournisseurs/PLAST ALUM - Gestion des Paiements Fournisseurs.exe
```

Le script détecte `main.py` comme fichier d'entrée, ajoute les dossiers `app/assets`, `app/styles`, `app/translations` et le fichier `config.py` au bundle PyInstaller. Si `app/assets/icons/app.ico` existe, il sera utilisé comme icône de l'exécutable.

La base de données locale est créée au premier lancement dans :

```text
dist/PLAST ALUM - Gestion des Paiements Fournisseurs/data/database.sqlite
```

Les sauvegardes, exports, uploads et logos personnalisés restent dans le dossier `data` à côté de l'exécutable.

## Raccourci bureau

Après le build :

```powershell
python create_desktop_shortcut.py
```

Le raccourci créé sur le bureau s'appelle :

```text
PLAST ALUM - Gestion des Paiements
```

Pour vérifier sans créer le raccourci :

```powershell
python create_desktop_shortcut.py --dry-run
```

## Build avancé avec fichier spec

Un fichier `plast_alum_windows.spec` est fourni pour les builds PyInstaller avancés :

```powershell
python -m PyInstaller --noconfirm --clean plast_alum_windows.spec
```
