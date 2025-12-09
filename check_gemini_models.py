#!/usr/bin/env python3
"""
Script para verificar qué modelos de Gemini están disponibles con tu API key
Ejecutar: python check_gemini_models.py
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console
from rich.table import Table

# Cargar variables de entorno
load_dotenv()

console = Console()

def check_models():
    """Verifica y lista los modelos disponibles"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        console.print("[red]❌ Error: GEMINI_API_KEY no está configurada[/red]")
        console.print("Configura tu API key en el archivo .env")
        sys.exit(1)
    
    if api_key == "your_gemini_api_key_here":
        console.print("[red]❌ Error: Debes reemplazar 'your_gemini_api_key_here' con tu API key real[/red]")
        console.print("Obtén tu key en: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    console.print("[cyan]🔍 Verificando modelos disponibles con tu API key...[/cyan]\n")
    
    try:
        # Configurar Gemini
        genai.configure(api_key=api_key)
        
        # Listar modelos
        models = genai.list_models()
        
        # Crear tabla
        table = Table(title="Modelos Gemini Disponibles")
        table.add_column("Nombre del Modelo", style="cyan")
        table.add_column("Soporta generateContent", style="green")
        table.add_column("Descripción", style="yellow")
        
        generate_content_models = []
        
        for model in models:
            # Verificar si soporta generateContent
            supports_generate = 'generateContent' in model.supported_generation_methods
            
            if supports_generate:
                generate_content_models.append(model.name)
                table.add_row(
                    model.name,
                    "✅ Sí",
                    model.display_name if hasattr(model, 'display_name') else "-"
                )
        
        console.print(table)
        
        if generate_content_models:
            console.print(f"\n[green]✅ Encontrados {len(generate_content_models)} modelos compatibles[/green]")
            console.print("\n[cyan]Modelos recomendados para usar:[/cyan]")
            for model_name in generate_content_models[:3]:
                console.print(f"  • {model_name}")
        else:
            console.print("\n[red]❌ No se encontraron modelos compatibles con generateContent[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("\nPosibles causas:")
        console.print("  1. API key inválida o expirada")
        console.print("  2. No tienes acceso a los modelos Gemini")
        console.print("  3. Problemas de conectividad")
        console.print("\nObtén una nueva API key en: https://makersuite.google.com/app/apikey")
        sys.exit(1)

def test_model(model_name: str):
    """Prueba un modelo específico"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content("Hola, di solo 'OK'")
        console.print(f"[green]✅ Modelo {model_name} funciona correctamente[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Modelo {model_name} falló: {e}[/red]")
        return False

if __name__ == "__main__":
    check_models()
    
    console.print("\n" + "="*70)
    console.print("[cyan]🧪 Probando modelos comunes...[/cyan]\n")
    
    common_models = [
        'gemini-pro',
        'gemini-1.5-pro-latest',
        'gemini-1.5-flash-latest',
    ]
    
    for model in common_models:
        test_model(model)