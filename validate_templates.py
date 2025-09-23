#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation des templates XML pour website_bensizwe
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_file(file_path):
    """Valide un fichier XML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse XML
        ET.fromstring(content)
        return True, "OK"
    except ET.ParseError as e:
        return False, f"Erreur XML: {e}"
    except Exception as e:
        return False, f"Erreur: {e}"

def main():
    """Fonction principale"""
    module_path = Path(__file__).parent
    views_path = module_path / "views"
    
    print("🔍 Validation des templates XML pour website_bensizwe\n")
    
    xml_files = list(views_path.glob("*.xml"))
    
    if not xml_files:
        print("❌ Aucun fichier XML trouvé dans le dossier views/")
        return
    
    total_files = len(xml_files)
    valid_files = 0
    
    for xml_file in xml_files:
        is_valid, message = validate_xml_file(xml_file)
        status = "✅" if is_valid else "❌"
        print(f"{status} {xml_file.name}: {message}")
        
        if is_valid:
            valid_files += 1
    
    print(f"\n📊 Résumé: {valid_files}/{total_files} fichiers valides")
    
    if valid_files == total_files:
        print("🎉 Tous les templates XML sont syntaxiquement valides!")
        
        # Validation de nos nouveaux templates
        print("\n🔎 Vérification des nouveaux templates:")
        
        templates_to_check = [
            "candidat_auth_templates.xml",
            "formation_registration_templates.xml", 
            "portal_formations.xml"
        ]
        
        for template in templates_to_check:
            template_path = views_path / template
            if template_path.exists():
                print(f"✅ {template} - Template présent et valide")
            else:
                print(f"❌ {template} - Template manquant")
                
    else:
        print("⚠️  Certains templates contiennent des erreurs de syntaxe.")

if __name__ == "__main__":
    main()
