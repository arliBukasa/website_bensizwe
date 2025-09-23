# -*- coding: utf-8 -*-
"""
Script de migration pour ajouter les colonnes de réinitialisation de mot de passe
À exécuter manuellement après que le module fonctionne
"""

def migrate_add_reset_password_fields(cr):
    """Ajoute les colonnes de réinitialisation de mot de passe à la table res_users"""
    
    # Vérifier si les colonnes existent déjà
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_users' 
        AND column_name IN ('reset_password_token', 'reset_password_token_expiry')
    """)
    
    existing_columns = [row[0] for row in cr.fetchall()]
    
    # Ajouter reset_password_token si elle n'existe pas
    if 'reset_password_token' not in existing_columns:
        cr.execute("""
            ALTER TABLE res_users 
            ADD COLUMN reset_password_token VARCHAR
        """)
        print("✓ Colonne reset_password_token ajoutée")
    else:
        print("- Colonne reset_password_token existe déjà")
    
    # Ajouter reset_password_token_expiry si elle n'existe pas
    if 'reset_password_token_expiry' not in existing_columns:
        cr.execute("""
            ALTER TABLE res_users 
            ADD COLUMN reset_password_token_expiry TIMESTAMP
        """)
        print("✓ Colonne reset_password_token_expiry ajoutée")
    else:
        print("- Colonne reset_password_token_expiry existe déjà")

# Instructions d'utilisation :
# 1. Connectez-vous à la base de données PostgreSQL
# 2. Exécutez ce script Python ou les commandes SQL directement
# 3. Redémarrez Odoo
# 4. Décommentez les champs dans models/res_users.py
# 5. Mettez à jour le module