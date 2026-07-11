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

## Branch builds

Every push to a non-`main` branch builds the mod and creates or replaces one GitHub prerelease for that branch. The tag uses `branch-<branch-name>`, and the prerelease title includes the current short commit SHA.

Branch prereleases are test builds only. They never publish to the Factorio Mod Portal and never create the stable `v<version>` tag.

Pull-request runs still build and validate an Actions artifact, but do not create another release. This avoids duplicate prereleases because the corresponding branch push already creates one.

## Stable releases

A push or manual workflow run on `main` creates the immutable `v<version>` GitHub Release. Only `main` is allowed to publish to the Factorio Mod Portal.

To publish automatically to the Factorio Mod Portal, add a GitHub Actions repository secret named `FACTORIO_API_KEY` containing an API key with `ModPortal: Upload Mods` permission. Existing portal versions are detected and skipped safely.
