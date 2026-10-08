"""Offline registry validation; game IDs/capabilities require game-side validation."""
import json
import math
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CATALOG_URL = 'https://raw.githubusercontent.com/GuyFights/guy-fights-mods/main/index.json'
FORBIDDEN = {'__proto__', 'prototype', 'constructor'}


def check_data(value, depth=0):
    if depth > 16:
        raise ValueError('JSON nesting exceeds 16')
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Nonfinite number')
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN:
                raise ValueError(f'Forbidden key: {key}')
            check_data(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            check_data(item, depth + 1)


def pairs_hook(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def parse_json(text):
    def reject_constant(value):
        raise ValueError(f'Non-JSON numeric constant: {value}')
    value = json.loads(text, object_pairs_hook=pairs_hook, parse_constant=reject_constant)
    check_data(value)
    return value


def load_json(path, limit=262144):
    data = path.read_bytes()
    if len(data) > limit:
        raise ValueError(f'{path}: size exceeds {limit} bytes')
    return parse_json(data.decode('utf-8'))


def version_tuple(value):
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError(f'Invalid exact version: {value}')
    return tuple(map(int, value.split('.')))


def bounds(compatibility):
    low = version_tuple(compatibility['minimum'])
    maximum = compatibility['maximum']
    if maximum.endswith('.x'):
        # Equivalent inclusive upper bound for a patch wildcard.
        major, minor = version_tuple(maximum[:-1] + '0')[:2]
        high = (major, minor, math.inf)
    else:
        high = version_tuple(maximum)
    if low > high:
        raise ValueError('Inverted compatibility range')
    return low, high


def compatible(compatibility, version):
    low, high = bounds(compatibility)
    return low <= version_tuple(version) <= high


def validate_manifest(manifest, schema):
    check_data(manifest)
    Draft202012Validator(schema).validate(manifest)
    bounds(manifest['compatibility'])
    for category in ('guys', 'zones', 'projectiles'):
        seen = set()
        for operation in manifest['changes'].get(category, {}).get('modify', []):
            entity_id = operation['id']
            if entity_id in seen:
                raise ValueError(f'Duplicate edit for {category}/{entity_id}')
            seen.add(entity_id)
            values = operation['set']
            if category == 'guys' and {'movementSpeedMin', 'movementSpeedMax'} <= values.keys():
                if values['movementSpeedMin'] > values['movementSpeedMax']:
                    raise ValueError('Inverted movement speed range')


def manifest_location(reference):
    """Registry policy: safe relative paths or HTTPS URLs within this registry."""
    raw = urlsplit(reference)
    decoded = unquote(raw.path)
    if any(part in ('.', '..') for part in decoded.split('/')) or '\\' in decoded:
        raise ValueError('Unsafe manifest path')
    if raw.query or raw.fragment or raw.username or raw.password:
        raise ValueError('Manifest credentials, query, or fragment are forbidden')
    if not raw.scheme and (raw.netloc or raw.path.startswith('/')):
        raise ValueError('Manifest path must be registry-relative')
    resolved = urlsplit(urljoin(CATALOG_URL, reference))
    prefix = '/GuyFights/guy-fights-mods/main/'
    if (resolved.scheme != 'https' or resolved.netloc != 'raw.githubusercontent.com'
            or not resolved.path.startswith(prefix)):
        raise ValueError('Manifest URL must belong to this trusted HTTPS registry')
    relative = resolved.path[len(prefix):]
    if not re.fullmatch(r'mods/[a-z0-9]+(?:-[a-z0-9]+)*/mod\.json', relative):
        raise ValueError('Manifest must point to mods/<id>/mod.json')
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Manifest escapes registry checkout')
    return path


def validate_catalog(catalog, schema, manifest_schema, loader=load_json):
    check_data(catalog)
    Draft202012Validator(schema).validate(catalog)
    seen = set()
    for entry in catalog['mods']:
        if entry['id'] in seen:
            raise ValueError('Duplicate catalog ID')
        seen.add(entry['id'])
        bounds(entry['compatibility'])
        manifest = loader(manifest_location(entry['manifest']))
        validate_manifest(manifest, manifest_schema)
        expected = {key: value for key, value in entry.items() if key != 'manifest'}
        actual = {key: value for key, value in manifest.items()
                  if key not in ('changes', 'formatVersion')}
        if actual != expected or manifest['formatVersion'] != catalog['formatVersion']:
            raise ValueError(f'Catalog/manifest metadata mismatch: {entry["id"]}')


def main():
    files = sorted(ROOT.rglob('*.json'))
    data = {path: load_json(path, 1048576 if path.name == 'index.json' else 262144)
            for path in files if '.git' not in path.parts}
    schemas = [path for path in data if path.name.endswith('.schema.json')]
    for path in schemas:
        Draft202012Validator.check_schema(data[path])
    manifest_schema = data[ROOT / 'schema/mod.schema.json']
    catalog_schema = data[ROOT / 'schema/catalog.schema.json']
    manifests = list(ROOT.glob('mods/*/mod.json'))
    ids = set()
    for path in manifests:
        manifest = data[path]
        validate_manifest(manifest, manifest_schema)
        if manifest['id'] != path.parent.name or manifest['id'] in ids:
            raise ValueError(f'Manifest ID/path mismatch or duplicate: {path}')
        ids.add(manifest['id'])
    validate_catalog(data[ROOT / 'index.json'], catalog_schema, manifest_schema)
    print(f'Validated {len(data)} JSON files, {len(schemas)} schemas, '
          f'{len(manifests)} manifests, and catalog agreement. '
          'Verified Guy/terrain IDs checked; game runtime adapters remain unverified.')


if __name__ == '__main__':
    main()
