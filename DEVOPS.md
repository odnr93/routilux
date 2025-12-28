# DevOps Guide

Complete guide for building, testing, and publishing Routilux.

## Table of Contents

- [Development Workflow](#development-workflow)
- [Building](#building)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Publishing to PyPI](#publishing-to-pypi)
  - [Manual Publishing](#manual-publishing)
  - [Automatic Publishing (GitHub Actions)](#automatic-publishing-github-actions)
- [Version Management](#version-management)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

## Development Workflow

### Initial Setup

```bash
# Install package in editable mode with development dependencies
make dev-install

# Or using pip directly
pip install -e ".[dev]"
```

This installs the package in "editable" mode, meaning:
- Changes to source code are immediately available
- No need to reinstall after code changes
- All imports work correctly without `sys.path` manipulation

### Available Commands

Run `make help` to see all available commands:

```bash
make help
```

## Building

### Build Package

```bash
# Build both source and wheel distributions
make build

# Build only source distribution
make sdist

# Build only wheel distribution
make wheel
```

Distribution files are created in the `dist/` directory:
- `routilux-X.X.X.tar.gz` (source distribution)
- `routilux-X.X.X-py3-none-any.whl` (wheel distribution)

### Check Package

Before uploading, validate the package:

```bash
make check-package
```

This runs `twine check` to validate the package structure and metadata.

### Clean Build Artifacts

```bash
make clean
```

Removes:
- `build/` directory
- `dist/` directory
- `*.egg-info` directories
- `__pycache__` directories
- `.pytest_cache` and `.mypy_cache`

## Testing

### Run Tests

```bash
# Run main tests
make test

# Run built-in routines tests
make test-builtin

# Run all tests
make test-all

# Run tests with coverage report
make test-cov
```

### Test Coverage

Coverage reports are generated in `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view the coverage report.

## Code Quality

### Linting

```bash
# Run linting checks (flake8)
make lint
```

### Code Formatting

```bash
# Format code with black
make format

# Check formatting without modifying files
make format-check
```

### Run All Checks

```bash
# Run linting, format check, and tests
make check
```

## Publishing to PyPI

### Prerequisites

1. **PyPI Account**: You need a PyPI account
2. **API Token**: Generate an API token from PyPI account settings
3. **Build Tools**: Install build tools:
   ```bash
   pip install build twine
   ```

### Manual Publishing

#### Step 1: Update Version

Before publishing, update the version in `routilux/__init__.py`:

```python
__version__ = "0.1.1"  # Increment version number
```

#### Step 2: Build Package

```bash
make build
```

#### Step 3: Check Package

```bash
make check-package
```

#### Step 4: Upload to PyPI

**Using Environment Variable (Recommended)**

```bash
export PYPI_TOKEN="your-pypi-api-token"
make upload
```

**Using .pypirc (Alternative)**

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = your-pypi-api-token
```

Then upload:
```bash
twine upload dist/*
```

**⚠️ Security Note**: Never commit `.pypirc` or tokens to git! They are in `.gitignore`.

#### Step 5: Test on TestPyPI (Optional)

Before publishing to production PyPI, you can test on TestPyPI:

```bash
export TEST_PYPI_TOKEN="your-test-pypi-token"
make upload-test
```

Then test installation:
```bash
pip install -i https://test.pypi.org/simple/ routilux
```

### Automatic Publishing (GitHub Actions)

The project includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically builds and publishes to PyPI when a release is created.

#### Setup

1. **Add PyPI Token to GitHub Secrets**:
   - Go to your GitHub repository
   - Navigate to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token
   - Click "Add secret"

2. **Create a Release**:
   - Go to your GitHub repository
   - Navigate to: Releases → Create a new release
   - Tag version: `v0.1.1` (match your package version)
   - Release title: `v0.1.1` or descriptive title
   - Description: Release notes
   - Click "Publish release"

3. **Workflow Triggers**:
   The workflow automatically runs when:
   - A new release is published
   - You manually trigger it (Actions → Publish to PyPI → Run workflow)

#### Workflow Steps

The GitHub Actions workflow will:
1. Checkout code
2. Set up Python
3. Install build dependencies
4. Build package
5. Check package
6. Upload to PyPI
7. Attach files to GitHub release

#### Manual Workflow Trigger

You can also manually trigger the workflow:
1. Go to Actions tab
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Version Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Version Update Checklist

Before publishing a new version:

- [ ] Update `routilux/__init__.py` version
- [ ] Update `CHANGELOG.md` with new version
- [ ] Commit changes
- [ ] Create git tag: `git tag v0.1.1`
- [ ] Push tag: `git push origin v0.1.1`
- [ ] Create GitHub release (for automatic publishing)

## Troubleshooting

### Error: "Package already exists"

- PyPI doesn't allow re-uploading the same version
- Increment version number and rebuild

### Error: "Invalid credentials"

- Check your API token is correct
- Ensure token has upload permissions
- For GitHub Actions, verify secret name is `PYPI_API_TOKEN`

### Error: "Package validation failed"

- Run `make check-package` to see detailed errors
- Check `pyproject.toml` and `setup.py` for issues
- Ensure all required files are included in `MANIFEST.in`

### Build fails

- Ensure `build` and `twine` are installed: `pip install build twine`
- Clean build artifacts: `make clean`
- Rebuild: `make build`

### Tests fail

- Ensure development dependencies are installed: `make dev-install`
- Check Python version compatibility (requires Python 3.7+)
- Run tests individually to isolate issues

### Linting/formatting issues

- Run `make format` to auto-format code
- Check `flake8` configuration in `pyproject.toml`
- Review `black` configuration if needed

## Security

### Best Practices

1. **Never commit tokens**:
   - Tokens are in `.gitignore`
   - Use environment variables or GitHub Secrets

2. **Use API tokens, not passwords**:
   - PyPI API tokens are more secure
   - Can be revoked individually

3. **Rotate tokens regularly**:
   - Generate new tokens periodically
   - Revoke old tokens

4. **Limit token scope**:
   - Use project-specific tokens when possible
   - Don't use account-wide tokens unless necessary

### Protected Files

The following files are in `.gitignore` and should never be committed:
- `.pypirc` - PyPI credentials
- `.env` - Environment variables
- `*.egg-info/` - Build artifacts
- `dist/` - Distribution files
- `build/` - Build directory

## Quick Reference

```bash
# Development
make dev-install          # Install in editable mode
make test                 # Run tests
make test-all            # Run all tests
make test-cov            # Run tests with coverage
make lint                # Run linting
make format              # Format code
make check               # Run all checks

# Building
make build               # Build package
make check-package       # Validate package
make clean               # Clean build artifacts

# Publishing
PYPI_TOKEN=token make upload        # Upload to PyPI
TEST_PYPI_TOKEN=token make upload-test  # Upload to TestPyPI
```

## Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)

