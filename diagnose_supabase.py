
#!/usr/bin/env python3
"""
Supabase Diagnostic Tool
Identifies and suggests fixes for common Supabase issues
"""

import os
import re
import psycopg2
from datetime import datetime

def check_environment():
    """Check environment configuration"""
    issues = []
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        issues.append({
            "type": "critical",
            "message": "DATABASE_URL environment variable not set",
            "fix": "Set DATABASE_URL in Replit Secrets"
        })
        return issues
    
    # Validate URL format
    if not database_url.startswith('postgresql://'):
        issues.append({
            "type": "critical",
            "message": "DATABASE_URL should start with 'postgresql://'",
            "fix": "Check your DATABASE_URL format"
        })
    
    # Check if URL contains password
    if '[YOUR-PASSWORD]' in database_url or 'your-password' in database_url.lower():
        issues.append({
            "type": "critical",
            "message": "DATABASE_URL contains placeholder password",
            "fix": "Replace [YOUR-PASSWORD] with your actual Supabase password"
        })
    
    return issues

def check_database_connectivity():
    """Check database connectivity and common issues"""
    issues = []
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        return [{"type": "critical", "message": "Cannot check connectivity - DATABASE_URL not set"}]
    
    try:
        # Test basic connection
        conn = psycopg2.connect(database_url)
        conn.close()
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).lower()
        
        if 'password authentication failed' in error_msg:
            issues.append({
                "type": "critical",
                "message": "Password authentication failed",
                "fix": "Check your Supabase password in DATABASE_URL"
            })
        elif 'connection timed out' in error_msg or 'could not connect' in error_msg:
            issues.append({
                "type": "warning",
                "message": "Connection timeout - database may be sleeping",
                "fix": "Wait a moment and try again, or run keep-alive to wake database"
            })
        elif 'ssl required' in error_msg:
            issues.append({
                "type": "critical",
                "message": "SSL connection required",
                "fix": "Add '?sslmode=require' to your DATABASE_URL"
            })
        else:
            issues.append({
                "type": "error",
                "message": f"Database connection failed: {e}",
                "fix": "Check your DATABASE_URL and Supabase project status"
            })
    
    except Exception as e:
        issues.append({
            "type": "error",
            "message": f"Unexpected connection error: {e}",
            "fix": "Check your DATABASE_URL format and Supabase project"
        })
    
    return issues

def check_dependencies():
    """Check required dependencies"""
    issues = []
    
    try:
        import psycopg2
    except ImportError:
        issues.append({
            "type": "critical",
            "message": "psycopg2 not installed",
            "fix": "Run: pip install psycopg2-binary"
        })
    
    return issues

def check_keep_alive_files():
    """Check if keep-alive files exist and are configured"""
    issues = []
    
    required_files = [
        'supabase_keepalive.py',
        'keep_alive_daemon.py',
        'test_supabase_connection.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            issues.append({
                "type": "warning",
                "message": f"Missing file: {file}",
                "fix": f"Ensure {file} exists in your project"
            })
    
    return issues

def run_full_diagnosis():
    """Run complete diagnostic"""
    print("🔧 Supabase Diagnostic Tool")
    print("=" * 50)
    
    all_issues = []
    
    # Check environment
    print("1️⃣ Environment Configuration...")
    env_issues = check_environment()
    all_issues.extend(env_issues)
    
    # Check dependencies
    print("2️⃣ Dependencies...")
    dep_issues = check_dependencies()
    all_issues.extend(dep_issues)
    
    # Check files
    print("3️⃣ Keep-Alive Files...")
    file_issues = check_keep_alive_files()
    all_issues.extend(file_issues)
    
    # Check connectivity (only if no critical issues so far)
    critical_issues = [i for i in all_issues if i['type'] == 'critical']
    if not critical_issues:
        print("4️⃣ Database Connectivity...")
        conn_issues = check_database_connectivity()
        all_issues.extend(conn_issues)
    
    # Report results
    print("\n" + "=" * 50)
    print("📋 Diagnostic Results:")
    
    if not all_issues:
        print("✅ No issues found! Your Supabase setup looks good.")
        return True
    
    # Group issues by type
    critical = [i for i in all_issues if i['type'] == 'critical']
    errors = [i for i in all_issues if i['type'] == 'error']
    warnings = [i for i in all_issues if i['type'] == 'warning']
    
    if critical:
        print(f"\n🚨 Critical Issues ({len(critical)}):")
        for issue in critical:
            print(f"   ❌ {issue['message']}")
            print(f"      💡 Fix: {issue['fix']}")
    
    if errors:
        print(f"\n⚠️  Errors ({len(errors)}):")
        for issue in errors:
            print(f"   ❌ {issue['message']}")
            print(f"      💡 Fix: {issue['fix']}")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for issue in warnings:
            print(f"   ⚠️  {issue['message']}")
            print(f"      💡 Fix: {issue['fix']}")
    
    print(f"\n📊 Total issues found: {len(all_issues)}")
    return len(critical) == 0

if __name__ == "__main__":
    success = run_full_diagnosis()
    if not success:
        print("\n🔧 Please fix the critical issues above and run the diagnosis again.")
    else:
        print("\n✅ You can now test your Supabase connection with: python test_supabase_connection.py")
