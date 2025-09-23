"""
Script Odoo pour ajouter les colonnes de réinitialisation
À exécuter avec: odoo shell -d demo15
"""

# Dans le shell Odoo, exécutez ces commandes :

# 1. Vérifier les colonnes existantes
env.cr.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='res_users' 
    AND column_name IN ('reset_password_token', 'reset_password_token_expiry')
""")
existing = [row[0] for row in env.cr.fetchall()]
print(f"Colonnes existantes: {existing}")

# 2. Ajouter reset_password_token si nécessaire
if 'reset_password_token' not in existing:
    env.cr.execute("ALTER TABLE res_users ADD COLUMN reset_password_token VARCHAR")
    print("✅ Colonne reset_password_token ajoutée")

# 3. Ajouter reset_password_token_expiry si nécessaire  
if 'reset_password_token_expiry' not in existing:
    env.cr.execute("ALTER TABLE res_users ADD COLUMN reset_password_token_expiry TIMESTAMP")
    print("✅ Colonne reset_password_token_expiry ajoutée")

# 4. Confirmer les changements
env.cr.commit()
print("🎉 Migration terminée!")

# 5. Vérifier que tout est OK
env.cr.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='res_users' 
    AND column_name IN ('reset_password_token', 'reset_password_token_expiry')
""")
final = [row[0] for row in env.cr.fetchall()]
print(f"Colonnes finales: {final}")