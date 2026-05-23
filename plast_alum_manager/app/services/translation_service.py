from __future__ import annotations

import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QWidget,
)

from config import TRANSLATION_DIR


SUPPORTED_LANGUAGES = {"fr", "en"}
DEFAULT_LANGUAGE = "fr"

UI_TEXTS = {
    "secure_access": {"fr": "Accès sécurisé", "en": "Secure access"},
    "create_account": {"fr": "Créer un compte", "en": "Create account"},
    "register_subtitle": {"fr": "Ouvrez un accès utilisateur standard pour consulter les données de l'application.", "en": "Create a standard user account to view application data."},
    "login_subtitle": {"fr": "Connectez-vous avec votre nom d'utilisateur ou votre email.", "en": "Sign in with your username or email."},
    "full_name_required": {"fr": "Nom complet *", "en": "Full name *"},
    "username_required": {"fr": "Nom d'utilisateur *", "en": "Username *"},
    "email_required": {"fr": "Email *", "en": "Email *"},
    "phone_optional": {"fr": "Téléphone (optionnel)", "en": "Phone (optional)"},
    "password_required": {"fr": "Mot de passe *", "en": "Password *"},
    "confirm_password": {"fr": "Confirmer le mot de passe *", "en": "Confirm password *"},
    "forgot_password": {"fr": "Mot de passe oublié ?", "en": "Forgot password?"},
    "light_mode": {"fr": "Mode clair", "en": "Light mode"},
    "dark_mode": {"fr": "Mode sombre", "en": "Dark mode"},
    "supplier_payments": {"fr": "Paiements fournisseurs", "en": "Supplier payments"},
    "suppliers_word": {"fr": "fournisseurs", "en": "suppliers"},
    "invoices_word": {"fr": "factures", "en": "invoices"},
    "global_search": {"fr": "Recherche globale", "en": "Global search"},
    "change_theme": {"fr": "Changer de thème", "en": "Change theme"},
    "ready": {"fr": "Prêt", "en": "Ready"},
    "language_updated": {"fr": "La langue est mise à jour.", "en": "Language updated."},
    "dashboard_title": {"fr": "Tableau de bord", "en": "Dashboard"},
    "suppliers_title": {"fr": "Fournisseurs", "en": "Suppliers"},
    "invoices_title": {"fr": "Factures", "en": "Invoices"},
    "conventions_title": {"fr": "Deadlines / Conventions", "en": "Deadlines / Conventions"},
    "reports_title": {"fr": "Rapports", "en": "Reports"},
    "import_excel_title": {"fr": "Import Excel", "en": "Import Excel"},
    "users_title": {"fr": "Utilisateurs", "en": "Users"},
    "settings_title": {"fr": "Paramètres", "en": "Settings"},
    "activity_logs_title": {"fr": "Journal d'activité", "en": "Activity log"},
    "activity_logs_title_alt": {"fr": "Journal d’activité", "en": "Activity log"},
    "logout": {"fr": "Déconnexion", "en": "Log out"},
    "welcome": {"fr": "Bienvenue", "en": "Welcome"},
    "backup_database": {"fr": "Sauvegarder base", "en": "Back up database"},
    "backup_database_tip": {"fr": "Créer une sauvegarde de la base", "en": "Create a database backup"},
    "create_backup": {"fr": "Créer sauvegarde", "en": "Create backup"},
    "restore_backup": {"fr": "Restaurer sauvegarde", "en": "Restore backup"},
    "add_supplier": {"fr": "Ajouter fournisseur", "en": "Add supplier"},
    "add_invoice": {"fr": "Ajouter facture", "en": "Add invoice"},
    "add_user": {"fr": "Ajouter utilisateur", "en": "Add user"},
    "add_convention": {"fr": "Ajouter convention", "en": "Add convention"},
    "export_suppliers": {"fr": "Exporter fournisseurs", "en": "Export suppliers"},
    "export_report": {"fr": "Exporter rapport", "en": "Export report"},
    "export_logs": {"fr": "Exporter logs", "en": "Export logs"},
    "export_excel": {"fr": "Export Excel", "en": "Export Excel"},
    "export_pdf": {"fr": "Export PDF", "en": "Export PDF"},
    "import_excel_button": {"fr": "Importer Excel", "en": "Import Excel"},
    "choose_excel": {"fr": "Choisir fichier Excel", "en": "Choose Excel file"},
    "import_valid_rows": {"fr": "Importer les lignes valides", "en": "Import valid rows"},
    "choose_file": {"fr": "Choisir fichier", "en": "Choose file"},
    "choose": {"fr": "Choisir", "en": "Choose"},
    "save_settings": {"fr": "Enregistrer paramètres", "en": "Save settings"},
    "print": {"fr": "Imprimer", "en": "Print"},
    "recalculate": {"fr": "Recalculer", "en": "Recalculate"},
    "complete": {"fr": "Terminer", "en": "Complete"},
    "view": {"fr": "Voir", "en": "View"},
    "edit": {"fr": "Éditer", "en": "Edit"},
    "edit_alt": {"fr": "Modifier", "en": "Edit"},
    "delete": {"fr": "Supprimer", "en": "Delete"},
    "delete_short": {"fr": "Sup.", "en": "Del."},
    "invoices_button": {"fr": "Factures", "en": "Invoices"},
    "previous": {"fr": "Précédent", "en": "Previous"},
    "next": {"fr": "Suivant", "en": "Next"},
    "search": {"fr": "Recherche", "en": "Search"},
    "supplier_search": {"fr": "Recherche nom, ICE, téléphone, ville", "en": "Search name, ICE, phone, city"},
    "invoice_search": {"fr": "Recherche fournisseur ou numéro facture", "en": "Search supplier or invoice number"},
    "user_search": {"fr": "Recherche utilisateur", "en": "Search user"},
    "convention_search": {"fr": "Recherche société ou numéro de convention", "en": "Search company or convention number"},
    "action": {"fr": "Action", "en": "Action"},
    "all_users": {"fr": "Tous utilisateurs", "en": "All users"},
    "all_suppliers": {"fr": "Tous fournisseurs", "en": "All suppliers"},
    "all_statuses": {"fr": "Tous statuts", "en": "All statuses"},
    "all_deadlines": {"fr": "Tous délais", "en": "All deadlines"},
    "all_cities": {"fr": "Toutes les villes", "en": "All cities"},
    "recent_date": {"fr": "Date récente", "en": "Newest date"},
    "old_date": {"fr": "Date ancienne", "en": "Oldest date"},
    "amount": {"fr": "Montant", "en": "Amount"},
    "days_count": {"fr": "Nombre de jours", "en": "Day count"},
    "name": {"fr": "Nom", "en": "Name"},
    "created_date": {"fr": "Date création", "en": "Created date"},
    "date_from": {"fr": "Du yyyy-mm-dd", "en": "From yyyy-mm-dd"},
    "date_to": {"fr": "Au yyyy-mm-dd", "en": "To yyyy-mm-dd"},
    "invoice_date": {"fr": "Date facture", "en": "Invoice date"},
    "id": {"fr": "ID", "en": "ID"},
    "supplier": {"fr": "Fournisseur", "en": "Supplier"},
    "supplier_name": {"fr": "Nom fournisseur", "en": "Supplier name"},
    "invoice_number": {"fr": "N° facture", "en": "Invoice no."},
    "invoice": {"fr": "Facture", "en": "Invoice"},
    "date": {"fr": "Date", "en": "Date"},
    "reception": {"fr": "Réception", "en": "Reception"},
    "status": {"fr": "Statut", "en": "Status"},
    "payment": {"fr": "Paiement", "en": "Payment"},
    "days": {"fr": "Jours", "en": "Days"},
    "deadline": {"fr": "Délai", "en": "Deadline"},
    "attachment_short": {"fr": "PJ", "en": "File"},
    "actions": {"fr": "Actions", "en": "Actions"},
    "city": {"fr": "Ville", "en": "City"},
    "phone": {"fr": "Téléphone", "en": "Phone"},
    "email": {"fr": "Email", "en": "Email"},
    "rib": {"fr": "RIB", "en": "RIB"},
    "ttc": {"fr": "TTC", "en": "Total"},
    "remaining": {"fr": "Reste", "en": "Remaining"},
    "paid_amount_short": {"fr": "Payé", "en": "Paid"},
    "user": {"fr": "Utilisateur", "en": "User"},
    "role": {"fr": "Rôle", "en": "Role"},
    "active": {"fr": "Actif", "en": "Active"},
    "last_login": {"fr": "Dernière connexion", "en": "Last login"},
    "entity": {"fr": "Entité", "en": "Entity"},
    "entity_id": {"fr": "ID entité", "en": "Entity ID"},
    "details": {"fr": "Détails", "en": "Details"},
    "unpaid_amount": {"fr": "Impayé", "en": "Unpaid"},
    "paid": {"fr": "Payée", "en": "Paid"},
    "paid_plural": {"fr": "Payées", "en": "Paid"},
    "unpaid": {"fr": "Non payée", "en": "Unpaid"},
    "unpaid_plural": {"fr": "Non payées", "en": "Unpaid"},
    "partial": {"fr": "Partiellement payée", "en": "Partially paid"},
    "partial_plural": {"fr": "Partielles", "en": "Partial"},
    "overdue": {"fr": "En retard", "en": "Overdue"},
    "unpaid_amount_card": {"fr": "Montant impayé", "en": "Unpaid amount"},
    "paid_amount_card": {"fr": "Montant payé", "en": "Paid amount"},
    "critical_60": {"fr": "Critiques +60j", "en": "Critical +60d"},
    "urgent_conventions": {"fr": "Conventions urgentes", "en": "Urgent conventions"},
    "normal": {"fr": "Normal", "en": "Normal"},
    "attention": {"fr": "Attention", "en": "Attention"},
    "urgent": {"fr": "Urgent", "en": "Urgent"},
    "critical": {"fr": "Critique", "en": "Critical"},
    "yes": {"fr": "Oui", "en": "Yes"},
    "no": {"fr": "Non", "en": "No"},
    "users_management": {"fr": "Gestion des utilisateurs", "en": "User management"},
    "suppliers_management": {"fr": "Gestion des fournisseurs", "en": "Supplier management"},
    "invoices_management": {"fr": "Gestion des factures fournisseurs", "en": "Supplier invoice management"},
    "reports_exports": {"fr": "Rapports et exports", "en": "Reports and exports"},
    "all_invoices": {"fr": "Toutes les factures", "en": "All invoices"},
    "paid_invoices": {"fr": "Factures payées", "en": "Paid invoices"},
    "unpaid_invoices": {"fr": "Factures non payées", "en": "Unpaid invoices"},
    "partial_invoices": {"fr": "Factures partiellement payées", "en": "Partially paid invoices"},
    "critical_invoices_60": {"fr": "Factures critiques +60 jours", "en": "Critical invoices +60 days"},
    "unpaid_by_supplier": {"fr": "Montant impayé par fournisseur", "en": "Unpaid amount by supplier"},
    "monthly_report": {"fr": "Rapport mensuel", "en": "Monthly report"},
    "deadline_report": {"fr": "Rapport des délais de paiement", "en": "Payment deadline report"},
    "recent_activity": {"fr": "Activité récente", "en": "Recent activity"},
    "priority_alerts": {"fr": "Alertes prioritaires", "en": "Priority alerts"},
    "payment_analysis": {"fr": "Analyse des paiements", "en": "Payment analysis"},
    "conventions_deadlines": {"fr": "Conventions et échéances", "en": "Conventions and deadlines"},
    "notifications_none": {"fr": "Aucune notification", "en": "No notifications"},
    "empty_activity": {"fr": "Aucune activité enregistrée.", "en": "No activity recorded."},
    "empty_activity_found": {"fr": "Aucune activité trouvée.", "en": "No activity found."},
    "empty_supplier_found": {"fr": "Aucun fournisseur trouvé.", "en": "No suppliers found."},
    "empty_invoice_found": {"fr": "Aucune facture trouvée.", "en": "No invoices found."},
    "empty_data_available": {"fr": "Aucune donnée disponible.", "en": "No data available."},
    "empty_data_filters": {"fr": "Aucune donnée pour les filtres sélectionnés.", "en": "No data for the selected filters."},
    "empty_urgent_alerts": {"fr": "Aucune alerte urgente", "en": "No urgent alerts"},
    "deadlines_under_control": {"fr": "Les délais sont sous contrôle.", "en": "Deadlines are under control."},
    "empty_convention_deadline": {"fr": "Aucune échéance de convention", "en": "No convention deadline"},
    "empty_active_convention": {"fr": "Aucune convention active à surveiller.", "en": "No active convention to monitor."},
    "access_denied": {"fr": "Accès refusé", "en": "Access denied"},
    "authorized_users_only": {"fr": "Cette page est réservée aux utilisateurs autorisés.", "en": "This page is reserved for authorized users."},
    "admins_only": {"fr": "Cette page est réservée aux administrateurs.", "en": "This page is reserved for administrators."},
    "forgot_password_title": {"fr": "Mot de passe oublié", "en": "Forgot password"},
    "forgot_password_message": {
        "fr": "La récupération automatique sera disponible dans une prochaine version. Contactez un administrateur pour réinitialiser le mot de passe.",
        "en": "Automatic recovery will be available in a future version. Contact an administrator to reset the password.",
    },
    "security": {"fr": "Sécurité", "en": "Security"},
    "default_password_warning": {
        "fr": "Le compte admin utilise encore un mot de passe par défaut. Changez-le depuis la page Utilisateurs.",
        "en": "The admin account is still using the default password. Change it from the Users page.",
    },
    "login_failed": {"fr": "Connexion impossible.", "en": "Unable to sign in."},
    "account_created": {"fr": "Compte créé avec succès. Vous pouvez vous connecter.", "en": "Account created successfully. You can sign in."},
    "auth_cover_caption": {
        "fr": "Gestion sécurisée des fournisseurs, factures et paiements.",
        "en": "Secure management of suppliers, invoices and payments.",
    },
    "file_created": {"fr": "Fichier créé:", "en": "File created:"},
    "settings_company": {"fr": "Société", "en": "Company"},
    "settings_app_title": {"fr": "Titre application", "en": "Application title"},
    "settings_default_language": {"fr": "Langue par défaut", "en": "Default language"},
    "settings_default_theme": {"fr": "Thème par défaut", "en": "Default theme"},
    "settings_currency": {"fr": "Devise", "en": "Currency"},
    "settings_date_format": {"fr": "Format date", "en": "Date format"},
    "settings_logo": {"fr": "Logo", "en": "Logo"},
    "settings_backup_folder": {"fr": "Dossier sauvegarde", "en": "Backup folder"},
    "settings_keep_backups": {"fr": "Sauvegardes à garder", "en": "Backups to keep"},
    "settings_high_unpaid": {"fr": "Alerte montant impayé", "en": "High unpaid alert"},
    "settings_auto_backup": {"fr": "Créer une sauvegarde à la fermeture", "en": "Create a backup on close"},
    "normal_max_days": {"fr": "Normal max jours", "en": "Normal max days"},
    "attention_min": {"fr": "Attention min", "en": "Attention min"},
    "attention_max": {"fr": "Attention max", "en": "Attention max"},
    "urgent_min": {"fr": "Urgent min", "en": "Urgent min"},
    "urgent_max": {"fr": "Urgent max", "en": "Urgent max"},
    "critical_min": {"fr": "Critique min", "en": "Critical min"},
    "dark_theme": {"fr": "Sombre", "en": "Dark"},
    "light_theme": {"fr": "Clair", "en": "Light"},
    "french": {"fr": "Français", "en": "French"},
    "english": {"fr": "English", "en": "English"},
}

