# Testing Read the Docs Configuration Locally

This guide explains how to test your Read the Docs configuration locally before pushing to GitHub.

## Method 1: Using Makefile (Recommended)

The easiest way to test the Read the Docs configuration:

```bash
make test-rtd
```

This will:
1. Install the package with docs dependencies
2. Build the documentation using Sphinx
3. Verify the build was successful

## Method 2: Using Test Script

Run the comprehensive test script:

```bash
./test_rtd.sh
```

This script performs:
- ✅ Validates `.readthedocs.yml` format
- ✅ Checks Python version compatibility
- ✅ Installs package with docs dependencies
- ✅ Verifies Sphinx configuration
- ✅ Builds documentation
- ✅ Verifies build output

## Method 3: Manual Testing

### Step 1: Install Dependencies

```bash
# Install the package with documentation dependencies
pip install -e ".[docs]"
```

### Step 2: Build Documentation

```bash
cd docs
make html
```

### Step 3: Verify Output

Check that `docs/build/html/index.html` was created successfully.

### Step 4: View Documentation

```bash
# Start a local web server
python3 -m http.server 8000 -d docs/build/html

# Open in browser
# http://localhost:8000
```

## Method 4: Using Docker (Most Accurate)

This method uses Docker to simulate the exact Read the Docs build environment:

### Prerequisites

Install Docker if not already installed.

### Build with Docker

```bash
# Pull Read the Docs build image
docker pull readthedocs/build:latest

# Run the build (adjust paths as needed)
docker run --rm -it \
  -v $(pwd):/home/docs \
  -w /home/docs \
  readthedocs/build:latest \
  bash -c "pip install -e '.[docs]' && cd docs && make html"
```

## Method 5: Using readthedocs-build (Official Tool)

Install and use the official Read the Docs build tool:

```bash
# Install readthedocs-build
pip install readthedocs-build

# Run the build
readthedocs-build
```

## Common Issues and Solutions

### Issue: Import Errors

**Problem**: Sphinx can't import your package modules.

**Solution**: Ensure the package is installed in editable mode:
```bash
pip install -e ".[docs]"
```

### Issue: Missing Dependencies

**Problem**: Build fails due to missing packages.

**Solution**: Check that all dependencies are in `pyproject.toml` under `[project.optional-dependencies.docs]`.

### Issue: Configuration Errors

**Problem**: `.readthedocs.yml` validation errors.

**Solution**: 
- Validate YAML syntax: `yamllint .readthedocs.yml`
- Check Read the Docs v2 documentation format
- Ensure all required fields are present

### Issue: Path Issues

**Problem**: Sphinx can't find source files.

**Solution**: Check `docs/source/conf.py` path settings. In Read the Docs, the package is installed, so paths should work automatically.

## Verification Checklist

Before pushing to GitHub, verify:

- [ ] `.readthedocs.yml` is valid YAML
- [ ] Python version matches (3.11)
- [ ] Package installs successfully with `pip install -e ".[docs]"`
- [ ] Documentation builds without errors: `cd docs && make html`
- [ ] All API documentation generates correctly
- [ ] No broken links or missing images
- [ ] Output HTML files are generated in `docs/build/html/`

## Quick Test Command

For a quick test, run:

```bash
make test-rtd && echo "✓ Ready for Read the Docs!" || echo "✗ Issues found, check output above"
```

## Next Steps

After local testing passes:

1. Commit your changes
2. Push to GitHub
3. Read the Docs will automatically build
4. Check the build status on Read the Docs dashboard
5. View your documentation at `https://flowforge.readthedocs.io`

