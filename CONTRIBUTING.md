# Contributing to NOUS Personal Assistant

First off, thank you for considering contributing! We welcome any and all contributions that help make this project better.

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## ▶️ Getting Started

1.  **Fork & Clone:** Fork the repository to your own GitHub account and then clone it locally.
2.  **Branch:** Create a new branch for your changes: `git checkout -b feature/your-awesome-feature`.
3.  **Develop:** Make your changes. Follow the code style guidelines below.
4.  **Test:** Run the test suite to ensure your changes don't break existing functionality: `pytest`.
5.  **Commit:** Commit your changes with a clear and descriptive message.
6.  **Push & Pull Request:** Push your branch to your fork and submit a pull request to the main repository.

## ⚙️ Development Setup

The application is configured to run on Replit, which handles most dependency management. For a local setup:

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

2.  **Environment Variables:**
    Copy the documented variables from `ENV_VARS.md` into a `.env` file. At a minimum, you will need to set `DATABASE_URL`, `GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET`.

3.  **Run the App:**
    ```bash
    python main.py
    ```

## 🎨 Code Style

- **Python:** We follow `PEP 8` for all Python code.
- **Docstrings:** Use Google-style docstrings for all modules, classes, and functions.
- **Naming:** Use descriptive and consistent names for variables, functions, and classes.

## ✅ Pre-Commit Hooks (Recommended)

We highly recommend using `pre-commit` to automatically lint and format your code before you commit it.

1.  **Install pre-commit:**
    ```bash
    pip install pre-commit
    ```
2.  **Install the git hooks:**
    `bash
pre-commit install
`
    Now, `pre-commit` will run automatically on `git commit`!

## 🧪 Testing

The test suite uses `pytest`. To run all tests:

```bash
pytest
```

Ensure all tests pass before submitting a pull request. New features should include corresponding tests.

## Project Structure

```
├── api/                 # API endpoints and chat handlers
├── models/             # Database models
├── routes/             # Web route handlers
├── utils/              # Utility functions and helpers
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, and static assets
├── tests/              # Test files
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Types of Contributions

### Bug Reports

- Use the issue template
- Include steps to reproduce
- Provide error messages and logs
- Specify your environment details

### Feature Requests

- Describe the feature clearly
- Explain the use case
- Consider implementation complexity
- Check if it aligns with project goals

### Pull Requests

- Reference related issues
- Include tests for new functionality
- Update documentation as needed
- Follow the code review process

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

For specific test categories:

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Smoke tests
python -m pytest tests/smoke_test_suite.py
```

## Documentation

- Update relevant documentation for your changes
- Add docstrings to new functions and classes
- Update the CHANGELOG.md for significant changes
- Consider updating the user guide for user-facing features

## Security

- Report security vulnerabilities privately
- Follow secure coding practices
- Don't commit sensitive information
- Use environment variables for secrets

## Code Review Process

1. All changes require code review
2. At least one approval required
3. All tests must pass
4. Documentation must be updated
5. No merge conflicts

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production

## Community Guidelines

- Be respectful and inclusive
- Follow the Code of Conduct
- Ask questions if unclear
- Help others when possible
- Keep discussions on-topic

## Getting Help

- Check existing issues and documentation
- Ask questions in discussions
- Join our community chat
- Contact maintainers for complex issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
