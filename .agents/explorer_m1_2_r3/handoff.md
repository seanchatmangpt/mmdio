# Handoff Report — Explorer 2 (Milestone M1 Iteration 3 Oracle Test Investigation)

**Explorer ID**: `explorer_m1_2_r3`  
**Working Directory**: `/Users/sac/mmdio/.agents/explorer_m1_2_r3`  
**Date**: 2026-08-02  
**Target Issue**: Oracle test failures in `tests/test_oracle_generated.py` caused by `tests/oracle/verify_mermaid.mjs` throwing `PARSE_ERROR: DOMPurify.sanitize is not a function` across 12 diagram types.

---

## 1. Observation

### 1.1 Test Failure Reproduction
Running `uv run pytest tests/test_oracle_generated.py -o addopts=""` resulted in **13 failed out of 15 tests**:
- **12 diagram types** (`block`, `c4`, `class`, `er`, `flowchart`, `git`, `kanban`, `mindmap`, `pie`, `sankey`, `state`, `timeline`) failed in `tests/oracle/verify_mermaid.mjs` with:
  ```
  AssertionError: Mermaid parser rejected diagram.
  Exit code: 1
  Stdout: 
  Stderr: PARSE_ERROR: DOMPurify.sanitize is not a function
  ```
- **2 diagram types** (`gantt`, `sequence`) passed cleanly.
- **1 diagram type** (`xychart`) failed with a syntax error (`xychart-beta line: [[]]`, assigned to Explorer 3).

### 1.2 Inspection of `tests/oracle/verify_mermaid.mjs`
File contents of `/Users/sac/mmdio/tests/oracle/verify_mermaid.mjs`:
```javascript
1: import fs from 'node:fs/promises';
2: import mermaid from 'mermaid';
3: 
4: const filePath = process.argv[2];
5: 
...
11: await mermaid.initialize({
12:   startOnLoad: false,
13:   securityLevel: 'strict',
14:   htmlLabels: false,
15:   flowchart: { defaultRenderer: 'dagre-wrapper' },
16:   architecture: { randomize: false }
17: });
...
21: await mermaid.parse(source);
```

### 1.3 Inspection of Mermaid 11.16.0 Source (`chunk-WYO6CB5R.mjs`)
In `/Users/sac/mmdio/tests/oracle/node_modules/mermaid/dist/chunks/mermaid.core/chunk-WYO6CB5R.mjs`:
- Line 5013: `import DOMPurify from "dompurify";`
- Line 5068-5080:
  ```javascript
  var sanitizeText = /* @__PURE__ */ __name((text, config2) => {
    if (!text) {
      return text;
    }
    if (config2.dompurifyConfig) {
      text = DOMPurify.sanitize(sanitizeMore(text, config2), config2.dompurifyConfig).toString();
    } else {
      text = DOMPurify.sanitize(sanitizeMore(text, config2), {
        FORBID_TAGS: ["style"]
      }).toString();
    }
    return text;
  }, "sanitizeText");
  ```
The parsers for 12 diagram types invoke `sanitizeText()` during AST parsing, whereas `gantt` and `sequence` parsers do not call `sanitizeText()`.

### 1.4 Node.js `dompurify` Module Behavior Inspection
Executing `node --input-type=module -e "import DOMPurify from 'dompurify'; console.log(typeof DOMPurify.sanitize, DOMPurify.isSupported);"` yielded:
```
undefined false
```
`DOMPurify` exported by default in Node.js (without a `window`/`document` DOM environment) is an uninitialized factory function (`createDOMPurify`). `DOMPurify.sanitize` is `undefined`, causing `DOMPurify.sanitize(...)` to throw `TypeError: DOMPurify.sanitize is not a function`.

### 1.5 Module Evaluation & Import Order Testing
- Testing static import vs global window assignment:
  ```javascript
  import { JSDOM } from 'jsdom';
  import DOMPurify from 'dompurify'; // Static import evaluates BEFORE window assignment
  globalThis.window = new JSDOM('').window;
  console.log(typeof DOMPurify.sanitize); // -> undefined
  ```
- Testing dynamic import after window assignment:
  ```javascript
  import { JSDOM } from 'jsdom';
  globalThis.window = new JSDOM('').window;
  const DOMPurify = (await import('dompurify')).default;
  console.log(typeof DOMPurify.sanitize); // -> function
  ```
Static ES imports evaluate `dompurify` at top-level module load time when `window` is `undefined`. Therefore, establishing `globalThis.window` and `globalThis.document` **must occur before** `mermaid` is imported, which requires a dynamic `await import('mermaid')`.

---

## 2. Logic Chain

1. **Failure Mechanics**:
   `tests/oracle/verify_mermaid.mjs` executes `await mermaid.parse(source)`.
   In Mermaid 11.16.0, 12 diagram types call `sanitizeText(text)` during `parse()`.
   `sanitizeText(text)` calls `DOMPurify.sanitize(text, ...)`.

2. **DOM Environment Requirement**:
   In Node.js, `dompurify` checks for `window` and `document` upon module evaluation.
   Without a DOM environment, `dompurify` returns an uninitialized factory object where `DOMPurify.sanitize` is `undefined`.

