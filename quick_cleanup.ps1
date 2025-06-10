# Quick Cleanup Command - Run this in PowerShell from Intern-Work directory
# Removes all unnecessary migration and test files in one go

# One-liner cleanup command:
Remove-Item -Force -ErrorAction SilentlyContinue migrate_books.py,migrate_orders_complete.py,final_complete_migration.py,complete_remaining.py,complete_migrate.py,final_migrate.py,migrate_to_mysql.py,simple_migrate.py,quick_test.py,test_migrate.py,test_one_user.py,test_admin.py,test_admin_fix.py,test_fix.py,test_orders.py,check_database.py,debug_books_issue.py,debug_books.py,verify_orders.py,verify_mysql_migration.py,test_migration.bat,setup_mysql_only.py,setup_mysql.py,add_book_images.py,add_sample_books.py,add_sample_reviews.py,add_mock_orders.py,create_mysql_orders.py,create_analysis_orders.py,create_analytics_orders.py,simple_orders_creator.py,simple_orders_test.py,quick_orders_test.py,quick_realistic_orders.py,fresh_orders_mysql.py,generate_orders_mysql.py,generate_realistic_analysis_orders.py,analytics_report.py,analytics_summary.py,advanced_analytics_dashboard.py,comprehensive_analytics.py,"instance\shopping_site.db",shopping_site.db,migration_error.log,migration_output.log,migration_output.txt,migration.log,query; Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__,instance; Write-Host "✅ Cleanup completed - All unnecessary files removed!" -ForegroundColor Green

# Alternative: Run the comprehensive cleanup script
# .\cleanup_unnecessary_files.ps1
