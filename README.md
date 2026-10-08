# Guy Fights mod registry

Declarative JSON mod registry targeting Guy Fights Beta 0.2.2.

- `index.json`: online catalog for the future in-game Mod Browser.
- `schema/mod.schema.json`: closed, bounded Mod API v1 manifest schema.
- `schema/catalog.schema.json`: catalog schema using the same metadata contract.
- [Mod API v1](docs/mod-api-v1.md): external fields, units, limits, validation, and required game integration.
- `mods/example-mod/mod.json`: Drunk Guy stat example targeting a verified existing Guy.
- `mods/example-match-settings/mod.json`: editable match defaults integration template.

Catalog URL: `https://raw.githubusercontent.com/GuyFights/guy-fights-mods/main/index.json`. Resolve `manifest` paths relative to it. Catalog entries include mod ID, name, author, version, description, compatibility, tags, API version, and manifest URL/path. Shared metadata must match the downloaded manifest exactly.

## Integration status

This repository defines the external API and its explicit whitelist. The supplied Beta 0.2.2 integration reference verifies 12 stable Guy IDs mapped to current `CHARACTERS` names, 10 exact terrain IDs, safe Guy/editor limits, and Drunk Guy defaults; these are documented in the API reference. Test Guys are excluded. Internal property paths are not exposed or guessed.

The Drunk Guy example changes HP, base damage, and projectile defaults using `drunk-guy`. The second example changes editable match defaults using proposed external settings. Both require corresponding runtime adapters in the game; these operations have not been confirmed implemented, so the examples remain excluded from the valid, empty browser catalog. Once runtime support and functional testing are confirmed, add their matching entries. Unmodified Beta 0.2.2 is not claimed to support the new API.

Both examples target minimum `0.2.2`, maximum `0.2.x`. Numeric version comparison accepts later 0.2 patches but excludes 0.3.0. Mods contain only whitelisted data changes. Never execute downloaded JavaScript or code strings; no `eval()`, `new Function()`, script URLs, arbitrary object paths, or executable hooks are supported.

## Validate

With Python 3.10+:

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate_registry.py
python -m unittest discover -s tests -v
```

The validator checks all repository JSON/schema files, manifest structure, catalog agreement and paths, duplicate keys/IDs/edits, finite numbers, forbidden keys, and compatibility ranges. Tests cover accepted categories and rejected unsafe/invalid inputs. These checks do not establish that game IDs or capabilities exist. Runtime validation and game functional tests are still required.

## Add a mod

1. Use a verified game-owned external ID and supported fields; create `mods/<mod-id>/mod.json` with `formatVersion: 1`, `apiVersion: 1`, metadata, and `changes`.
2. Add matching metadata to `index.json` with its relative `manifest` path only once game integration works.
3. Validate, test in the game, and increment the mod version when releasing updates. Keep stable IDs independent of UI names and array positions.

The future browser must fetch and validate manifests, let players choose enabled mods/order, and store those choices locally. Match setting overrides are editable defaults, never locks.
