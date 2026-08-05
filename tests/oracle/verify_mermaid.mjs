import fs from 'node:fs/promises';
import { JSDOM } from 'jsdom';

// Establish JSDOM environment before importing DOMPurify / Mermaid.
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
const filePath = process.argv[2];

if (!filePath) {
  console.error('USAGE: node verify_mermaid.mjs <path_to_mmd_file>');
  process.exit(2);
}

await mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  htmlLabels: false,
  flowchart: { defaultRenderer: 'dagre-wrapper' },
  architecture: { randomize: false },
});

try {
  const source = await fs.readFile(filePath, 'utf8');
  await mermaid.parse(source);
  console.log('SUCCESS: Parsed diagram successfully');
} catch (error) {
  console.error(`PARSE_ERROR: ${error?.message ?? error}`);
  process.exit(1);
}
