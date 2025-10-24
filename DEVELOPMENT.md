# Development Guide - Cross-Platform

Dieses Projekt bietet **3 verschiedene Möglichkeiten**, um Entwicklungs-Tasks auszuführen - kompatibel mit **Windows, macOS und Linux**.

## 🎯 Empfohlene Lösung: Python Task Runner ⭐

**Funktioniert auf allen Plattformen ohne zusätzliche Tools!**

### Installation

Keine! Python ist bereits installiert.

### Verwendung

```bash
# Hilfe anzeigen
python tasks.py help

# Dependencies installieren
python tasks.py install

# Tests ausführen
python tasks.py test           # Alle Tests
python tasks.py test-unit      # Nur Unit Tests
python tasks.py test-int       # Nur Integration Tests

# Code-Qualität
python tasks.py lint           # Linter ausführen
python tasks.py format         # Code formatieren
python tasks.py typecheck      # Type-Checking
python tasks.py check          # Alle Checks (lint + typecheck)

# Sonstiges
python tasks.py clean          # Cache aufräumen
python tasks.py run            # Server starten
```

**Vorteile:**

- ✅ Funktioniert überall (Windows, macOS, Linux)
- ✅ Keine zusätzlichen Tools erforderlich
- ✅ Benutzerfreundliche Ausgabe mit Emojis
- ✅ Einfach zu erweitern

---

## 🪟 Windows-Spezifisch: PowerShell

**Nur für Windows-Nutzer**

### Installation

PowerShell ist in Windows integriert.

### Verwendung

```powershell
# Hilfe anzeigen
.\tasks.ps1 help

# Dependencies installieren
.\tasks.ps1 install

# Tests ausführen
.\tasks.ps1 test           # Alle Tests
.\tasks.ps1 test-unit      # Nur Unit Tests
.\tasks.ps1 test-int       # Nur Integration Tests

# Code-Qualität
.\tasks.ps1 lint           # Linter ausführen
.\tasks.ps1 format         # Code formatieren
.\tasks.ps1 typecheck      # Type-Checking
.\tasks.ps1 check          # Alle Checks

# Sonstiges
.\tasks.ps1 clean          # Cache aufräumen
.\tasks.ps1 run            # Server starten
```

**Vorteile:**

- ✅ Native Windows-Integration
- ✅ Farbige Ausgabe
- ✅ Schnelle Ausführung

---

## 🛠️ Unix/Linux/Mac: Makefile (Original)

**Für Unix-Systeme und Windows mit Git Bash / WSL**

### Installation auf Windows

Installiere eine dieser Optionen:

- **Git Bash** (empfohlen): Kommt mit Git für Windows
- **WSL** (Windows Subsystem for Linux)
- **Chocolatey Make**: `choco install make`

### Verwendung

```bash
# Hilfe anzeigen
make help

# Dependencies installieren
make install

# Tests ausführen
make test

# Code-Qualität
make lint              # Linter ausführen
make format            # Code formatieren
make typecheck         # Type-Checking
make check             # Alle Checks

# Sonstiges
make clean             # Cache aufräumen
make run               # Server starten
```

**Vorteile:**

- ✅ Standard in der Unix-Welt
- ✅ Kurze Befehle
- ✅ Parallel-Ausführung möglich

**Nachteile auf Windows:**

- ❌ Benötigt zusätzliche Tools
- ❌ `rm`, `find` Befehle nicht nativ verfügbar

---

## 📋 Befehlsübersicht

| Aktion         | Python                      | PowerShell              | Makefile         |
| -------------- | --------------------------- | ----------------------- | ---------------- |
| Hilfe          | `python tasks.py help`      | `.\tasks.ps1 help`      | `make help`      |
| Install        | `python tasks.py install`   | `.\tasks.ps1 install`   | `make install`   |
| Alle Tests     | `python tasks.py test`      | `.\tasks.ps1 test`      | `make test`      |
| Unit Tests     | `python tasks.py test-unit` | `.\tasks.ps1 test-unit` | `make test-unit` |
| Integration    | `python tasks.py test-int`  | `.\tasks.ps1 test-int`  | `make test-int`  |
| Lint           | `python tasks.py lint`      | `.\tasks.ps1 lint`      | `make lint`      |
| Format         | `python tasks.py format`    | `.\tasks.ps1 format`    | `make format`    |
| Typecheck      | `python tasks.py typecheck` | `.\tasks.ps1 typecheck` | `make typecheck` |
| Alle Checks    | `python tasks.py check`     | `.\tasks.ps1 check`     | `make check`     |
| Clean          | `python tasks.py clean`     | `.\tasks.ps1 clean`     | `make clean`     |
| Server starten | `python tasks.py run`       | `.\tasks.ps1 run`       | `make run`       |

---

## 🎨 Direkter uv-Befehl (Alle Plattformen)

Falls du die Task-Runner nicht verwenden möchtest, kannst du auch direkt `uv` nutzen:

```bash
# Dependencies
uv sync

# Tests
uv run pytest                    # Alle Tests
uv run pytest -m unit            # Nur Unit Tests
uv run pytest -m integration     # Nur Integration Tests

# Code-Qualität
uv run ruff check src/           # Linter
uv run ruff format src/          # Formatter
uv run pyright src/              # Type-Checking Source
uv run pyright tests/            # Type-Checking Tests

# Coverage
uv run pytest --cov=src/fdk_mcp --cov-report=html

# Server
uv run sbb-fdk-mcp
```

---

## 💡 Empfehlung

**Für die beste Cross-Platform-Erfahrung:**

1. **Windows**: Verwende `python tasks.py` oder `.\tasks.ps1`
2. **macOS/Linux**: Verwende `make` oder `python tasks.py`
3. **CI/CD**: Verwende direkte `uv run` Befehle

**Warum Python-Task-Runner?**

- Funktioniert überall ohne zusätzliche Installation
- Einfach zu erweitern und anzupassen
- Bessere Fehlerbehandlung als Makefile
- Plattform-unabhängiger Python-Code

---

## 🔧 Erweiterung

### Neuen Task hinzufügen (Python)

Bearbeite `tasks.py`:

```python
def my_new_task() -> int:
    """Description of my task."""
    return run_command(["command", "here"], "Task description")

# In main() commands dict:
commands = {
    # ... existing commands
    "my_task": my_new_task,
}
```

### Neuen Task hinzufügen (PowerShell)

Bearbeite `tasks.ps1`:

```powershell
function Invoke-MyTask {
    Write-Host "Running my task..." -ForegroundColor Yellow
    # Your commands here
}

# In switch statement:
"my-task" { Invoke-MyTask }
```

### Neuen Task hinzufügen (Makefile)

Bearbeite `Makefile`:

```makefile
my-task:
    uv run my-command
```

---

## 📚 Weitere Ressourcen

- [uv Documentation](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [pyright Documentation](https://github.com/microsoft/pyright)
