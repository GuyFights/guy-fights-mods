# Guy Fights Mod API v1

## Status and integration boundary

This is an **external** JSON contract for Guy Fights Beta 0.2.2, not a list of JavaScript object paths. The authoritative integration reference supplied for this task verifies the Guy/terrain IDs, Guy editor limits, and Drunk Guy defaults below. This repository contains no game code or Mod API runtime implementation. Do not assume unmodified Beta 0.2.2 implements the operations merely because the manifest validates.

The schemas, real Drunk Guy example, catalog format, and offline validation are ready for integration development. The game must implement adapters, capability maps, validation, and lifecycle handling before these mods work. Both examples are excluded from `index.json` because corresponding runtime operations have not been confirmed implemented. The Drunk Guy example targets a verified existing Guy; the match-settings example still uses proposed external fields whose internal mappings must be verified. Actual game behavior has not been tested.

## Verified identity mapping

The runtime must use an explicit, game-owned mapping to current `CHARACTERS` names. These names are lookup values for the adapter only, never public mod selectors. Keep the external ID unchanged if an internal name or localized UI label changes; update the mapping instead. Never derive IDs by array position or translating UI text. Test Guys are deliberately excluded from the schema and runtime map.

| External Guy ID | Current internal `CHARACTERS` name |
| --- | --- |
| drunk-guy | Drunk Guy |
| angry-guy | Angry Guy |
| tired-guy | Tired Guy |
| business-guy | Business Guy |
| badass-cool-guy | Badass Cool Guy |
| chef-guy | Chef Guy |
| woman-guy | Woman Guy |
| tennis-guy | Tennis Guy |
| boxing-guy | Boxing Guy |
| magician-guy | Magician Guy |
| gravity-guy | Gravity Guy |
| dealer-guy | Dealer Guy |

The exact terrain IDs accepted by `zones.modify` are `river`, `lava`, `mud`, `ice`, `poison`, `healing`, `boost`, `wind`, `shield`, and `wall`. These are existing IDs, not new zone definitions. Schema enums reject other Guy/terrain IDs. Runtime must also check that the selected game build actually contains each mapped entity. Projectile IDs have not been supplied; they remain stable slugs resolved through a game-owned map, with unknown IDs rejected at runtime.

`formatVersion: 1` describes the registry envelope; required `apiVersion: 1` describes this change contract. Both catalog entries and manifests include `apiVersion`. Earlier no-op manifests without it are rejected; migrate them explicitly rather than guessing an API version.

## Shape and stable identity

A manifest repeats catalog metadata (`id`, `apiVersion`, `name`, `author`, `version`, `description`, `compatibility`, `tags`), includes `formatVersion`, and adds `changes`. A catalog entry replaces `changes` with `manifest`, a registry-relative JSON path or approved HTTPS URL.

Only four categories are allowed in `changes`. Entities support only `modify`, an array of `{ "id": "stable-id", "set": { ... } }` objects. `matchSettings` is a flat object of defaults. At least one change is required. There are no add/remove operations, paths, wildcard selectors, code expressions, hooks, or script URLs. Values are absolute replacements, not arithmetic expressions. IDs are lowercase ASCII slugs up to 64 characters; they must never be array indexes or localized display names. The game must maintain explicit maps from published external IDs to existing entities; renaming or reordering the UI must not change these IDs. Only the verified Guy and terrain IDs above are assigned by this contract.

Example Guy operation (verified existing Guy; requires runtime integration):

```json
{"guys":{"modify":[{"id":"drunk-guy","set":{"hp":1200,"baseDamage":130,"projectileSpeed":900,"projectileSize":50,"projectileInterval":1.8}}]}}
```

Example editable match defaults (integration template):

```json
{"matchSettings":{"roundDuration":180,"scoreLimit":5,"friendlyFire":false}}
```

Zone and projectile syntax (`mud` is verified; the projectile ID is a placeholder):

```json
{
  "zones":{"modify":[{"id":"mud","set":{"movementMultiplier":0.5,"blocksProjectiles":true,"color":"#3366FF"}}]},
  "projectiles":{"modify":[{"id":"example-existing-projectile","set":{"speed":600,"lifetime":2,"bounceCount":1}}]}
}
```

