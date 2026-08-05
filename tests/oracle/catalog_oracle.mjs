import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { execFileSync } from 'node:child_process';
import { JSDOM } from 'jsdom';

const upstreamRoot = process.argv[2];
if (!upstreamRoot) {
  console.error('USAGE: node catalog_oracle.mjs <mermaid-11.16.0-checkout>');
  process.exit(2);
}

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost/',
});
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.Node = dom.window.Node;
globalThis.navigator = dom.window.navigator;

const DOMPurifyModule = await import('dompurify');
const DOMPurify = DOMPurifyModule.default
  ? DOMPurifyModule.default(dom.window)
  : DOMPurifyModule(dom.window);
globalThis.DOMPurify = DOMPurify;

const { default: mermaid } = await import('mermaid');
const { default: zenuml } = await import('@mermaid-js/mermaid-zenuml');
await mermaid.registerExternalDiagrams([zenuml]);
await mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  htmlLabels: false,
  flowchart: { defaultRenderer: 'dagre-wrapper' },
  architecture: { randomize: false },
});

const python = process.env.PYTHON || 'python';
const env = { ...process.env, PYTHONPATH: process.env.PYTHONPATH || 'src' };
const manifest = JSON.parse(
  execFileSync(
    python,
    ['-c', 'from mmdio.engine.universal import capability_json; print(capability_json())'],
    { encoding: 'utf8', env },
  ),
);

function extractFirstExample(moduleSource) {
  const match = moduleSource.match(/code:\s*(?:String\.raw)?`([\s\S]*?)`\s*,/u);
  if (!match) {
    throw new Error('No template-literal example found');
  }
  return `${match[1].trim()}\n`;
}

async function sourceFor(record) {
  if (record.diagram_type === 'info') {
    return 'info\n';
  }
  if (record.diagram_type === 'swimlane') {
    return `flowchart LR
  subgraph intake["Intake lane"]
    A["Receive"] --> B["Admit"]
  end
  subgraph execution["Execution lane"]
    B --> C["Receipt"]
  end
`;
  }
  if (record.diagram_type === 'zenuml') {
    return `zenuml
  BookLibService.Borrow(id) {
    User = Session.GetUser()
    BookRepository.Update(id, onLoan, User)
    return receipt
  }
`;
  }
  const examplePath = path.join(
    upstreamRoot,
    'packages',
    'examples',
    'src',
    'examples',
    `${record.upstream_example}.ts`,
  );
  const moduleSource = await fs.readFile(examplePath, 'utf8');
  let source = extractFirstExample(moduleSource);
  if (record.diagram_type === 'flowchart-elk') {
    source = `---\nconfig:\n  flowchart:\n    defaultRenderer: elk\n---\n${source}`;
  } else if (record.diagram_type === 'classDiagram-v2') {
    source = source.replace(/^\s*classDiagram\b/mu, 'classDiagram-v2');
  } else if (record.diagram_type === 'stateDiagram-v2') {
    source = source.replace(/^\s*stateDiagram(?:-v2)?\b/mu, 'stateDiagram-v2');
  }
  return source;
}

const results = [];
for (const record of manifest) {
  const source = await sourceFor(record);
  const parsed = await mermaid.parse(source);
  const jsType =
    typeof parsed === 'object' && parsed !== null ? parsed.diagramType : undefined;
  if (jsType && !record.accepted_js_types.includes(jsType)) {
    throw new Error(
      `${record.diagram_type}: mermaid.parse returned ${jsType}; expected ${record.accepted_js_types.join(', ')}`,
    );
  }
  const parsedDocument = JSON.parse(
    execFileSync(
      python,
      ['-m', 'mmdio.cli', 'parse', '-', '--type', record.diagram_type],
      { input: source, encoding: 'utf8', env },
    ),
  );
  if (parsedDocument.type !== record.diagram_type) {
    throw new Error(`${record.diagram_type}: mmdio returned ${parsedDocument.type}`);
  }
  const canonical = source
    .replace(/\r\n?/gu, '\n')
    .replace(/[ \t]+$/gmu, '')
    .replace(/\n*$/u, '\n');
  if (parsedDocument.source !== canonical) {
    throw new Error(`${record.diagram_type}: canonical replay mismatch`);
  }
  results.push({
    diagram_type: record.diagram_type,
    document_class: record.document_class,
    js_type: jsType ?? 'accepted',
    source_sha256: parsedDocument.source_sha256,
  });
}

if (results.length !== 39) {
  throw new Error(`Expected 39 executed types, observed ${results.length}`);
}
console.log(
  JSON.stringify({
    schema: 'mmdio.js-oracle/v1',
    mermaid: '11.16.0',
    count: 39,
    results,
  }),
);
