#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

// dist template subdir -> project target subdir (per tool's native command folder)
const TOOL_MAP = [
  ['claude/agents',         '.claude/agents',   'Claude Code'],
  ['claude/commands',       '.claude/commands', 'Claude Code'],
  ['antigravity/workflows', '.agent/workflows', 'Antigravity'],
  ['cursor/commands',       '.cursor/commands', 'Cursor'],
  ['copilot/prompts',       '.github/prompts',  'Copilot'],
];

// Command names (kept in sync with dist/) — used only for the printed hint.
const COMMANDS_HINT = ['brain', 'planpro', 'orchestrate', 'architect', 'code',
  'execute', 'ui', 'ux', 'review', 'compress'];

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

  // Install native /command files into every tool's folder so `/brain`, `/planpro`,
  // `/code`, … work in whichever chat box the user uses. Non-destructive.
  const projectRoot = process.cwd();
  const wired = installCommands(path.join(kitRoot, 'dist'), projectRoot);

  // Keep the bulky helper out of the user's commits; the small command files stay.
  const ignored = ensureGitignored(projectRoot, 'agents-maker/');

  console.log('');
  console.log('✓ agents-maker/ ready');
  if (wired.length) {
    console.log('✓ /commands installed for: ' + wired.join(', '));
    console.log('');
    console.log('  Commands: ' + COMMANDS_HINT.map(c => '/' + c).join('  '));
  }
  if (ignored) console.log('✓ agents-maker/ added to .gitignore (kept out of your commits)');
  console.log('');
  console.log('Use them now — type "/" in your AI chat box:');
  console.log('  Antigravity → .agent/workflows   Claude Code → .claude   Cursor → .cursor/commands   Copilot → .github/prompts');
  console.log('');
  console.log('Optional (Python): bash agents-maker/quickstart.sh  ·  .\\agents-maker\\quickstart.ps1');
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

// Copy each dist/<tool> into its project target, skipping files that already
// exist (never clobber the user's own commands). Returns the list of tool names wired.
function installCommands(distRoot, projectRoot) {
  const tools = new Set();
  for (const [srcSub, dstSub, toolName] of TOOL_MAP) {
    const srcDir = path.join(distRoot, srcSub);
    if (!fs.existsSync(srcDir)) continue;
    const dstDir = path.join(projectRoot, dstSub);
    fs.mkdirSync(dstDir, { recursive: true });
    for (const entry of fs.readdirSync(srcDir)) {
      const dstFile = path.join(dstDir, entry);
      if (fs.existsSync(dstFile)) {
        console.log(`  (kept existing ${dstSub}/${entry})`);
        continue;
      }
      fs.copyFileSync(path.join(srcDir, entry), dstFile);
      tools.add(toolName);
    }
  }
  return [...tools];
}

// Append a pattern to <project>/.gitignore idempotently (create the file if missing).
function ensureGitignored(projectRoot, pattern) {
  const gi = path.join(projectRoot, '.gitignore');
  let text = '';
  if (fs.existsSync(gi)) text = fs.readFileSync(gi, 'utf8');
  const has = text.split(/\r?\n/).some(l => l.trim().replace(/\/$/, '') === pattern.replace(/\/$/, ''));
  if (has) return false;
  const block = (text && !text.endsWith('\n') ? '\n' : '') +
    '\n# agents-maker helper kit (local only — not part of the project)\n' + pattern + '\n';
  fs.appendFileSync(gi, block);
  return true;
}
