#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier l'installation du module website_bensizwe
"""

import sys
import os

def check_files():
    """Vérifie que tous les fichiers nécessaires existent"""
    base_path = r"c:\odoo\server\odoo\addons\website_bensizwe"
    
    required_files = [
        "controllers/candidat_auth_main.py",
        "models/res_users.py", 
        "models/__init__.py",
        "views/candidat_auth_templates.xml",
        "__manifest__.py"
    ]
    
    print("=== Vérification des fichiers ===")
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MANQUANT!")
            return False
    
    return True

def check_xml_templates():
    """Vérifie que les templates XML sont bien définis"""
    xml_file = r"c:\odoo\server\odoo\addons\website_bensizwe\views\candidat_auth_templates.xml"
    
    required_templates = [
        'candidat_reset_password_template',
        'candidat_reset_password_confirm_template', 
        'candidat_reset_password_success_template',
        'formation_auth_unified_template'
    ]
    
    print("\n=== Vérification des templates XML ===")
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for template in required_templates:
            if f'id="{template}"' in content:
                print(f"✓ {template}")
            else:
                print(f"✗ {template} - MANQUANT!")
                return False
                
        return True
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier XML: {e}")
        return False

def main():
    """Fonction principale"""
    print("Script de vérification du module website_bensizwe")
    print("="*50)
    
    files_ok = check_files()
    templates_ok = check_xml_templates()
    
    print("\n=== RÉSULTAT ===")
    if files_ok and templates_ok:
        print("✓ Tous les fichiers et templates sont présents!")
        print("\nCommandes pour redémarrer Odoo:")
        print("1. Arrêter tous les processus Python")
        print("2. c:\\odoo\\python\\python.exe c:\\odoo\\server\\odoo-bin -d demo15 -u website_bensizwe --stop-after-init")
        print("3. c:\\odoo\\python\\python.exe c:\\odoo\\server\\odoo-bin -d demo15 --dev=reload")
        return 0
    else:
        print("✗ Des fichiers ou templates sont manquants!")
        return 1

if __name__ == "__main__":
    sys.exit(main())