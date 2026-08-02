import mermaid from 'mermaid';
const cases = {
  'pie w/ garbage body': `pie title X\n@@@ NOT PIE SYNTAX @@@\n!!!! ????`,
  'kanban w/ garbage body': `kanban\n@@@@ !!!! ####`,
  'valid pie': `pie title X\n    "A" : 30\n    "B" : 70`,
};
for (const [name, src] of Object.entries(cases)) {
  let d, p;
  try { d = 'detectType=' + mermaid.detectType(src); } catch (e) { d = 'detectType THREW: ' + e.message.slice(0,60); }
  try { await mermaid.parse(src); p = 'parse=ACCEPTED'; } catch (e) { p = 'parse=REJECTED(' + String(e?.message).slice(0,70) + ')'; }
  console.log(`${name}\n   ${d}\n   ${p}`);
}