## External field allowlists and limits

These names and units are proposed external API names. They are **not inferred internal fields**. Guy field bounds come from the verified editor limits supplied for Beta 0.2.2; other category bounds are proposed API safety ceilings. A game adapter must explicitly translate units, map each external field to the actual implementation, and publish which fields each ID supports. Reject an unsupported field even if the schema accepts it; never invent a missing gameplay feature or silently skip it. The numbers are safety ceilings for the contract, not guarantees that every value is appropriate for every entity. Runtime adapters can enforce stricter limits and cross-field constraints.

Guy dimensions/projectile sizes use pixels and Guy speeds use px/second; proposed zone/projectile distances use logical game units and speeds use units/second; time uses seconds; health and damage use game points. Colors are exactly `#RRGGBB`, not CSS, URLs, or asset references. Numeric intervals below are inclusive. All numbers must be finite. Only projectile counts, bounce counts, and score limits are integers; fractional values are otherwise allowed within bounds.

| Category | External field | Type and bounds | Meaning |
| --- | --- | --- | --- |
| guys.modify | hp | number 1–1000000 | Base starting/max HP; apply before spawning |
| guys.modify | baseDamage | number 0–1000000 | Default attack damage |
| guys.modify | width | number 8–1000 | Width in pixels |
| guys.modify | height | number 8–1000 | Height in pixels |
| guys.modify | movementSpeedMin | number 0–5000 | Minimum movement speed, px/s |
| guys.modify | movementSpeedMax | number 0–5000 | Maximum movement speed, px/s |
| guys.modify | projectileInterval | number 0.05–3600 | Seconds between projectile firing cycles |
| guys.modify | projectileSpeed | number 0–5000 | Projectile launch speed, px/s |
| guys.modify | projectileSize | number 1–240 | Projectile size in pixels |
| guys.modify | projectileCount | integer 1–32 | Shots per firing cycle |
| guys.modify | projectileShotSpacing | number 0–60 | Seconds between shots within a cycle |
| guys.modify | sleepDuration | number 0–60 | Sleep duration in seconds, where supported |
| guys.modify | healingAmount | number 0–1000000 | Health points per healing event, where supported |
| guys.modify | healingInterval | number 0.05–3600 | Seconds between healing events, where supported |
| zones.modify | strength | number 0–100 | Nonnegative zone effect magnitude in adapter-documented units |
| zones.modify | duration | number 0.05–300 | Zone lifetime |
| zones.modify | movementMultiplier | number 0–4 | Multiplier applied to affected movement |
| zones.modify | blocksProjectiles | boolean | Whether the zone blocks projectiles |
| zones.modify | radius | number 1–2000 | Zone radius |
| zones.modify | color | hex string | Zone visual color |
| zones.modify | opacity | number 0–1 | Zone visual opacity |
| projectiles.modify | speed | number 0–5000 | Base projectile speed |
| projectiles.modify | damage | number 0–10000 | Base impact damage |
| projectiles.modify | size | number 1–500 | Collision diameter |
| projectiles.modify | lifetime | number 0.05–300 | Maximum projectile lifetime |
| projectiles.modify | bounceCount | integer 0–100 | Maximum bounces |
| projectiles.modify | color | hex string | Projectile visual color |
| matchSettings | roundDuration | number 10–3600 | Default round time |
| matchSettings | scoreLimit | integer 1–100 | Default winning score |
| matchSettings | friendlyFire | boolean | Default friendly-fire toggle |

Verified Drunk Guy defaults: HP 1000, default attack damage 112, movement `Drunk`, projectile interval 2 seconds, speed 840 px/s, size 60 px, spin 540. The first example changes those verified stats to HP 1200, damage 130, speed 900, size 50, and interval 1.8 seconds. It leaves movement and spin unchanged. Movement modes and spin are intentionally not exposed: the reference supplies no safe enum/range for editing them. No Guy color field is exposed because no verified safe Guy color contract was supplied. Boolean and constrained color-string values are supported in proposed zone/projectile operations instead.

Require effective `movementSpeedMin <= movementSpeedMax` after combining overrides with base values. Offline validation catches an inverted pair supplied together; runtime must check a partial override against actual defaults and after combining enabled mods. Do not expose a special ability on a Guy that does not support it, even if its external field has an editor limit.

