#!/bin/bash

################################################################################
# Bob AI Session Export Script
# Exports the complete IBM Dexter project with Bob configuration
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="IBM_Dexter_AI_Code_Reviewer"
EXPORT_DATE=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="$HOME/Desktop/${PROJECT_NAME}_Export_${EXPORT_DATE}"
ARCHIVE_NAME="${PROJECT_NAME}_${EXPORT_DATE}"
CURRENT_DIR=$(pwd)

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Print section header
print_header() {
    echo ""
    print_msg "$BLUE" "═══════════════════════════════════════════════════════"
    print_msg "$BLUE" "  $1"
    print_msg "$BLUE" "═══════════════════════════════════════════════════════"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

################################################################################
# Main Export Process
################################################################################

print_header "🚀 Bob AI Session Export"
print_msg "$GREEN" "Project: $PROJECT_NAME"
print_msg "$GREEN" "Export Directory: $EXPORT_DIR"
echo ""

# Step 1: Create export directory
print_header "📁 Creating Export Directory"
mkdir -p "$EXPORT_DIR"
print_msg "$GREEN" "✓ Created: $EXPORT_DIR"

# Step 2: Copy project files
print_header "📦 Copying Project Files"

# Core directories
print_msg "$YELLOW" "Copying backend..."
cp -r backend "$EXPORT_DIR/" 2>/dev/null || print_msg "$RED" "⚠ Backend directory not found"

print_msg "$YELLOW" "Copying frontend..."
cp -r frontend "$EXPORT_DIR/" 2>/dev/null || print_msg "$RED" "⚠ Frontend directory not found"

print_msg "$YELLOW" "Copying documentation..."
cp -r docs "$EXPORT_DIR/" 2>/dev/null || print_msg "$RED" "⚠ Docs directory not found"

print_msg "$YELLOW" "Copying Bob configuration..."
cp -r .bob "$EXPORT_DIR/" 2>/dev/null || print_msg "$RED" "⚠ .bob directory not found"

print_msg "$YELLOW" "Copying skills..."
cp -r skills "$EXPORT_DIR/" 2>/dev/null || print_msg "$RED" "⚠ Skills directory not found"

# Root files
print_msg "$YELLOW" "Copying root documentation files..."
for file in *.md; do
    [ -f "$file" ] && cp "$file" "$EXPORT_DIR/"
done

# Configuration files
print_msg "$YELLOW" "Copying configuration files..."
[ -f ".gitignore" ] && cp .gitignore "$EXPORT_DIR/"
[ -f "package.json" ] && cp package.json "$EXPORT_DIR/"
[ -f "package-lock.json" ] && cp package-lock.json "$EXPORT_DIR/"

print_msg "$GREEN" "✓ Project files copied"

# Step 3: Clean up sensitive data
print_header "🔐 Cleaning Sensitive Data"

# Remove .env files (keep .env.example)
find "$EXPORT_DIR" -name ".env" -type f -delete 2>/dev/null || true
print_msg "$GREEN" "✓ Removed .env files"

# Remove node_modules
find "$EXPORT_DIR" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
print_msg "$GREEN" "✓ Removed node_modules"

# Remove Python virtual environments
find "$EXPORT_DIR" -name "venv" -type d -exec rm -rf {} + 2>/dev/null || true
find "$EXPORT_DIR" -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
print_msg "$GREEN" "✓ Removed Python virtual environments"

# Remove __pycache__
find "$EXPORT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
print_msg "$GREEN" "✓ Removed Python cache"

# Remove build artifacts
find "$EXPORT_DIR" -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
find "$EXPORT_DIR" -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
print_msg "$GREEN" "✓ Removed build artifacts"

# Remove database files
find "$EXPORT_DIR" -name "*.db" -type f -delete 2>/dev/null || true
find "$EXPORT_DIR" -name "*.sqlite" -type f -delete 2>/dev/null || true
print_msg "$GREEN" "✓ Removed database files"

# Remove log files
find "$EXPORT_DIR" -name "*.log" -type f -delete 2>/dev/null || true
print_msg "$GREEN" "✓ Removed log files"

# Step 4: Generate session summary
print_header "📝 Generating Session Summary"

cat > "$EXPORT_DIR/SESSION_SUMMARY.md" << 'EOF'
# Bob AI Session Summary

## Export Information
- **Export Date:** $(date +"%Y-%m-%d %H:%M:%S")
- **Project:** IBM Dexter AI Code Reviewer
- **Bob Version:** Latest

## Project Overview
This export contains the complete IBM Dexter AI Code Reviewer project, including:
- Backend FastAPI application
- React frontend with Carbon Design
- Multi-agent AI system
- Bob AI configuration and skills
- Comprehensive documentation

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.production.example .env.production
# Edit .env.production with your API URL
npm run dev
```

## Key Features
- ✅ Multi-agent AI architecture
- ✅ Pull request review automation
- ✅ RAG pipeline for context-aware reviews
- ✅ IBM ecosystem integration (watsonx.ai, Db2)
- ✅ Engineering analytics and governance
- ✅ Modern React UI with Carbon Design

## Documentation
- `BOB_SESSION_EXPORT_GUIDE.md` - Complete export guide
- `README.md` - Project overview
- `backend/INSTALL.md` - Backend setup
- `frontend/QUICK_START.md` - Frontend guide
- `docs/` - Architecture and planning docs

## Bob AI Configuration
- `.bob/config/skill-loader.json` - Skill auto-loading
- `.bob/config/auto-loader.py` - Skill loader script
- `skills/` - Custom Bob skills

## Support
For questions or issues, refer to the documentation files included in this export.

---
**Made with Bob AI** 🤖
EOF

# Replace $(date) with actual date
sed -i.bak "s/\$(date +\"%Y-%m-%d %H:%M:%S\")/$(date +"%Y-%m-%d %H:%M:%S")/g" "$EXPORT_DIR/SESSION_SUMMARY.md" 2>/dev/null || true
rm -f "$EXPORT_DIR/SESSION_SUMMARY.md.bak" 2>/dev/null || true

print_msg "$GREEN" "✓ Session summary generated"

# Step 5: Create file inventory
print_header "📋 Creating File Inventory"

cat > "$EXPORT_DIR/FILE_INVENTORY.txt" << EOF
IBM Dexter AI Code Reviewer - File Inventory
Generated: $(date +"%Y-%m-%d %H:%M:%S")
================================================================================

EOF

# Count files by type
echo "File Statistics:" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
echo "----------------" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f | wc -l | xargs echo "Total Files:" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type d | wc -l | xargs echo "Total Directories:" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
echo "" >> "$EXPORT_DIR/FILE_INVENTORY.txt"

echo "File Types:" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
echo "-----------" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f -name "*.py" | wc -l | xargs echo "Python files (.py):" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f -name "*.js" -o -name "*.jsx" | wc -l | xargs echo "JavaScript files (.js/.jsx):" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f -name "*.md" | wc -l | xargs echo "Markdown files (.md):" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f -name "*.json" | wc -l | xargs echo "JSON files (.json):" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
find "$EXPORT_DIR" -type f -name "*.skill" | wc -l | xargs echo "Bob skills (.skill):" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
echo "" >> "$EXPORT_DIR/FILE_INVENTORY.txt"

echo "Directory Structure:" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
echo "-------------------" >> "$EXPORT_DIR/FILE_INVENTORY.txt"
tree -L 2 "$EXPORT_DIR" >> "$EXPORT_DIR/FILE_INVENTORY.txt" 2>/dev/null || \
    find "$EXPORT_DIR" -maxdepth 2 -type d >> "$EXPORT_DIR/FILE_INVENTORY.txt"

print_msg "$GREEN" "✓ File inventory created"

# Step 6: Create archives
print_header "🗜️  Creating Archives"

cd "$HOME/Desktop"

# Create tar.gz archive
if command_exists tar; then
    print_msg "$YELLOW" "Creating tar.gz archive..."
    tar -czf "${ARCHIVE_NAME}.tar.gz" "$(basename "$EXPORT_DIR")"
    ARCHIVE_SIZE=$(du -h "${ARCHIVE_NAME}.tar.gz" | cut -f1)
    print_msg "$GREEN" "✓ Created: ${ARCHIVE_NAME}.tar.gz ($ARCHIVE_SIZE)"
fi

# Create zip archive
if command_exists zip; then
    print_msg "$YELLOW" "Creating zip archive..."
    zip -r -q "${ARCHIVE_NAME}.zip" "$(basename "$EXPORT_DIR")"
    ZIP_SIZE=$(du -h "${ARCHIVE_NAME}.zip" | cut -f1)
    print_msg "$GREEN" "✓ Created: ${ARCHIVE_NAME}.zip ($ZIP_SIZE)"
fi

cd "$CURRENT_DIR"

# Step 7: Generate export report
print_header "📊 Export Report"

cat > "$EXPORT_DIR/EXPORT_REPORT.txt" << EOF
IBM Dexter AI Code Reviewer - Export Report
================================================================================

Export Date: $(date +"%Y-%m-%d %H:%M:%S")
Export Location: $EXPORT_DIR
Archive Location: $HOME/Desktop/

Archives Created:
EOF

[ -f "$HOME/Desktop/${ARCHIVE_NAME}.tar.gz" ] && echo "  ✓ ${ARCHIVE_NAME}.tar.gz" >> "$EXPORT_DIR/EXPORT_REPORT.txt"
[ -f "$HOME/Desktop/${ARCHIVE_NAME}.zip" ] && echo "  ✓ ${ARCHIVE_NAME}.zip" >> "$EXPORT_DIR/EXPORT_REPORT.txt"

cat >> "$EXPORT_DIR/EXPORT_REPORT.txt" << EOF

Export Contents:
  ✓ Backend application (Python/FastAPI)
  ✓ Frontend application (React/Carbon Design)
  ✓ Documentation (Markdown files)
  ✓ Bob AI configuration (.bob/)
  ✓ Custom Bob skills (skills/)
  ✓ Session summary
  ✓ File inventory

Cleaned Items:
  ✓ Removed .env files (kept .env.example)
  ✓ Removed node_modules
  ✓ Removed Python virtual environments
  ✓ Removed __pycache__
  ✓ Removed build artifacts
  ✓ Removed database files
  ✓ Removed log files

Next Steps:
  1. Review the exported files in: $EXPORT_DIR
  2. Check archives on Desktop: ${ARCHIVE_NAME}.tar.gz / .zip
  3. Read BOB_SESSION_EXPORT_GUIDE.md for restoration instructions
  4. Store archives in a secure backup location

For restoration instructions, see:
  - BOB_SESSION_EXPORT_GUIDE.md
  - SESSION_SUMMARY.md

================================================================================
Export completed successfully!
EOF

print_msg "$GREEN" "✓ Export report generated"

# Final summary
print_header "✅ Export Complete!"
echo ""
print_msg "$GREEN" "Export Directory: $EXPORT_DIR"
[ -f "$HOME/Desktop/${ARCHIVE_NAME}.tar.gz" ] && print_msg "$GREEN" "Archive (tar.gz): $HOME/Desktop/${ARCHIVE_NAME}.tar.gz"
[ -f "$HOME/Desktop/${ARCHIVE_NAME}.zip" ] && print_msg "$GREEN" "Archive (zip): $HOME/Desktop/${ARCHIVE_NAME}.zip"
echo ""
print_msg "$BLUE" "📖 Read BOB_SESSION_EXPORT_GUIDE.md for detailed information"
print_msg "$BLUE" "📋 Check EXPORT_REPORT.txt for export details"
print_msg "$BLUE" "📝 Review SESSION_SUMMARY.md for quick start guide"
echo ""
print_msg "$YELLOW" "💡 Tip: Store the archives in a secure backup location"
echo ""

# Open export directory (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_msg "$BLUE" "Opening export directory..."
    open "$EXPORT_DIR"
fi

exit 0

# Made with Bob
