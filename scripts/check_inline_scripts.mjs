import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.resolve(import.meta.dirname, '..');
const pages = fs.readdirSync(root).filter((name) => name.endsWith('.html')).sort();
const scriptPattern = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
let checked = 0;
const errors = [];

for (const page of pages) {
  const source = fs.readFileSync(path.join(root, page), 'utf8');
  let match;
  let index = 0;
  while ((match = scriptPattern.exec(source)) !== null) {
    index += 1;
    if (!match[1].trim()) continue;
    try {
      new vm.Script(match[1], { filename: `${page}:inline-${index}` });
      checked += 1;
    } catch (error) {
      errors.push(error.message);
    }
  }
}

if (errors.length) {
  console.error('Inline script validation failed:');
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`Inline script validation passed: pages=${pages.length}, scripts=${checked}`);
