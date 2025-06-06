# Git Push Instructions

You're encountering GitHub's file size limits because your virtual environment (`st-env`) contains large binary files that exceed GitHub's limits. Here's how to fix this issue:

## Solution 1: Properly exclude virtual environment (Recommended)

1. Make sure the enhanced `.gitignore` file is properly excluding your virtual environment and large files
2. Remove the virtual environment from Git tracking:

```bash
git rm -r --cached st-env/
git commit -m "Remove virtual environment from Git tracking"
```

3. Try pushing again:

```bash
git push origin main
```

## Solution 2: Use Git LFS (for large files you need to track)

If you have large files that you actually need to track in Git:

1. Install Git LFS:
   ```bash
   # macOS
   brew install git-lfs
   
   # Linux
   sudo apt-get install git-lfs
   ```

2. Initialize Git LFS:
   ```bash
   git lfs install
   ```

3. Track specific large file types:
   ```bash
   git lfs track "*.h5"
   git lfs track "*.pb"
   git lfs track "*.dylib"
   ```

4. Add, commit and push:
   ```bash
   git add .gitattributes
   git commit -m "Configure Git LFS"
   git push origin main
   ```

## Best Practices

1. **Never commit virtual environments**: Always use `.gitignore` to exclude them
2. **Document dependencies instead**: Use `requirements.txt` or `environment.yml`
3. **Large model files**: Consider storing them separately (Google Drive, S3, etc.)
4. **Use Git LFS selectively**: Only for large files you absolutely need to track

## Creating a requirements.txt

Generate a requirements file instead of committing the virtual environment:

```bash
pip freeze > requirements.txt
```

Then others can recreate your environment with:

```bash
python -m venv st-env
source st-env/bin/activate  # On Windows: st-env\Scripts\activate
pip install -r requirements.txt
```
