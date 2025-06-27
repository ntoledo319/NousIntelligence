# NOUS Personal Assistant - Documentation Index

**Generated**: June 27, 2025 at 07:59 AM

## Primary Documentation

### Core Documentation (RST Format)
- [System Overview](docs/overview.rst)
- [Installation Guide](docs/installation.rst) 
- [API Reference](docs/api_reference.rst)
- [Architecture Guide](docs/architecture.rst)
- [Development Guide](docs/development.rst)
- [Deployment Guide](docs/deployment.rst)
- [Troubleshooting](docs/troubleshooting.rst)
- [Changelog](docs/changelog.rst)

### Interactive Documentation
- **API Documentation**: Start app and visit `/api/docs/`
- **OpenAPI Spec**: `/api/docs/openapi.json`
- **Endpoint List**: `/api/docs/endpoints`

## Project Documentation

### Main Project Files
- [README.md](README.md) - Project overview and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [LICENSE](LICENSE) - MIT License

### Configuration Guides
- [Network Configuration](PORT_README.md) - Port and API path management
- [Mobile & Responsive Design](RESPONSIVE_README.md) - Responsive design guide

### Operations & Reports
- [Development Operations](OPERATION_COMPLETE.md) - Major operation summaries

## Building Documentation

```bash
# Build all documentation
make docs

# Serve documentation locally
make serve-docs
# Visit: http://localhost:8000/documentation_index.html

# API documentation (requires running app)
python main.py
# Visit: http://localhost:5000/api/docs/
```

## Documentation Standards

- **Format**: reStructuredText for comprehensive docs, Markdown for project files
- **API Documentation**: Auto-generated OpenAPI/Swagger specifications
- **Build System**: Sphinx + custom builders with quality validation
- **Responsive Design**: Mobile-friendly documentation portal
- **Interactive Testing**: Live API endpoint testing capabilities

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: June 27, 2025
