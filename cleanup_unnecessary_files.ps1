#!/usr/bin/env powershell
<#
.SYNOPSIS
    Cleanup Script - Remove All Unnecessary Migration and Test Files
.DESCRIPTION
    Removes all temporary files, migration scripts, test files, and SQLite databases
    that are no longer needed after successful MySQL migration.
.NOTES
    Run this script from the Intern-Work directory
#>

Write-Host "🧹 CLEANUP: Removing Unnecessary Files After MySQL Migration" -ForegroundColor Cyan
Write-Host "=" * 70

# List of migration and test files to remove
$filesToRemove = @(
    # Migration Scripts (no longer needed)
    "migrate_books.py",
    "migrate_orders_complete.py",
    "final_complete_migration.py", 
    "complete_remaining.py",
    "complete_migrate.py",
    "final_migrate.py",
    "migrate_to_mysql.py",
    "simple_migrate.py",
    
    # Test and Debug Scripts
    "quick_test.py",
    "test_migrate.py",
    "test_one_user.py",
    "test_admin.py",
    "test_admin_fix.py",
    "test_fix.py",
    "test_orders.py",
    "check_database.py",
    "debug_books_issue.py",
    "debug_books.py",
    "verify_orders.py",
    "verify_mysql_migration.py",
    "test_migration.bat",
    
    # Setup Scripts (already completed)
    "setup_mysql_only.py",
    "setup_mysql.py",
    
    # Sample Data Scripts (replaced by realistic generator)
    "add_book_images.py",
    "add_sample_books.py",
    "add_sample_reviews.py",
    "add_mock_orders.py",
    
    # Order Creation Scripts (replaced by generate_realistic_orders.py)
    "create_mysql_orders.py",
    "create_analysis_orders.py",
    "create_analytics_orders.py",
    "simple_orders_creator.py",
    "simple_orders_test.py",
    "quick_orders_test.py",
    "quick_realistic_orders.py",
    "fresh_orders_mysql.py",
    "generate_orders_mysql.py",
    "generate_realistic_analysis_orders.py",
    
    # Analytics Scripts (replaced by comprehensive version)
    "analytics_report.py",
    "analytics_summary.py",
    "advanced_analytics_dashboard.py",
    "comprehensive_analytics.py",
    
    # SQLite Database Files
    "instance\shopping_site.db",
    "..\instance\shopping_site.db",
    "shopping_site.db",
    "shopping_site.db.backup",
    
    # Log Files
    "migration_error.log",
    "migration_output.log",
    "migration_output.txt",
    "migration.log",
    
    # Temporary Files
    "query"
)

# Directories to remove
$dirsToRemove = @(
    "__pycache__",  # Python cache (will be regenerated)
    "instance"      # Contains SQLite database
)

$removedCount = 0
$skippedCount = 0

Write-Host "📋 Files to be removed:" -ForegroundColor Yellow
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   - $file (not found)" -ForegroundColor Gray
    }
}

Write-Host "`n📁 Directories to be removed:" -ForegroundColor Yellow
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Write-Host "   ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "   - $dir (not found)" -ForegroundColor Gray
    }
}

Write-Host "`n⚠️  IMPORTANT: This will permanently delete these files!" -ForegroundColor Red
$confirmation = Read-Host "Do you want to proceed? (y/N)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "❌ Cleanup cancelled by user." -ForegroundColor Red
    exit 1
}

Write-Host "`n🗑️  Starting cleanup..." -ForegroundColor Cyan

# Remove individual files
Write-Host "`n📄 Removing files..." -ForegroundColor Yellow
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force -ErrorAction Stop
            Write-Host "   ✅ Removed: $file" -ForegroundColor Green
            $removedCount++
        }
        catch {
            Write-Host "   ❌ Failed to remove: $file - $($_.Exception.Message)" -ForegroundColor Red
            $skippedCount++
        }
    }
}

# Remove directories
Write-Host "`n📁 Removing directories..." -ForegroundColor Yellow
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        try {
            Remove-Item $dir -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removed directory: $dir" -ForegroundColor Green
            $removedCount++
        }
        catch {
            Write-Host "   ❌ Failed to remove directory: $dir - $($_.Exception.Message)" -ForegroundColor Red
            $skippedCount++
        }
    }
}

Write-Host "`n🎉 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "   • Files/Directories Removed: $removedCount" -ForegroundColor Green
Write-Host "   • Skipped/Failed: $skippedCount" -ForegroundColor Yellow

Write-Host "`n📁 Essential Files Preserved:" -ForegroundColor Green
$essentialFiles = @(
    "app.py",
    "model.py", 
    "generate_realistic_orders.py",
    "export_database_to_csv.py",
    ".env",
    "requirements.txt",
    "README.md",
    "MYSQL_MIGRATION_GUIDE.md"
)

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $file (missing - you may need this)" -ForegroundColor Yellow
    }
}

Write-Host "`n📂 Essential Directories Preserved:" -ForegroundColor Green
$essentialDirs = @("templates", "static", "env", "database_exports")
foreach ($dir in $essentialDirs) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir\" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $dir\ (missing)" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Cleanup Complete!" -ForegroundColor Green
Write-Host "Your MySQL bookstore is now clean and production-ready!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Verify your Flask app runs: python app.py" -ForegroundColor White
Write-Host "   2. Test the website: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "   3. Generate fresh data: python generate_realistic_orders.py" -ForegroundColor White
Write-Host "   4. Ready for git commit and deployment!" -ForegroundColor White

# Pause to let user see the results
Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
