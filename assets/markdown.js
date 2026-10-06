// Render a safe Markdown subset using DOM nodes; never interpret supplied HTML.
function inline(parent, text) {
  const tokens = /(\*\*([^*]+)\*\*|`([^`]+)`)/g;
  let last = 0;
  for (const match of text.matchAll(tokens)) {
    parent.append(document.createTextNode(text.slice(last, match.index)));
    const node = document.createElement(match[2] !== undefined ? 'strong' : 'code');
    node.textContent = match[2] ?? match[3];
    parent.append(node);
    last = match.index + match[0].length;
  }
  parent.append(document.createTextNode(text.slice(last)));
}
export function renderMarkdown(container, source) {
  container.replaceChildren();
  const lines = source.replace(/\\r\\n|\\n/g, '\n').replace(/\r\n?/g, '\n').split('\n');
  let paragraph = [], quotes = [], list = null;
  const flushParagraph = () => {
    if (!paragraph.length) return;
    const p = document.createElement('p'); inline(p, paragraph.join('\n')); container.append(p); paragraph = [];
  };
  const flushQuotes = () => {
    if (!quotes.length) return;
    const block = document.createElement('blockquote');
    for (const part of quotes.join('\n').split(/\n\s*\n/)) {
      if (!part.trim()) continue;
      const p = document.createElement('p'); inline(p, part); block.append(p);
    }
    container.append(block); quotes = [];
  };
  for (const line of lines) {
    if (/^\s*>/.test(line)) {
      flushParagraph(); list = null; quotes.push(line.replace(/^\s*> ?/, '')); continue;
    }
    flushQuotes();
    if (!line.trim()) { flushParagraph(); list = null; continue; }
    const heading = line.match(/^#{1,6}\s+(.+)$/);
    const item = line.match(/^\s*(?:([-*+])|\d+\.)\s+(.+)$/);
    if (heading) {
      flushParagraph(); list = null;
      const h = document.createElement('h3'); inline(h, heading[1]); container.append(h);
    } else if (item) {
      flushParagraph(); const type = item[1] ? 'ul' : 'ol';
      if (!list || list.tagName.toLowerCase() !== type) { list = document.createElement(type); container.append(list); }
      const li = document.createElement('li'); inline(li, item[2]); list.append(li);
    } else { list = null; paragraph.push(line); }
  }
  flushParagraph(); flushQuotes();
}