There are at most 100 entity edits per category. Each `set` must be nonempty, and each category/operation object is closed to unknown fields. Do not expose unrestricted strings, asset URLs, deep merges, or arbitrary object paths. String metadata is inert text; it must never be interpreted as HTML or code.

## Validation and compatibility

Installation must validate the entire candidate before changing state:

1. Fetch bounded UTF-8 JSON from trusted registry locations. Recommended hard ceilings: 1 MiB catalog, 256 KiB manifest, nesting depth 16. Resolve relative manifest paths against the catalog URL; accept only approved HTTPS origins, with no credentials, traversal, or executable resource paths. Recheck redirects. Reject duplicate JSON keys, not just duplicate mod IDs.
2. Reject `__proto__`, `prototype`, and `constructor` keys recursively before any merge/copy, including locally stored inputs. Reject nonfinite numbers recursively with `Number.isFinite` in the game; strict JSON excludes NaN/Infinity but arithmetic overflow such as `1e999` can still produce Infinity. A schema validator alone is insufficient here.
3. Validate the catalog and manifest against their Draft 2020-12 schemas. Reject unknown format/API versions, categories, operation names, extra properties, wrong types, and out-of-range values. An ID string passing schema validation is not proof it exists.
4. Require unique catalog mod IDs. Compare every shared catalog/manifest field structurally, including API version, tags (in order), and compatibility. Require manifest formatVersion to match catalog formatVersion. Fetching by an entry must not bypass this agreement check.
5. Compare numeric version components, excluding the UI “Beta” prefix. Minimum is inclusive; maximum is an inclusive exact version or patch wildcard. `0.2.x` means all patches in minor series 0.2, never 0.3. Reject inverted ranges. The examples accept 0.2.2 and 0.2.10, reject 0.2.1 and 0.3.0. Ignore no checks just because a mod claims compatibility.
6. Resolve entity IDs only through explicit game-owned capability maps. Reject unknown IDs, duplicate edits to the same entity within one manifest, fields unsupported by a particular entity, unsupported settings, and illegal combinations. Validate resulting data and finite converted values after unit conversion. Never write through user-provided paths, use generic assignment onto game objects, or merge untrusted objects into prototypes.
7. Build a fresh candidate from pristine game defaults. Apply only explicit field setters to the candidate, then commit atomically if every enabled mod validates. A failure leaves live/default data unchanged and reports the offending mod/category/ID/field.

The offline validator checks JSON, schema, metadata, compatibility ranges, finite values, duplicate keys/edits, and URL policy. It cannot verify game IDs, capabilities, engine constraints, or execution behavior because those belong to the game implementation. Its test fixtures are synthetic, not game data.

## Application lifecycle and required game work

Guy Fights must add explicit ID registries and field setters, publish supported capabilities and per-entity limits, map these proposed fields to verified internal data, implement the validation sequence, and connect loading to match creation. For fields with no existing data-backed equivalent, reject them or defer support; do not interpret metadata as code.

Apply entity/projectile/zone defaults before creating a new match, not to a running simulation. Multiple enabled mods apply in the player's persisted ordered list; later mods win on overlapping fields. Show conflicts in the browser before enabling. Duplicate entity edits inside one mod are rejected rather than relying on order. If both a Guy launch-speed override and a projectile speed override apply, define Guy launch speed as the final per-launch override for that Guy; otherwise use the projectile default. An adapter unable to preserve that distinction must reject the unsupported field.

`matchSettings` changes are defaults only. Keep immutable built-in defaults, derive mod defaults, then overlay explicit player choices. Render the normal settings controls as editable; there is no lock operation. Resetting to defaults uses the current mod defaults. Enabling/disabling/reordering mods rebuilds from pristine defaults rather than repeatedly modifying already modified values. Preserve explicit player settings when rebuilding.

The Mod Browser and game must persist installed validated manifests, enabled IDs, order, and explicit player settings locally; revalidate stored data on load and game upgrades. Local storage is untrusted. Disabling a mod restores defaults through rebuilding. This registry provides no game execution, storage, network fetcher, or UI implementation. No JavaScript execution, `eval()`, `new Function()`, script URLs, or executable hooks are part of this API.

