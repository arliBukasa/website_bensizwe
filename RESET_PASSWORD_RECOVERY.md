# Récupération du système de réinitialisation de mot de passe

## Problème rencontré
Les colonnes `reset_password_token` et `reset_password_token_expiry` n'existent pas dans la table `res_users` de la base de données, causant des erreurs SQL.

## Solution immédiate (appliquée)
1. ✅ Désactivation temporaire des champs dans `models/res_users.py`
2. ✅ Simplification des méthodes pour éviter les erreurs
3. ✅ Le système de base fonctionne maintenant

## État actuel
- ✅ `/candidat/login` - Interface unifiée fonctionnelle
- ✅ `/candidat/signup` - Inscription fonctionnelle  
- ✅ `/candidat/reset_password` - Page de demande (simulation simple)
- ❌ Système complet de tokens (désactivé temporairement)

## Pour réactiver le système complet

### Étape 1: Ajouter les colonnes en base
Exécutez le script SQL dans PostgreSQL :
```bash
psql -U postgres -d demo15 -f c:\odoo\server\odoo\addons\website_bensizwe\migrations\add_reset_password_fields.sql
```

### Étape 2: Réactiver les champs dans le modèle
Dans `models/res_users.py`, décommentez les lignes :
```python
reset_password_token = fields.Char(string='Token de réinitialisation', copy=False)
reset_password_token_expiry = fields.Datetime(string='Expiration du token', copy=False)
```

### Étape 3: Réactiver les méthodes complètes
Décommentez le code TODO dans les méthodes :
- `_generate_reset_token()`
- `_validate_reset_token()`
- `_reset_password_with_token()`

### Étape 4: Réactiver les routes de confirmation
Dans `controllers/candidat_auth_main.py`, décommentez les routes :
- `/candidat/reset_password/confirm`
- `/candidat/reset_password/confirm/submit`

### Étape 5: Redémarrer et tester
```bash
c:\odoo\python\python.exe c:\odoo\server\odoo-bin -d demo15 -u website_bensizwe --stop-after-init
c:\odoo\python\python.exe c:\odoo\server\odoo-bin -d demo15 --dev=reload
```

## Tests
1. Aller sur `/candidat/login`
2. Cliquer sur "Mot de passe oublié"
3. Entrer un email existant
4. Vérifier les logs pour l'URL de réinitialisation
5. Tester le processus complet

## Notes
- Le système de base fonctionne maintenant sans erreur
- La réinitialisation de mot de passe est en mode simulation
- Tous les fichiers et templates sont prêts pour l'activation