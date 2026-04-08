import { readFileSync, existsSync } from 'fs';

const checks = [
  {
    path: 'dist/index.html',
    contains: 'Scott Tomlins',
    label: 'index.html exists and contains name',
  },
  {
    path: 'dist/now/index.html',
    contains: '/now',
    label: '/now page exists',
  },
  {
    path: 'dist/seasonal-spirals/index.html',
    contains: 'seasonal-spirals',
    label: '/seasonal-spirals page exists',
  },
];

let passed = 0;
let failed = 0;

for (const check of checks) {
  if (!existsSync(check.path)) {
    console.error(`✗ ${check.label} — file not found: ${check.path}`);
    failed++;
    continue;
  }

  const content = readFileSync(check.path, 'utf-8');

  if (check.isJson) {
    try {
      const json = JSON.parse(content);
      const missingKeys = check.keys.filter(k => !(k in json));
      if (missingKeys.length > 0) {
        console.error(`✗ ${check.label} — missing keys: ${missingKeys.join(', ')}`);
        failed++;
        continue;
      }
    } catch {
      console.error(`✗ ${check.label} — invalid JSON`);
      failed++;
      continue;
    }
  }

  if (check.contains && !content.includes(check.contains)) {
    console.error(`✗ ${check.label} — expected to contain: "${check.contains}"`);
    failed++;
    continue;
  }

  console.log(`✓ ${check.label}`);
  passed++;
}

console.log(`\nBuild validation: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
