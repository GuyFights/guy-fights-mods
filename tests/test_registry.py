import copy
import sys
import unittest
from pathlib import Path

from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_registry import (ROOT, compatible, load_json, manifest_location,
                               parse_json, validate_catalog, validate_manifest)


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(ROOT / 'schema/mod.schema.json')
        cls.catalog_schema = load_json(ROOT / 'schema/catalog.schema.json')
        cls.template = load_json(ROOT / 'mods/example-mod/mod.json')

    def validate(self, changes):
        manifest = copy.deepcopy(self.template)
        manifest['changes'] = changes
        validate_manifest(manifest, self.schema)

    def test_all_categories(self):
        self.validate({
            'guys': {'modify': [{'id': 'drunk-guy', 'set': {'hp': 1, 'projectileInterval': 0.05}}]},
            'zones': {'modify': [{'id': 'mud', 'set': {'blocksProjectiles': False, 'opacity': 1}}]},
            'projectiles': {'modify': [{'id': 'fixture-projectile', 'set': {'bounceCount': 100, 'lifetime': 0.05}}]},
            'matchSettings': {'roundDuration': 180, 'scoreLimit': 5, 'friendlyFire': False},
        })

    def test_rejected_operations_and_values(self):
        bad = [
            {}, {'guys': {'modify': [{'id': 'unknown-guy', 'set': {'hp': 100}}]}}, {'zones': {'modify': [{'id': 'unknown-zone', 'set': {'duration': 1}}]}}, {'scripts': []}, {'guys': {'add': []}},
            {'guys': {'modify': []}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {}}]}},
            {'guys': {'modify': [{'id': '0.health', 'set': {'hp': 100}}]}},
            {'guys': {'modify': [{'id': 'constructor', 'set': {'hp': 100}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'path': 'window.x', 'set': {'hp': 100}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'hp': 0}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'movementSpeedMax': 5001}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'projectileInterval': 0}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'hp': True}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'scriptUrl': 'script.js'}}]}},
            {'zones': {'modify': [{'id': 'mud', 'set': {'blocksProjectiles': 'true'}}]}},
            {'projectiles': {'modify': [{'id': 'fixture-projectile', 'set': {'bounceCount': 1.5}}]}},
            {'guys': {'modify': [{'id': 'drunk-guy', 'set': {'movementSpeedMin': 100, 'movementSpeedMax': 50}}]}}, {'matchSettings': {'lock': True}}, {'matchSettings': {'roundDuration': float('inf')}},
            {'matchSettings': {'roundDuration': float('nan')}},
        ]
        for changes in bad:
            with self.subTest(changes=changes), self.assertRaises((ValueError, ValidationError)):
                self.validate(changes)

    def test_verified_guy_limits(self):
        properties = self.schema['$defs']['guyValues']['properties']
        for field, constraint in properties.items():
            for boundary in ('minimum', 'maximum'):
                with self.subTest(field=field, boundary=boundary):
                    self.validate({'guys': {'modify': [{'id': 'drunk-guy', 'set': {field: constraint[boundary]}}]}})
            for value in (constraint['minimum'] - 1, constraint['maximum'] + 1):
                with self.subTest(field=field, rejected=value), self.assertRaises(ValidationError):
                    self.validate({'guys': {'modify': [{'id': 'drunk-guy', 'set': {field: value}}]}})
        with self.assertRaises(ValidationError):
            self.validate({'guys': {'modify': [{'id': 'drunk-guy', 'set': {'projectileCount': 1.5}}]}})

    def test_verified_entity_ids(self):
        for guy_id in self.schema['$defs']['guyId']['enum']:
            self.validate({'guys': {'modify': [{'id': guy_id, 'set': {'hp': 1000}}]}})
        for zone_id in self.schema['$defs']['zoneId']['enum']:
            self.validate({'zones': {'modify': [{'id': zone_id, 'set': {'duration': 1}}]}})
        for invalid_id in ('test-guy', 'Drunk Guy', '0', 'unknown-guy'):
            with self.subTest(invalid_id=invalid_id), self.assertRaises(ValidationError):
                self.validate({'guys': {'modify': [{'id': invalid_id, 'set': {'hp': 1000}}]}})

    def test_duplicate_edits(self):
        operation = {'id': 'drunk-guy', 'set': {'hp': 100}}
        with self.assertRaises(ValueError):
            self.validate({'guys': {'modify': [operation, operation]}})

    def test_strict_json_and_pollution(self):
        bad = ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}']
        bad += ['{"a":{"' + key + '":1}}' for key in ('__proto__', 'prototype', 'constructor')]
        for text in bad:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_json(text)

    def test_compatibility(self):
        compatibility = self.template['compatibility']
        for version, expected in [('0.2.1', False), ('0.2.2', True), ('0.2.10', True), ('0.3.0', False)]:
            self.assertEqual(compatible(compatibility, version), expected)
        self.assertTrue(compatible({'minimum': '0.2.2', 'maximum': '0.2.3'}, '0.2.3'))
        with self.assertRaises(ValueError):
            compatible({'minimum': '0.3.0', 'maximum': '0.2.x'}, '0.2.2')

    def test_api_version(self):
        for value in (None, 2):
            manifest = copy.deepcopy(self.template)
            if value is None:
                del manifest['apiVersion']
            else:
                manifest['apiVersion'] = value
            with self.assertRaises(ValidationError):
                validate_manifest(manifest, self.schema)

    def test_catalog_agreement(self):
        entry = {key: value for key, value in self.template.items() if key not in ('changes', 'formatVersion')}
        entry['manifest'] = 'mods/example-mod/mod.json'
        catalog = {'formatVersion': 1, 'mods': [entry]}
        validate_catalog(catalog, self.catalog_schema, self.schema)
        for field in ('name', 'author', 'version', 'description', 'compatibility', 'tags', 'apiVersion', 'id'):
            mismatch = copy.deepcopy(self.template)
            mismatch[field] = {'name': 'Changed', 'author': 'Changed', 'version': '3.0.0',
                               'description': 'Changed', 'compatibility': {'minimum': '0.2.3', 'maximum': '0.2.x'},
                               'tags': ['changed'], 'apiVersion': 2, 'id': 'different-id'}[field]
            with self.subTest(field=field), self.assertRaises((ValueError, ValidationError)):
                validate_catalog(catalog, self.catalog_schema, self.schema, loader=lambda _: mismatch)
        catalog['mods'].append(entry)
        with self.assertRaises(ValueError):
            validate_catalog(catalog, self.catalog_schema, self.schema)

    def test_url_policy(self):
        self.assertEqual(manifest_location('mods/example-mod/mod.json'), ROOT / 'mods/example-mod/mod.json')
        for reference in ('javascript:alert(1)', 'http://example.com/mod.json', '//evil.test/mod.json',
                          '../mod.json', 'mods/%2e%2e/mod.json', '/mods/example-mod/mod.json',
                          'https://evil.test/mod.json', 'mods/example-mod/mod.js',
                          'mods/example-mod/mod.json?script=1'):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                manifest_location(reference)


if __name__ == '__main__':
    unittest.main()
