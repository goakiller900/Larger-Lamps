# Releasing Larger Lamps

1. Update `LargerLamps-2.0/info.json`.
2. Add the matching version at the top of `LargerLamps-2.0/changelog.txt`.
3. Run `python scripts/build_release.py`.
4. Test the generated ZIP in Factorio 2.1 with:
   - base game;
   - Space Age;
   - current AAI Industry;
   - an existing save upgraded from the previous release.
5. Merge the reviewed release branch into `main`.

The GitHub Actions workflow builds the archive on pull requests and creates an immutable GitHub Release on `main`.

To publish automatically to the Factorio Mod Portal, add a GitHub Actions repository secret named `FACTORIO_API_KEY` containing an API key with `ModPortal: Upload Mods` permission. Existing portal versions are detected and skipped safely.
