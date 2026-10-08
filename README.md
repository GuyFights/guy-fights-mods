# Guy Fights mod registry

An online catalog of declarative JSON mods for Guy Fights, currently Beta 0.2.2 (a single-file HTML/JavaScript browser game).

## Files

- `index.json`: catalog fetched by the future in-game Mod Browser.
- `schema/mod.schema.json`: JSON Schema for validating mod manifests.
- `mods/example-mod/mod.json`: minimal example manifest.

Fetch the catalog from `https://raw.githubusercontent.com/GuyFights/guy-fights-mods/main/index.json`. Resolve each entry's `manifest` path relative to the catalog URL. Each entry contains `id`, `name`, `author`, `version`, `description`, `compatibility`, `tags`, and `manifest`. The manifest repeats that metadata, omits `manifest`, and adds `formatVersion` and `changes`. Matching metadata must agree between catalog and manifest.

## Version compatibility

Versions use numeric `major.minor.patch` strings without the UI's “Beta” prefix. `compatibility.minimum` is inclusive. `compatibility.maximum` is either an inclusive exact version or a patch wildcard such as `0.2.x`, which includes every patch in the `0.2` series. Compare components numerically, never as strings. The example accepts `0.2.2` and later `0.2` patches, but excludes `0.2.1` and `0.3.0`. Reject ranges whose maximum is below the minimum.

`formatVersion: 1` identifies the catalog and manifest format. Mod `version` tracks the mod's release independently of the game version.

## Declarative changes

`changes` is an object reserved for operations implemented by Guy Fights' own mod API. The example uses `{}` and intentionally has no gameplay effect: no API operations have been defined yet. Future API work must define supported keys, value types, limits, and validation rules before enabling nonempty changes. The current schema therefore accepts only an empty `changes` object.

Mods are data only. Never execute downloaded JavaScript, interpret strings as code, or use `eval()` or `new Function()`. Schema validation checks structure; the game must also check compatibility, duplicate IDs, catalog/manifest agreement, and supported API operations before installation. Treat all content as untrusted, render text safely, and reject unsupported format versions or changes. Restrict manifest URLs to trusted HTTPS registry locations.

## Adding a mod

1. Create `mods/<id>/mod.json` using the example and validate it against `schema/mod.schema.json` (JSON Schema Draft 2020-12).
2. Add matching metadata to the catalog's `mods` array with a relative `manifest` path.
3. Keep IDs unique and stable; use lowercase letters, numbers, and single separating hyphens. Increment the mod version when releasing changes.

The future Mod Browser will fetch the catalog and manifests, validate them, and store installed manifests and enabled mod IDs locally. This repository supplies registry data only; it does not yet implement that browser or the game's mod API.
