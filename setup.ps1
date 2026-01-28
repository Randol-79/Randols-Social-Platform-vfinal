# ===========================================
# Randol's Marketing Platform - One-Click Setup
# Windows PowerShell setup script
# ===========================================

$ErrorActionPreference = "Stop"

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"
$Purple = "Magenta"

function Write-Banner {
    Write-Host ""
    Write-Host "  ██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ██╗     ███████╗" -ForegroundColor $Red
    Write-Host "  ██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗██║     ██╔════╝" -ForegroundColor $Red
    Write-Host "  ██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║██║     ███████╗" -ForegroundColor $Red
    Write-Host "  ██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║██║     ╚════██║" -ForegroundColor $Red
    Write-Host "  ██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝███████╗███████║" -ForegroundColor $Red
    Write-Host "  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝" -ForegroundColor $Red
    Write-Host ""
    Write-Host "  Agentic Social Media Marketing Platform" -ForegroundColor $Blue
    Write-Host "  One-Click Setup Wizard for Windows" -ForegroundColor $Yellow
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "! $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Red
}

function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."

    $missing = @()

    # Check Python
    if (-not (Test-Command "python")) {
        $missing += "Python 3.11+"
    } else {
        $pythonVersion = python --version 2>&1
        Write-Host "  Found: $pythonVersion" -ForegroundColor Gray
    }

    # Check Node.js
    if (-not (Test-Command "node")) {
        $missing += "Node.js 18+"
    } else {
        $nodeVersion = node --version 2>&1
        Write-Host "  Found: Node.js $nodeVersion" -ForegroundColor Gray
    }

    # Check npm
    if (-not (Test-Command "npm")) {
        $missing += "npm"
    }

    # Check Git
    if (-not (Test-Command "git")) {
        $missing += "Git"
    }

    if ($missing.Count -gt 0) {
        Write-Error "Missing prerequisites:"
        foreach ($item in $missing) {
            Write-Host "  - $item" -ForegroundColor $Red
        }
        Write-Host ""
        Write-Host "Please install the missing prerequisites and try again."
        Write-Host ""
        Write-Host "Quick install options:" -ForegroundColor $Yellow
        Write-Host "  Python: winget install Python.Python.3.11"
        Write-Host "  Node.js: winget install OpenJS.NodeJS.LTS"
        Write-Host "  Git: winget install Git.Git"
        exit 1
    }

    Write-Success "All prerequisites satisfied"
}

function New-EnvFile {
    Write-Step "Setting up environment variables..."

    if (Test-Path ".env") {
        $overwrite = Read-Host "  .env file exists. Overwrite? (y/N)"
        if ($overwrite -ne "y" -and $overwrite -ne "Y") {
            Write-Warning "Keeping existing .env file"
            return
        }
    }

    Copy-Item ".env.example" ".env" -Force

    Write-Host ""
    Write-Host "🔑 API Key Configuration" -ForegroundColor $Blue
    Write-Host "  Enter your API keys (press Enter to skip and configure later)"
    Write-Host ""

    # OpenAI
    $openaiKey = Read-Host "  OpenAI API Key (required for AI features)"
    if ($openaiKey) {
        (Get-Content .env) -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$openaiKey" | Set-Content .env
    }

    # MongoDB
    $mongoUri = Read-Host "  MongoDB URI (or press Enter for local)"
    if ($mongoUri) {
        (Get-Content .env) -replace "MONGODB_URI=.*", "MONGODB_URI=$mongoUri" | Set-Content .env
    } else {
        (Get-Content .env) -replace "MONGODB_URI=.*", "MONGODB_URI=mongodb://localhost:27017/randols_marketing" | Set-Content .env
    }

    # Generate secrets
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

    (Get-Content .env) -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey" | Set-Content .env
    (Get-Content .env) -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$jwtSecret" | Set-Content .env

    Write-Success "Environment file configured"
}

function Install-Backend {
    Write-Step "📦 Setting up backend..."

    Push-Location backend

    # Create virtual environment
    if (-not (Test-Path "venv")) {
        python -m venv venv
    }

    # Activate and install
    & .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q

    # Download NLTK data
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)" 2>$null

    deactivate
    Pop-Location

    Write-Success "Backend setup complete"
}

function Install-Frontend {
    Write-Step "📦 Setting up frontend..."

    Push-Location frontend
    npm install --silent 2>$null
    Pop-Location

    Write-Success "Frontend setup complete"
}

function Initialize-Database {
    Write-Step "🗄️ Initializing database..."

    Push-Location backend
    & .\venv\Scripts\Activate.ps1

    try {
        python scripts/init_db.py --samples 2>$null
        Write-Success "Database initialized"
    } catch {
        Write-Warning "Database initialization skipped (MongoDB may not be running)"
        Write-Host "  Start MongoDB and run: python scripts/init_db.py" -ForegroundColor Gray
    }

    deactivate
    Pop-Location
}

function Write-Completion {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $Green
    Write-Host "🚀 Setup Complete!" -ForegroundColor $Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Quick Start Commands:" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "  Start Development Servers:" -ForegroundColor $Yellow
    Write-Host "    make dev"
    Write-Host ""
    Write-Host "  Or start separately:" -ForegroundColor $Yellow
    Write-Host "    Backend:  cd backend; .\venv\Scripts\Activate.ps1; python main.py"
    Write-Host "    Frontend: cd frontend; npm run dev"
    Write-Host ""
    Write-Host "  With Docker:" -ForegroundColor $Yellow
    Write-Host "    docker-compose up"
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor $Blue
    Write-Host "  Frontend:  http://localhost:3000"
    Write-Host "  Backend:   http://localhost:5000"
    Write-Host "  API Docs:  http://localhost:5000/api/v1/docs"
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor $Blue
    Write-Host "  1. Configure your social media API keys in .env"
    Write-Host "  2. Set up MongoDB (local or Atlas)"
    Write-Host "  3. Run: make dev"
    Write-Host ""
}

# Main execution
function Main {
    Write-Banner

    Test-Prerequisites
    Write-Host ""

    New-EnvFile
    Write-Host ""

    Install-Backend
    Install-Frontend
    Write-Host ""

    Initialize-Database

    Write-Completion
}

# Run
Main
