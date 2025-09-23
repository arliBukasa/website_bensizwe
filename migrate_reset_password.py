#!/usr/bin/env python3
"""
Script pour ajouter les colonnes de réinitialisation de mot de passe
"""

import psycopg2
import sys

def add_reset_password_columns():
    """Ajoute les colonnes reset_password_token et reset_password_token_expiry"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host="localhost",
            database="demo15",  # Changez selon votre base
            user="postgres",    # Changez selon votre config
            password="postgres" # Changez selon votre config
        )
        
        cur = conn.cursor()
        
        print("🔍 Vérification des colonnes existantes...")
        
        # Vérifier les colonnes existantes
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_users' 
            AND column_name IN ('reset_password_token', 'reset_password_token_expiry')
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"Colonnes existantes: {existing_columns}")
        
        # Ajouter reset_password_token si nécessaire
        if 'reset_password_token' not in existing_columns:
            print("➕ Ajout de la colonne reset_password_token...")
            cur.execute("ALTER TABLE res_users ADD COLUMN reset_password_token VARCHAR")
            print("✅ Colonne reset_password_token ajoutée")
        else:
            print("ℹ️  Colonne reset_password_token existe déjà")
        
        # Ajouter reset_password_token_expiry si nécessaire
        if 'reset_password_token_expiry' not in existing_columns:
            print("➕ Ajout de la colonne reset_password_token_expiry...")
            cur.execute("ALTER TABLE res_users ADD COLUMN reset_password_token_expiry TIMESTAMP")
            print("✅ Colonne reset_password_token_expiry ajoutée")
        else:
            print("ℹ️  Colonne reset_password_token_expiry existe déjà")
        
        # Valider les changements
        conn.commit()
        print("🎉 Migration terminée avec succès!")
        
        # Fermer la connexion
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de la migration des colonnes de réinitialisation...")
    success = add_reset_password_columns()
    
    if success:
        print("\n✅ Migration réussie! Vous pouvez maintenant:")
        print("1. Redémarrer Odoo")
        print("2. Tester le système de réinitialisation")
        sys.exit(0)
    else:
        print("\n❌ Migration échouée!")
        sys.exit(1)