## Publishing examples

`mods/example-mod/mod.json` and `mods/example-match-settings/mod.json` are schema-valid examples requiring game-side integration. Implement and verify the game adapters for the verified `drunk-guy` mapping and the proposed match defaults, then run functional game checks. Only then add matching metadata plus `manifest` paths to `index.json`. Until that happens the catalog is intentionally empty, so the future browser cannot offer an unverified template as a working mod.

## Source inspection notes for the future game repository

Game-side work belongs in `GuyFights/guy-fights`, which the owner will create and populate with the authoritative Beta 0.2.2 source. Do not put game HTML or runtime implementation in this registry. Implementation is deferred until that repository is available.

For integration planning, the live `https://guyfights.neocities.org/game.html` was inspected on 2026-10-08. It identifies itself as Beta 0.2.2 / Hotfix #4. Its SHA-256 was `83d13e6e5c167c4c0b1abe882ad17a690d844e2afd5da61eec2347b064539810`. These observations must be rechecked against the source committed to the future game repository; the downloaded file is not part of this registry. The public manifest format above remains unchanged.

- Guy `hp` maps to `CHARACTERS[name].hp`; `baseDamage` maps to `defaultAttack.damage` only when that Guy has a default attack. Gravity Guy and Dealer Guy have no default attack; reject attempts to add one through `baseDamage`. Special attacks also have independent damage calculations, so a base damage override must not be advertised as changing every attack.
- Movement bounds have data-backed equivalents `speed.min` / `speed.max`. Projectile fields map to `projectile.interval`, `.speed`, `.size`, `.count`, `.shotSpacing`, and `.sleepSeconds` where supported. Built-in behavior configs can duplicate projectile values; the adapter must keep the relevant configs consistent and preserve special attack semantics. Healing fields require an existing supported healing behavior.
- `width` / `height` have editor metadata equivalents in `size`, but `fitSprites()` currently uses a fixed shared 162.4-pixel frame rather than that metadata. Merely changing `size` would silently have no battle effect. Reject these fields until the game deliberately supports their documented runtime meaning, or implement and test that behavior in the game repository.
- `roundDuration` has a candidate mapping to `timerSettings.duration`. The timer defaults to disabled in HP mode; changing duration must not silently enable it. Existing normal controls use whole seconds, whereas the public schema permits fractional seconds. The game must support precise values end to end or explicitly reject unsupported fractional defaults; never silently round an accepted manifest. The inspected build has no score-limit setting or friendly-fire toggle equivalent. In particular, projectile target selection explicitly excludes teammates. The current match-default example includes these unsupported fields and must remain outside the catalog until support exists.
- Terrain IDs identify **types**, not placed-zone instance IDs. Instances have numeric IDs and rectangular percentage-based geometry. Runtime mapping should apply supported per-type overrides to existing zones of that type without using those numeric IDs as public selectors or creating zones implicitly. Existing normalization restricts instance strength to 0.1–5; the public schema permits 0–100. Enforce the narrower supported range explicitly until the game supports the full range; do not clamp a validated mod silently. Color has an existing data-backed equivalent. Duration, radius, opacity, arbitrary movement multipliers, and configurable projectile blocking do not have generic per-zone fields in this build. Lava/poison effect durations and movement effects are coded by type, while Shield blocking is type-based. Such fields require deliberate game changes or capability rejection.
- Projectiles are configured under Guys and created dynamically; there is no existing public projectile-definition ID map. Publish an explicit stable projectile map in the game implementation before accepting `projectiles.modify`. A generic projectile lifetime, bounce count, or visual color cannot be assumed just because a specialized projectile has related behavior. Reject unsupported IDs/fields and preserve the documented Guy launch-speed precedence.
- The existing `.pak` system supports custom script behaviors separately. Registry JSON must never be routed through package import, custom script loading, or executable behavior hooks. The future Mod Manager needs a dedicated declarative path.

These are integration gaps, not permission to change the public schema silently. The Guy stat example is ready to test once its explicit adapters are implemented; the match-default example is schema-valid but not currently executable in the inspected unmodified game. No game runtime, Mods UI, or functional game tests have been implemented in this repository.
