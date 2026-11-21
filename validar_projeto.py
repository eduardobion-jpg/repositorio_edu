#!/usr/bin/env python
"""
Script de validação: verifica se o projeto está totalmente funcional.
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("╔════════════════════════════════════════════════════════╗")
print("║  Validação do Projeto - Painel Operacional Loja       ║")
print("╚════════════════════════════════════════════════════════╝")
print()

checks = []

# 1. Verificar estrutura de diretórios
print("📁 Verificando estrutura de diretórios...")
required_dirs = ["templates", "static", "data", "env"]
for dir_name in required_dirs:
    dir_path = os.path.join(BASE_DIR, dir_name)
    exists = os.path.isdir(dir_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {dir_name}/")
    checks.append(exists)

print()

# 2. Verificar arquivos críticos
print("📄 Verificando arquivos críticos...")
required_files = ["app.py", "setup_db.py", "requirements.txt", "loja.db"]
for file_name in required_files:
    file_path = os.path.join(BASE_DIR, file_name)
    exists = os.path.isfile(file_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {file_name}")
    checks.append(exists)

print()

# 3. Verificar templates
print("🎨 Verificando templates...")
template_files = ["base.html", "dashboard.html", "vendas.html", "estoque.html", "logistica.html"]
templates_dir = os.path.join(BASE_DIR, "templates")
for tmpl in template_files:
    tmpl_path = os.path.join(templates_dir, tmpl)
    exists = os.path.isfile(tmpl_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {tmpl}")
    checks.append(exists)

print()

# 4. Verificar banco de dados
print("🗄️  Verificando banco de dados...")
db_path = os.path.join(BASE_DIR, "loja.db")
if os.path.isfile(db_path):
    print(f"  ✓ loja.db existe ({os.path.getsize(db_path)} bytes)")

    # Verificar tabelas
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()

        expected_tables = ['vendas', 'estoque', 'logistica']
        found_tables = [t[0] for t in tables]

        print("  Tabelas encontradas:")
        for tbl in expected_tables:
            status = "✓" if tbl in found_tables else "✗"
            print(f"    {status} {tbl}")
            checks.append(tbl in found_tables)
    except Exception as e:
        print(f"  ✗ Erro ao verificar banco: {e}")
        checks.append(False)
else:
    print("  ✗ loja.db não encontrado")
    checks.append(False)

print()

# 5. Verificar dependências Python
print("📦 Verificando dependências Python...")
try:
    import flask
    print(f"  ✓ Flask {flask.__version__}")
    checks.append(True)
except ImportError:
    print("  ✗ Flask não instalado")
    checks.append(False)

try:
    import sqlalchemy
    print(f"  ✓ SQLAlchemy {sqlalchemy.__version__}")
    checks.append(True)
except ImportError:
    print("  ✗ SQLAlchemy não instalado")
    checks.append(False)

try:
    import pandas
    print(f"  ✓ pandas {pandas.__version__}")
    checks.append(True)
except ImportError:
    print("  ✗ pandas não instalado")
    checks.append(False)

print()

# Resultado final
print("╔════════════════════════════════════════════════════════╗")
total = len(checks)
passed = sum(checks)
status_text = "✅ TUDO PRONTO!" if all(checks) else "⚠️  ALGUNS PROBLEMAS ENCONTRADOS"
status_color = "Green" if all(checks) else "Yellow"

print(f"║  {status_text.ljust(52)} ║")
print(f"║  {f'Verificações: {passed}/{total} passaram'.ljust(52)} ║")
print("╚════════════════════════════════════════════════════════╝")

if all(checks):
    print()
    print("🚀 Para iniciar o servidor:")
    print("   python app.py")
    print()
    print("   Acesse: http://127.0.0.1:5050")
    sys.exit(0)
else:
    print()
    print("❌ Problemas detectados. Corrija e tente novamente.")
    sys.exit(1)
