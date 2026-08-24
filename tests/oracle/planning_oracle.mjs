import fs from 'node:fs/promises';
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost/',
});

globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.Node = dom.window.Node;

const DOMPurifyModule = await import('dompurify');
const DOMPurify = DOMPurifyModule.default
  ? DOMPurifyModule.default(dom.window)
  : DOMPurifyModule(dom.window);
globalThis.DOMPurify = DOMPurify;

const { default: mermaid } = await import('mermaid');
const files = process.argv.slice(2);

if (files.length === 0) {
  console.error('USAGE: node planning_oracle.mjs <diagram.mmd> [...]');
  process.exit(2);
}

await mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  htmlLabels: false,
});

const parsed = [];
for (const file of files.sort()) {
  try {
    const source = await fs.readFile(file, 'utf8');
    await mermaid.parse(source);
    parsed.push(file);
  } catch (error) {
    console.error(`PARSE_ERROR ${file}: ${error?.message ?? error}`);
    process.exit(1);
  }
}

console.log(JSON.stringify({
  schema: 'mmdio.planning-mermaid-oracle/1',
  mermaid: '11.16.0',
  parsed,
  count: parsed.length,
  claim: 'PLANNING_MERMAID_SYNTAX_ACCEPTED_ONLY',
}));
