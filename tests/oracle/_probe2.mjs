import mermaid from 'mermaid';
// Does detectType accept garbage bodies for the 15 types mmdio claims?
const types = {
 flowchart:'graph TD', sequence:'sequenceDiagram', class:'classDiagram', state:'stateDiagram',
 er:'erDiagram', gantt:'gantt', pie:'pie title X', git:'gitGraph', c4:'C4Context',
 mindmap:'mindmap', sankey:'sankey-beta', kanban:'kanban', timeline:'timeline',
 xychart:'xychart-beta', block:'block-beta'};
let weak=0, strict=0;
for (const [name, header] of Object.entries(types)) {
  const garbage = header + '\n@@@@ !!!! #### NOT VALID SYNTAX ????';
  let r;
  try { r = mermaid.detectType(garbage); weak++; } catch(e){ r='THREW'; strict++; }
  console.log(`${name.padEnd(10)} header=${header.padEnd(15)} detectType(garbage) -> ${r}`);
}
console.log(`\ngarbage ACCEPTED by detectType: ${weak}/15   rejected: ${strict}/15`);
