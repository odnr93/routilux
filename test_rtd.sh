#!/bin/bash
# Test Read the Docs configuration locally
# This script simulates the Read the Docs build process

set -e  # Exit on error

echo "=========================================="
echo "Testing Read the Docs Configuration"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Validate .readthedocs.yml
echo -e "${YELLOW}Step 1: Validating .readthedocs.yml${NC}"
if [ ! -f .readthedocs.yml ]; then
    echo -e "${RED}✗ .readthedocs.yml not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ .readthedocs.yml found${NC}"

# Check if yamllint is available (optional)
if command -v yamllint &> /dev/null; then
    echo "  Running yamllint..."
    yamllint .readthedocs.yml || echo "  Warning: yamllint found issues (non-critical)"
fi

# Step 2: Check Python version
echo ""
echo -e "${YELLOW}Step 2: Checking Python version${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "  Python version: $PYTHON_VERSION"
if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l 2>/dev/null || echo "0") == "1" ]] || [[ "$PYTHON_VERSION" == "3.11" ]]; then
    echo -e "${GREEN}✓ Python version OK${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Read the Docs uses Python 3.11, you have $PYTHON_VERSION${NC}"
fi

# Step 3: Install package with docs dependencies
echo ""
echo -e "${YELLOW}Step 3: Installing package with docs dependencies${NC}"
echo "  Running: pip install -e '.[docs]'"
pip install -e ".[docs]" || {
    echo -e "${RED}✗ Failed to install package with docs dependencies${NC}"
    exit 1
}
echo -e "${GREEN}✓ Package installed successfully${NC}"

# Step 4: Verify Sphinx configuration
echo ""
echo -e "${YELLOW}Step 4: Verifying Sphinx configuration${NC}"
if [ ! -f docs/source/conf.py ]; then
    echo -e "${RED}✗ docs/source/conf.py not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Sphinx configuration found${NC}"

# Step 5: Build documentation
echo ""
echo -e "${YELLOW}Step 5: Building documentation${NC}"
echo "  This simulates the Read the Docs build process..."
echo "  Note: Warnings are allowed (Read the Docs uses fail_on_warning: false)"
cd docs
sphinx-build -b html source build/html || {
    echo -e "${RED}✗ Documentation build failed! Check errors above.${NC}"
    cd ..
    exit 1
}
cd ..

# Step 6: Verify build output
echo ""
echo -e "${YELLOW}Step 6: Verifying build output${NC}"
if [ -f docs/build/html/index.html ]; then
    echo -e "${GREEN}✓ Documentation built successfully!${NC}"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}All checks passed!${NC}"
    echo "=========================================="
    echo ""
    echo "Documentation output: docs/build/html/index.html"
    echo "You can open it in your browser to verify."
    echo ""
    echo "To view the documentation:"
    echo "  python3 -m http.server 8000 -d docs/build/html"
    echo "  Then open http://localhost:8000 in your browser"
else
    echo -e "${RED}✗ Build output not found!${NC}"
    exit 1
fi

