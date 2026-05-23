# PLAST ALUM - Gestion des Paiements Fournisseurs

Application desktop interne pour gérer les fournisseurs, les factures, les délais de paiement, les alertes, les rapports et les exports Excel/PDF de PLAST ALUM.

## Installation

1. Installer Python 3.11 ou plus récent.
2. Ouvrir PowerShell dans ce dossier.
3. Installer les dépendances :

```powershell
python -m pip install -r requirements.txt
```

4. Lancer l'application :

```powershell
python main.py
```

## Premier lancement

La base SQLite locale est créée automatiquement dans `data/database.sqlite`.

Compte administrateur initial :

- Utilisateur : `admin`
- Email / identifiant : `admin@plast-alum.local`
- Mot de passe : `admin123`
- Rôle : `admin`

Vous pouvez vous connecter avec `admin` ou `admin@plast-alum.local` dans le champ utilisateur/email.

Après la première connexion, changez ce mot de passe depuis la page `Utilisateurs` : éditez le compte `admin`, saisissez un nouveau mot de passe, puis enregistrez.

## Données de démonstration

Les données de démonstration sont uniquement destinées aux tests. Elles ne sont jamais insérées automatiquement au lancement normal de l'application.

Pour remplir la base locale avec un jeu réaliste de fournisseurs, factures, paiements partiels, retards et alertes :

```powershell
python -m app.database.seed
```

Commande équivalente :

```powershell
python seed_demo.py
```

Le script ajoute des données marquées comme démo :

- 10 fournisseurs marocains ;
- 60 factures avec statuts payée, non payée et partiellement payée ;
- factures en retard de plus de 40, 50 et 60 jours ;
- paiements partiels ;
- pièces jointes PDF de test pour certaines factures ;
- journal d'activité de démonstration.

Le script est sécurisé contre les doublons : si les données de démonstration existent déjà, il n'ajoute rien.

Pour réinitialiser uniquement les données de démonstration :

```powershell
python -m app.database.seed --reset-demo
```

Pour les supprimer uniquement :

```powershell
python -m app.database.seed --remove-demo
```

Ces commandes demandent une confirmation. Pour automatiser un test local :

```powershell
python -m app.database.seed --reset-demo --yes
```

Attention : ces commandes ne ciblent que les lignes marquées comme données de démonstration. Ne les utilisez pas comme mécanisme de nettoyage de données réelles.

## Fonctionnalités

- Connexion sécurisée avec mots de passe hachés.
- Gestion des rôles : `admin` et `user`.
- Tableau de bord avec statistiques, alertes et graphiques.
- Gestion complète des fournisseurs.
- Gestion complète des factures et paiements partiels.
- Suivi des conventions et échéances configurables avec alertes à 15, 7 et 3 jours.
- Calcul automatique des catégories de délai : Normal, Attention, Urgent, Critique.
- Import Excel avec prévisualisation et validation.
- Exports Excel et PDF.
- Sauvegarde/restauration de la base de données.
- Journal d'activité.
- Interface française/arabe avec support RTL pour l'arabe.
- Thèmes sombre et clair.

## Conventions et échéances

Le module `Deadlines / Conventions` permet de suivre des conventions ou contrats avec des délais configurables, par exemple 60, 90, 120 jours ou un délai personnalisé.

La date d'échéance est calculée automatiquement depuis la date de début. Les statuts sont recalculés selon les jours restants :

- `active` : plus de 15 jours restants ;
- `warning` : entre 1 et 15 jours restants ;
- `expired` : échéance atteinte ou dépassée ;
- `completed` : convention marquée comme terminée manuellement.

Les alertes sont affichées dans les notifications et le tableau de bord quand une échéance est à 15 jours ou moins, 7 jours ou moins, 3 jours ou moins, ou expirée.

Note : les délais sont configurables selon le type de convention et le dossier de l'entreprise. Ce module ne constitue pas un avis juridique ou fiscal.

## Sauvegarde

Les sauvegardes sont créées dans `data/backups`. Utilisez la page `Paramètres` pour créer ou restaurer une sauvegarde. L'application peut aussi créer une sauvegarde automatique à la fermeture.

## Exports

Les fichiers Excel et PDF sont enregistrés par défaut dans `data/exports`.

## Construction d'un exécutable Windows

Le point d'entrée de l'application est détecté automatiquement par le script de build. Dans ce projet, le fichier principal est `main.py`.

Depuis le dossier `plast_alum_manager`, lancer :

```powershell
build_windows.bat
```

Le script :

- vérifie le fichier d'entrée `main.py` ;
- installe PyInstaller si nécessaire ;
- utilise le nom `PLAST ALUM - Gestion des Paiements Fournisseurs` ;
- ajoute l'icône `app/assets/icons/app.ico` si elle existe ;
- inclut les assets, thèmes QSS, traductions et `config.py` ;
- crée les dossiers `data/backups`, `data/exports`, `data/uploads` et `data/assets` à côté de l'exécutable.

L'exécutable sera généré ici :

```text
dist/PLAST ALUM - Gestion des Paiements Fournisseurs/PLAST ALUM - Gestion des Paiements Fournisseurs.exe
```

## Raccourci bureau Windows

Après le build, créer le raccourci bureau avec :

```powershell
python create_desktop_shortcut.py
```

Nom du raccourci :

```text
PLAST ALUM - Gestion des Paiements
```

Pour tester les chemins sans créer le raccourci :

```powershell
python create_desktop_shortcut.py --dry-run
```

Des instructions complémentaires sont disponibles dans `installer/build_instructions.md`.
