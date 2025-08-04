#!/usr/bin/env python3
"""
Flask Structure Validation Script for AcidTech API
Validates that all Flask components are properly configured
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return Path(file_path).exists()

def validate_flask_structure():
    """Validate Flask project structure"""
    
    print("Validating AcidTech Flask API Structure...\n")
    
    # Core Flask files
    core_files = {
        "Entry Point": "run.py",
        "Environment Config": ".env",
        "Requirements": "requirements.txt",
        "Flask Factory": "app/__init__.py",
        "Configuration": "app/config.py"
    }
    
    # Model files
    model_files = {
        "Models Init": "app/models/__init__.py",
        "Base Model": "app/models/base.py",
        "User Model": "app/models/user.py",
        "Transaction Model": "app/models/transaction.py",
        "Purchase Order Model": "app/models/purchase_order.py",
        "System Log Model": "app/models/system_log.py"
    }
    
    # Route files
    route_files = {
        "Auth Routes": "app/routes/auth.py",
        "Transaction Routes": "app/routes/transactions.py",
        "Purchase Order Routes": "app/routes/purchase_orders.py",
        "System Log Routes": "app/routes/system_logs.py"
    }
    
    # Service files
    service_files = {
        "Auth Service": "app/services/auth_service.py",
        "Database Service": "app/services/db_service.py",
        "API Client Service": "app/services/api_client.py"
    }
    
    # Middleware files
    middleware_files = {
        "Middleware Init": "app/middleware/__init__.py",
        "Auth Middleware": "app/middleware/auth_middleware.py",
        "Logging Middleware": "app/middleware/logging_middleware.py",
        "Rate Limiting": "app/middleware/rate_limiting.py"
    }
    
    # Test files
    test_files = {
        "Tests Init": "tests/__init__.py",
        "Test Config": "tests/conftest.py",
        "Basic Tests": "tests/test_basic.py"
    }
    
    all_files = {
        "Core Files": core_files,
        "Models": model_files,
        "Routes": route_files,
        "Services": service_files,
        "Middleware": middleware_files,
        "Tests": test_files
    }
    
    total_files = 0
    found_files = 0
    missing_files = []
    
    for category, files in all_files.items():
        print(f"{category}")
        print("-" * 40)
        
        for name, file_path in files.items():
            total_files += 1
            if check_file_exists(file_path):
                print(f"[OK] {name}: {file_path}")
                found_files += 1
            else:
                print(f"[MISSING] {name}: {file_path}")
                missing_files.append(file_path)
        
        print()
    
    # Summary
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Files Expected: {total_files}")
    print(f"Files Found: {found_files}")
    print(f"Files Missing: {len(missing_files)}")
    print(f"Completion: {(found_files/total_files)*100:.1f}%")
    
    if missing_files:
        print(f"\nMissing Files:")
        for file in missing_files:
            print(f"   - {file}")
    
    # Additional checks
    print(f"\nAdditional Validations:")
    
    # Check if .env has required variables
    if check_file_exists('.env'):
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                required_vars = [
                    'FLASK_ENV', 'SECRET_KEY', 'AZURE_TENANT_ID', 
                    'AZURE_CLIENT_ID', 'AZURE_B2C_AUTHORITY'
                ]
                missing_vars = [var for var in required_vars if var not in env_content]
                
                if not missing_vars:
                    print("[OK] Environment variables configured")
                else:
                    print(f"[WARNING] Missing environment variables: {missing_vars}")
        except Exception as e:
            print(f"[ERROR] Error reading .env file: {e}")
    
    # Check if requirements.txt has Flask
    if check_file_exists('requirements.txt'):
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                if 'Flask==' in requirements:
                    print("[OK] Flask dependency configured")
                else:
                    print("[ERROR] Flask dependency not found in requirements.txt")
        except Exception as e:
            print(f"[ERROR] Error reading requirements.txt: {e}")
    
    # Directory structure check
    required_dirs = ['app', 'app/models', 'app/routes', 'app/services', 'app/middleware', 'tests']
    missing_dirs = [d for d in required_dirs if not Path(d).is_dir()]
    
    if not missing_dirs:
        print("[OK] Directory structure complete")
    else:
        print(f"[ERROR] Missing directories: {missing_dirs}")
    
    print(f"\n{'FLASK STRUCTURE VALIDATION COMPLETE!' if not missing_files else 'FLASK STRUCTURE NEEDS ATTENTION'}")
    
    return len(missing_files) == 0

def validate_imports():
    """Validate that imports work correctly"""
    print(f"\nValidating Python Imports...")
    
    try:
        # Test Flask app creation
        from app import create_app
        app = create_app('testing')
        print("[OK] Flask app creation successful")
        
        # Test configuration
        from app.config import get_config, validate_config
        config = get_config()
        validation = validate_config()
        print("[OK] Configuration validation successful")
        
        # Test models
        from app.models import User, Transaction, PurchaseOrder, SystemLog
        print("[OK] Model imports successful")
        
        # Test services
        from app.services.auth_service import auth_service
        from app.services.db_service import db_service
        from app.services.api_client import api_client
        print("[OK] Service imports successful")
        
        # Test middleware
        from app.middleware import auth_required, require_roles
        print("[OK] Middleware imports successful")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Validation error: {e}")
        return False

if __name__ == "__main__":
    print("AcidTech Flask API - Structure Validation")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Validate structure
    structure_valid = validate_flask_structure()
    
    # Validate imports (only if structure is mostly complete)
    if structure_valid:
        imports_valid = validate_imports()
        
        if structure_valid and imports_valid:
            print(f"\nFlask API is ready for development!")
            print(f"Next steps:")
            print(f"   1. Run: pip install -r requirements.txt")
            print(f"   2. Run: python run.py")
            print(f"   3. Test: curl http://localhost:8000/health")
            sys.exit(0)
        else:
            print(f"\nSome issues found. Please fix them before proceeding.")
            sys.exit(1)
    else:
        print(f"\nFlask structure incomplete. Please ensure all files are created.")
        sys.exit(1)