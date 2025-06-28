# Build Optimization Guide

## For Replit Deployment:
The build should complete in 3-5 minutes with these optimizations:

1. **Use Binary Wheels**: All dependencies configured to prefer pre-compiled binaries
2. **Parallel Builds**: NumPy/SciPy configured for 4-core compilation  
3. **Version Pinning**: Exact versions to avoid dependency resolution delays
4. **Build Caching**: Optimized cache directories for faster rebuilds

## Expected Build Time:
- Before optimization: 10+ minutes (source compilation)
- After optimization: 3-5 minutes (binary wheels + caching)

## If builds are still slow:
1. Check that binary wheels are being used (look for "Building wheel" vs "Using cached")
2. Ensure pip cache is working properly
3. Verify network connectivity to PyPI mirrors

## Manual speed test:
```bash
time pip install -r requirements-optimized.txt --force-reinstall
```