3. **Import Timing Requirement**:
   Because ES module static `import` declarations are evaluated before top-level code execution, statically importing `mermaid` at the top of `verify_mermaid.mjs` evaluates `dompurify` before any DOM setup code can run.
   Thus, `jsdom` must be initialized first, setting `globalThis.window`, `globalThis.document`, `globalThis.Node`, and `globalThis.navigator`, followed by `const { default: mermaid } = await import('mermaid');`.

4. **Node Version Engine Compatibility**:
   Installing `jsdom@30` on Node v20.13.0 raises `ERR_REQUIRE_ESM` due to `@exodus/bytes` requiring Node >=22.
   Pinning `jsdom` to `^24.1.3` (or `^24.0.0`) supports Node v20 and v22 without engine warnings or ESM compatibility errors.

5. **Empirical Verification of Fix**:
   Running a Node test with `jsdom@24` and the dynamic import pattern against all 12 failing diagram types resulted in 100% PASS rates (`PASS: block`, `PASS: c4`, `PASS: class`, `PASS: er`, `PASS: flowchart`, `PASS: git`, `PASS: kanban`, `PASS: mindmap`, `PASS: pie`, `PASS: sankey`, `PASS: state`, `PASS: timeline`).

---

## 3. Caveats

- **Scope Boundary**: This report addresses the 12 diagram failures caused by `DOMPurify.sanitize is not a function`. It does not fix the single `xychart` syntax fixture failure (`xychart-beta line: [[]]`), which is assigned to Explorer 3 / `generated_fixtures.py.tmpl`.
- **Node Engine Pin**: `jsdom` should be pinned to `^24.1.3` in `tests/oracle/package.json` to ensure compatibility with Node v20.x runtimes.

---

## 4. Conclusion

The oracle failure `PARSE_ERROR: DOMPurify.sanitize is not a function` is caused by `tests/oracle/verify_mermaid.mjs` running Mermaid 11.16.0 in Node.js without a JSDOM environment, combined with static ESM import evaluation order.

### Proposed Concrete Fix

#### Fix Part 1: Update `tests/oracle/package.json`
Add `jsdom` (`^24.1.3`) to `devDependencies`:
```json
{
  "name": "mmdio-oracle",
  "version": "1.0.0",
  "type": "module",
  "devDependencies": {
    "jsdom": "^24.1.3",
    "mermaid": "11.16.0"
  }
}
```

#### Fix Part 2: Update `tests/oracle/verify_mermaid.mjs`
Initialize JSDOM and bind DOM globals before dynamically importing `mermaid`:
```javascript
import fs from 'node:fs/promises';
import { JSDOM } from 'jsdom';

// Initialize DOM environment before importing DOMPurify / Mermaid
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost/'
});

globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.Node = dom.window.Node;
globalThis.navigator = dom.window.navigator;

// Dynamically import mermaid after DOM globals are set
const { default: mermaid } = await import('mermaid');

const filePath = process.argv[2];

if (!filePath) {
  console.error('USAGE: node verify_mermaid.mjs <path_to_mmd_file>');
  process.exit(1);
}

await mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  htmlLabels: false,
  flowchart: { defaultRenderer: 'dagre-wrapper' },
  architecture: { randomize: false }
});

try {
  const source = await fs.readFile(filePath, 'utf8');
  await mermaid.parse(source);
  console.log('SUCCESS: Parsed diagram successfully');
  process.exit(0);
} catch (error) {
  console.error(`PARSE_ERROR: ${error?.message ?? error}`);
  process.exit(1);
}
```

---

## 5. Verification Method

To verify this fix:

1. **Install updated dependencies**:
   ```bash
   cd /Users/sac/mmdio/tests/oracle && npm install
   ```

2. **Run Node verification test across all 12 failing diagram types**:
   ```bash
   node --input-type=module -e "
   import { JSDOM } from 'jsdom';
   const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
   globalThis.window = dom.window;
   globalThis.document = dom.window.document;
   globalThis.Node = dom.window.Node;
   globalThis.navigator = dom.window.navigator;
   const { default: mermaid } = await import('mermaid');
   await mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
   
   const samples = [
     'stateDiagram-v2\n  [*] --> S1',
     'graph TD\n  A --> B',
     'classDiagram\n  class A',
     'erDiagram\n  A ||--o{ B : rel',
     'C4Context\n  Person(p, \"Label\", \"Descr\")',
     'mindmap\n  root((Root))',
     'timeline\n  title T\n  2024 : Event',
     'pie title P\n  \"A\" : 100',
     'sankey-beta\n  A,B,10',
     'block-beta\n  block\n    A\n  end',
     'gitGraph\n  commit',
     'kanban\n  Todo\n    [T1]'
   ];
   for (const s of samples) {
     await mermaid.parse(s);
   }
   console.log('ALL 12 DIAGRAM TYPES PARSED CLEANLY');
   "
   ```
   *Expected Output*: `ALL 12 DIAGRAM TYPES PARSED CLEANLY` with 0 DOMPurify errors.
