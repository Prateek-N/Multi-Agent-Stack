#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const command = process.argv[2];

if (!command || command === '--help' || command === '-h') {
  console.log('Usage: agents-maker <command>');
  console.log('');
  console.log('Commands:');
  console.log('  init    Inject agents-maker into your project');
  console.log('');
  console.log('Example:');
  console.log('  npx @prateek_ai/agents-maker init');
  process.exit(0);
}

if (command === 'init') {
  const kitRoot = path.join(__dirname, '..');
  const dest = path.join(process.cwd(), 'agents-maker');

  if (fs.existsSync(dest)) {
    console.log('agents-maker/ already exists.');
    console.log('To update, delete the folder and re-run: npx @prateek_ai/agents-maker init');
    process.exit(0);
  }

  console.log('Initializing agents-maker...');

  // Copy agent/skill/tool + docs directories wholesale
  ['agents', 'skills', 'tools', 'context_loaders', 'token_optimization',
   'platforms', 'docs', 'examples'].forEach(dir => {
    const src = path.join(kitRoot, dir);
    if (fs.existsSync(src)) copyDir(src, path.join(dest, dir));
  });

  // Copy config/ — specific files only (never project.yaml — that's per-developer)
  const configFiles = ['agents.yaml', 'domain_profiles.yaml', 'token_policies.yaml', 'project.yaml.example'];
  const configDst = path.join(dest, 'config');
  fs.mkdirSync(configDst, { recursive: true });
  configFiles.forEach(f => {
    const src = path.join(kitRoot, 'config', f);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(configDst, f));
  });

  // Copy root scripts, requirements, and the paste-only docs (PROMPT_TEMPLATE
  // powers the zero-Python workflow the README advertises).
  ['quickstart.sh', 'quickstart.ps1', 'requirements.txt', 'PROMPT_TEMPLATE.md', 'README.md'].forEach(f => {
    const src = path.join(kitRoot, f);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dest, f));
  });

  // Make shell script executable on Unix
  try { fs.chmodSync(path.join(dest, 'quickstart.sh'), 0o755); } catch (_) {}

  console.log('');
  console.log('✓ agents-maker/ ready');
  console.log('');
  console.log('Next — run from your project root:');
  console.log('  macOS / Linux / WSL:  bash agents-maker/quickstart.sh');
  console.log('  Windows:              .\\agents-maker\\quickstart.ps1');
  console.log('');
  console.log('This validates the kit and generates system_prompt.md for your project.');
  process.exit(0);
}

console.error(`Unknown command: ${command}`);
console.error('Run "agents-maker --help" for usage.');
process.exit(1);

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src)) {
    const s = path.join(src, entry);
    const d = path.join(dst, entry);
    if (fs.statSync(s).isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}