_TEXT_INDEX = {
    value: key
    for key, translations in UI_TEXTS.items()
    for value in translations.values()
}

DYNAMIC_TEXT_KEYS = (
    "welcome",
    "file_created",
    "suppliers_word",
    "invoices_word",
)


class TranslationService:
    def __init__(self, language: str = "fr") -> None:
        self.language = self._normalize(language)
        self.messages = self._load(self.language)

    @staticmethod
    def _normalize(language: str | None) -> str:
        return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    def _load(self, language: str) -> dict[str, str]:
        language = self._normalize(language)
        path = TRANSLATION_DIR / f"{language}.json"
        if not path.exists():
            path = TRANSLATION_DIR / "fr.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def set_language(self, language: str) -> None:
        self.language = self._normalize(language)
        self.messages = self._load(language)
        app = QApplication.instance()
        if app:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def tr(self, key: str, default: str | None = None) -> str:
        return self.messages.get(key, default or key)

    def text(self, key: str, default: str | None = None) -> str:
        translations = UI_TEXTS.get(key)
        if translations:
            return translations.get(self.language, translations[DEFAULT_LANGUAGE])
        return self.tr(key, default)

    def translate_text(self, value: str) -> str:
        key = _TEXT_INDEX.get(value)
        if not key:
            stripped = value.strip()
            key = _TEXT_INDEX.get(stripped)
            if not key:
                return self._translate_dynamic_text(value)
            translated = self.text(key)
            return value.replace(stripped, translated, 1)
        return self.text(key)

    def _translate_dynamic_text(self, value: str) -> str:
        translated_value = value
        source_language = "en" if self.language == "fr" else "fr"
        for key in DYNAMIC_TEXT_KEYS:
            translations = UI_TEXTS[key]
            source = translations[source_language]
            target = translations[self.language]
            translated_value = translated_value.replace(source, target)
        return translated_value

    def apply_to_widget(self, root: QWidget) -> None:
        for widget in [root, *root.findChildren(QWidget)]:
            if widget.toolTip():
                widget.setToolTip(self.translate_text(widget.toolTip()))
            if isinstance(widget, QLabel) and widget.text():
                widget.setText(self.translate_text(widget.text()))
            elif isinstance(widget, QPushButton) and widget.text():
                widget.setText(self.translate_text(widget.text()))
            elif isinstance(widget, QCheckBox) and widget.text():
                widget.setText(self.translate_text(widget.text()))
            elif isinstance(widget, QGroupBox) and widget.title():
                widget.setTitle(self.translate_text(widget.title()))
            if isinstance(widget, QLineEdit) and widget.placeholderText():
                widget.setPlaceholderText(self.translate_text(widget.placeholderText()))
            elif isinstance(widget, QTextEdit) and widget.placeholderText():
                widget.setPlaceholderText(self.translate_text(widget.placeholderText()))
            elif isinstance(widget, QComboBox):
                for index in range(widget.count()):
                    widget.setItemText(index, self.translate_text(widget.itemText(index)))
            elif isinstance(widget, QTableWidget):
                for column in range(widget.columnCount()):
                    item = widget.horizontalHeaderItem(column)
                    if item:
                        item.setText(self.translate_text(item.text()))
                for row in range(widget.rowCount()):
                    for column in range(widget.columnCount()):
                        item = widget.item(row, column)
                        if item:
                            item.setText(self.translate_text(item.text()))
