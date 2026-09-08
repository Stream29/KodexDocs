// Use Markdown's own token positions to avoid treating headings in fences as navigation.
export function rawDocument(source, tokens) {
  const lines = source.split(/(?<=\n)/);
  const headings = tokens.flatMap((token, index) =>
    token.type === 'heading_open' && token.level === 0 && token.tag === 'h2'
      ? [{ line: token.map[0], title: tokens[index + 1].content }]
      : []);
  const titleIndex = tokens.findIndex(token => token.type === 'heading_open' && token.tag === 'h1');
  const starts = [0, ...headings.map(heading => heading.line)];
  return {
    title: titleIndex < 0 ? 'Kodex' : tokens[titleIndex + 1].content,
    chunks: starts.map((start, index) => ({
      id: index ? `section-${index}` : 'introduction',
      title: index ? headings[index - 1].title : '',
      text: lines.slice(start, starts[index + 1] ?? lines.length).join(''),
    })),
  };
}
