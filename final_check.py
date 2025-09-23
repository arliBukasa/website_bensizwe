#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification finale pour la mise à jour du module website_bensizwe
"""

import os
from pathlib import Path
import ast

def check_manifest():
    """Vérifier le manifeste"""
    print("🔍 Vérification du manifeste...")
    
    manifest_path = Path(__file__).parent / "__manifest__.py"
    
    if not manifest_path.exists():
        print("❌ Manifeste manquant")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_content = f.read()
    
    try:
        manifest_dict = ast.literal_eval(manifest_content)
        
        # Vérifier les dépendances
        required_deps = ['website', 'website_hr_recruitment', 'hr', 'website_blog', 'portal']
        deps = manifest_dict.get('depends', [])
        
        missing_deps = [dep for dep in required_deps if dep not in deps]
        if missing_deps:
            print(f"❌ Dépendances manquantes: {missing_deps}")
            return False
        
        # Vérifier les fichiers de données
        data_files = manifest_dict.get('data', [])
        views_path = Path(__file__).parent / "views"
        
        for file_ref in data_files:
            if file_ref.startswith('views/'):
                file_path = Path(__file__).parent / file_ref
                if not file_path.exists():
                    print(f"❌ Fichier manquant: {file_ref}")
                    return False
        
        print("✅ Manifeste valide")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le manifeste: {e}")
        return False

def check_controllers():
    """Vérifier les contrôleurs"""
    print("\n🔍 Vérification des contrôleurs...")
    
    controllers_path = Path(__file__).parent / "controllers"
    
    required_controllers = [
        "formation_auth.py",
        "candidate_portal.py"
    ]
    
    for controller in required_controllers:
        controller_path = controllers_path / controller
        if not controller_path.exists():
            print(f"❌ Contrôleur manquant: {controller}")
            return False
    
    # Vérifier l'import dans __init__.py
    init_path = controllers_path / "__init__.py"
    if init_path.exists():
        with open(init_path, 'r', encoding='utf-8') as f:
            init_content = f.read()
        
        if 'formation_auth' not in init_content or 'candidate_portal' not in init_content:
            print("❌ Imports manquants dans controllers/__init__.py")
            return False
    
    print("✅ Contrôleurs valides")
    return True

def check_critical_templates():
    """Vérifier les templates critiques"""
    print("\n🔍 Vérification des templates critiques...")
    
    views_path = Path(__file__).parent / "views"
    
    critical_templates = [
        "candidat_auth_templates.xml",
        "formation_registration_templates.xml",
        "portal_formations.xml"
    ]
    
    for template in critical_templates:
        template_path = views_path / template
        if not template_path.exists():
            print(f"❌ Template critique manquant: {template}")
            return False
    
    print("✅ Templates critiques présents")
    return True

def check_file_integrity():
    """Vérifier l'intégrité des fichiers"""
    print("\n🔍 Vérification de l'intégrité des fichiers...")
    
    # Vérifier que tous les fichiers référencés existent
    base_path = Path(__file__).parent
    
    # Contrôleurs
    controllers_check = [
        "controllers/formation_auth.py",
        "controllers/candidate_portal.py"
    ]
    
    for file_path in controllers_check:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"❌ Fichier manquant: {file_path}")
            return False
    
    print("✅ Intégrité des fichiers OK")
    return True

def main():
    """Fonction principale"""
    print("🚀 Vérification finale du module website_bensizwe")
    print("=" * 60)
    
    checks = [
        check_manifest,
        check_controllers,
        check_critical_templates,
        check_file_integrity
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Le module est prêt pour la mise à jour")
        print("\n📋 Étapes suivantes :")
        print("   1. Sauvegarder la base de données")
        print("   2. Arrêter le serveur Odoo")
        print("   3. Mettre à jour le module : -u website_bensizwe")
        print("   4. Redémarrer le serveur")
        print("   5. Tester les nouvelles fonctionnalités")
        print("\n🎯 Nouvelles routes disponibles :")
        print("   • /formation/auth - Authentification unifiée")
        print("   • /my/formations - Portail candidat")
        print("   • /appels-offres - Blog appels d'offres")
        
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  Corriger les erreurs avant la mise à jour")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
