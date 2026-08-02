import mermaid from 'mermaid';

await mermaid.initialize({ startOnLoad: false });

console.log('detectType flowchart corrupted:', mermaid.detectType('flowchart TD\n BAD SYNTAX %%% $$$ ==='));
console.log('detectType sequence corrupted:', mermaid.detectType('sequenceDiagram\n INVALID MESSAGES >>> --->'));

try {
  await mermaid.parse('flowchart TD\n BAD SYNTAX %%% $$$ ===');
  console.log('parse succeeded unexpectedly');
} catch (e) {
  console.log('parse failed as expected with error:', e.message || e);
}
