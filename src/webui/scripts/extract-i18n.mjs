import fs from 'node:fs';
import path from 'node:path';

const args = new Set(process.argv.slice(2));
const checkOnly = args.has('--check');
const appDir = path.resolve('src/app');
const outputDir = path.resolve('src/assets/i18n');
const locales = ['en', 'vi', 'ja'];

const staticKeys = new Set();
const dynamicKeys = new Set(['language.en', 'language.vi', 'language.ja']);

function walk(dir, visit) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, visit);
    } else {
      visit(fullPath);
    }
  }
}

function addKey(key, target = staticKeys) {
  if (key && !key.includes('${')) {
    target.add(key);
  }
}

walk(appDir, (filePath) => {
  if (!/\.(html|ts)$/.test(filePath) || filePath.endsWith('.d.ts')) return;

  const source = fs.readFileSync(filePath, 'utf8');

  for (const match of source.matchAll(/(['"`])([^'"`]+)\1\s*\|\s*translate/g)) {
    addKey(match[2]);
  }
  for (const match of source.matchAll(/(?:this\.)?translate\.(?:instant|get)\(\s*['"`]([^'"`]+)['"`]/g)) {
    addKey(match[1]);
  }
  for (const match of source.matchAll(/i18n\.t\(\s*['"`]([^'"`]+)['"`]/g)) {
    addKey(match[1]);
    addKey(match[1], dynamicKeys);
  }
  for (const match of source.matchAll(/labelKey:\s*['"`]([^'"`]+)['"`]/g)) {
    addKey(match[1]);
    addKey(match[1], dynamicKeys);
  }
  for (const match of source.matchAll(/i18nKey\(\s*['"`]([^'"`]+)['"`]/g)) {
    addKey(match[1]);
  }
  if (source.includes("'language.' + locale")) {
    for (const locale of locales) {
      addKey(`language.${locale}`);
      addKey(`language.${locale}`, dynamicKeys);
    }
  }
});

const keys = [...staticKeys].sort((a, b) => a.localeCompare(b));
const expectedDynamicKeys = [...dynamicKeys].sort((a, b) => a.localeCompare(b));

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return {};
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function sortedObject(obj) {
  return Object.fromEntries(Object.entries(obj).sort(([a], [b]) => a.localeCompare(b)));
}

let failed = false;

for (const key of expectedDynamicKeys) {
  if (!staticKeys.has(key)) {
    console.error(`[i18n] Dynamic key is not covered by extraction markers/patterns: ${key}`);
    failed = true;
  }
}

for (const locale of locales) {
  const filePath = path.join(outputDir, `${locale}.json`);
  const existing = readJson(filePath);

  if (checkOnly) {
    const missing = keys.filter((key) => !(key in existing));
    if (missing.length) {
      console.error(`[i18n] ${locale}.json is missing extracted keys:\n${missing.map((key) => `  - ${key}`).join('\n')}`);
      failed = true;
    }
    continue;
  }

  const next = {};
  for (const key of keys) {
    next[key] = existing[key] ?? '';
  }
  fs.writeFileSync(filePath, `${JSON.stringify(sortedObject(next), null, 2)}\n`, 'utf8');
}

if (failed) {
  process.exit(1);
}

if (checkOnly) {
  console.log(`[i18n] Check passed: ${keys.length} keys found, including ${expectedDynamicKeys.length} dynamic keys.`);
} else {
  console.log(`[i18n] Updated ${locales.map((locale) => `src/assets/i18n/${locale}.json`).join(', ')} with ${keys.length} keys.`);
}
