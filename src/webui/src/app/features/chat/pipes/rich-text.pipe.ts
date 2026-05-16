import { Pipe, PipeTransform, SecurityContext, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

/**
 * RichTextPipe converts a raw assistant message string into safe rendered HTML.
 *
 * Responsibilities:
 *  - Extract <think>...</think> reasoning blocks and render them as a
 *    collapsible "Suy nghĩ" panel above/inline with the answer. While the
 *    assistant is still streaming and a <think> tag is open but not yet
 *    closed, the partial reasoning is shown live in a "Đang suy nghĩ..."
 *    panel that grows with each token.
 *  - Escape raw HTML in the source text to prevent XSS.
 *  - Render a minimal but useful markdown subset:
 *      headings (#, ##, ###)
 *      bold (**text**), italic (*text* / _text_)
 *      inline code (`code`) and fenced code blocks (```...```)
 *      unordered lists (-, *, +)
 *      ordered lists (1. ...)
 *      blockquotes (> ...)
 *      links [text](url)
 *      horizontal rules (---)
 *      paragraphs / line breaks
 *
 * The output is then passed through Angular's DomSanitizer for an extra
 * defence-in-depth layer before being bound via [innerHTML].
 */
@Pipe({
  name: 'richText',
  standalone: true,
})
export class RichTextPipe implements PipeTransform {
  private readonly sanitizer = inject(DomSanitizer);

  transform(value: string | null | undefined): SafeHtml {
    const raw = value ?? '';
    const html = renderRichText(raw);
    return this.sanitizer.sanitize(SecurityContext.HTML, html) ?? '';
  }
}

interface HtmlPlaceholder {
  token: string;
  html: string;
}

const HTML_BLOCK_RE = /\u0000HTMLBLOCK(\d+)\u0000/;

/**
 * Top-level entry: pull <think> blocks out as raw-HTML placeholders, render
 * the rest as markdown, then re-inject the placeholders.
 */
function renderRichText(input: string): string {
  if (!input) {
    return '';
  }

  const htmlBlocks: HtmlPlaceholder[] = [];

  // 1. Replace COMPLETED <think>...</think> blocks with placeholders.
  let working = input.replace(
    /<think\b[^>]*>([\s\S]*?)<\/think\s*>/gi,
    (_m, inner: string) => makeThinkPlaceholder(inner, false, htmlBlocks),
  );

  // 2. If there is still an open <think> with no closing tag (mid-stream),
  //    convert the trailing portion into a "thinking..." placeholder so the
  //    user sees the reasoning as it streams.
  const openMatch = /<think\b[^>]*>([\s\S]*)$/i.exec(working);
  if (openMatch) {
    const placeholder = makeThinkPlaceholder(openMatch[1], true, htmlBlocks);
    working = working.slice(0, openMatch.index) + placeholder;
  }

  // 3. Render the remaining markdown, telling the renderer to leave any
  //    HTML placeholders untouched as standalone blocks.
  const rendered = renderMarkdown(working);

  // 4. Substitute placeholders back with the real HTML.
  let html = rendered;
  for (const block of htmlBlocks) {
    html = html.split(block.token).join(block.html);
  }
  return html;
}

function makeThinkPlaceholder(
  innerRaw: string,
  isStreaming: boolean,
  htmlBlocks: HtmlPlaceholder[],
): string {
  const trimmedInner = innerRaw.replace(/^\s+/, '').replace(/\s+$/, '');
  const innerHtml = trimmedInner ? renderMarkdown(trimmedInner) : '';
  const summary = isStreaming ? 'Đang suy nghĩ…' : 'Suy nghĩ';
  const cls = isStreaming ? 'think-block thinking' : 'think-block';
  const indicator = isStreaming
    ? '<span class="think-dots"><span></span><span></span><span></span></span>'
    : '';
  const token = `\u0000HTMLBLOCK${htmlBlocks.length}\u0000`;
  htmlBlocks.push({
    token,
    html:
      `<details class="${cls}" open>` +
      `<summary><span class="think-icon">💭</span><span class="think-label">${summary}</span>${indicator}</summary>` +
      `<div class="think-content">${innerHtml || '<em class="think-empty">…</em>'}</div>` +
      `</details>`,
  });
  return `\n${token}\n`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

interface CodePlaceholder {
  token: string;
  html: string;
}

/**
 * Convert a markdown string to HTML. Recognises pre-existing
 * `\u0000HTMLBLOCK<n>\u0000` markers as opaque block elements and leaves
 * them untouched (used by the <think> extraction above).
 */
function renderMarkdown(src: string): string {
  if (!src) {
    return '';
  }

  let text = src.replace(/\r\n?/g, '\n');

  const codeBlocks: CodePlaceholder[] = [];
  text = text.replace(/```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g, (_m, lang: string, code: string) => {
    const token = `\u0000CODEBLOCK${codeBlocks.length}\u0000`;
    const langClass = lang ? ` class="language-${escapeHtml(lang)}"` : '';
    const html = `<pre><code${langClass}>${escapeHtml(code.replace(/\n$/, ''))}</code></pre>`;
    codeBlocks.push({ token, html });
    return token;
  });

  const inlineCodes: CodePlaceholder[] = [];
  text = text.replace(/`([^`\n]+?)`/g, (_m, code: string) => {
    const token = `\u0000INLINECODE${inlineCodes.length}\u0000`;
    inlineCodes.push({ token, html: `<code>${escapeHtml(code)}</code>` });
    return token;
  });

  text = escapeHtml(text);

  const lines = text.split('\n');
  const out: string[] = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Pre-rendered HTML placeholder (e.g. <think> block) — pass through.
    if (HTML_BLOCK_RE.test(trimmed) && trimmed.replace(HTML_BLOCK_RE, '') === '') {
      out.push(trimmed);
      i++;
      continue;
    }

    if (/^\s*(?:---+|\*\*\*+|___+)\s*$/.test(line)) {
      out.push('<hr />');
      i++;
      continue;
    }

    const heading = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      out.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
      i++;
      continue;
    }

    if (/^\s*>\s?/.test(line)) {
      const buf: string[] = [];
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
        buf.push(lines[i].replace(/^\s*>\s?/, ''));
        i++;
      }
      out.push(`<blockquote>${renderInline(buf.join(' '))}</blockquote>`);
      continue;
    }

    if (/^\s*[-*+]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*+]\s+/, ''));
        i++;
      }
      out.push(
        '<ul>' +
          items.map((it) => `<li>${renderInline(it)}</li>`).join('') +
          '</ul>',
      );
      continue;
    }

    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i++;
      }
      out.push(
        '<ol>' +
          items.map((it) => `<li>${renderInline(it)}</li>`).join('') +
          '</ol>',
      );
      continue;
    }

    if (line.trim() === '') {
      out.push('');
      i++;
      continue;
    }

    if (/^\u0000CODEBLOCK\d+\u0000$/.test(trimmed)) {
      out.push(trimmed);
      i++;
      continue;
    }

    const para: string[] = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !/^(#{1,6})\s+/.test(lines[i]) &&
      !/^\s*[-*+]\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i]) &&
      !/^\s*>\s?/.test(lines[i]) &&
      !/^\s*(?:---+|\*\*\*+|___+)\s*$/.test(lines[i]) &&
      !/^\u0000CODEBLOCK\d+\u0000$/.test(lines[i].trim()) &&
      !(
        HTML_BLOCK_RE.test(lines[i].trim()) &&
        lines[i].trim().replace(HTML_BLOCK_RE, '') === ''
      )
    ) {
      para.push(lines[i]);
      i++;
    }
    out.push(`<p>${renderInline(para.join('\n')).replace(/\n/g, '<br />')}</p>`);
  }

  let html = out.filter((s) => s !== '').join('\n');

  for (const ic of inlineCodes) {
    html = html.split(ic.token).join(ic.html);
  }
  for (const cb of codeBlocks) {
    html = html.split(cb.token).join(cb.html);
  }

  return html;
}

/**
 * Inline transforms applied to already HTML-escaped text.
 * Order matters: bold before italic so `**x**` is not eaten by `*x*`.
 */
function renderInline(text: string): string {
  let t = text;

  // Auto-link bare http/https URLs not already inside a markdown link
  t = t.replace(
    /(?<!\]\()(https?:\/\/[^\s<>"'&]+)/g,
    (url) =>
      `<a href="${sanitizeUrl(url)}" target="_blank" rel="noopener noreferrer">${url}</a>`,
  );

  t = t.replace(
    /\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;([^&]*)&quot;)?\)/g,
    (_m, label: string, url: string, title?: string) => {
      const safeUrl = sanitizeUrl(url);
      const titleAttr = title ? ` title="${title}"` : '';
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer"${titleAttr}>${label}</a>`;
    },
  );

  t = t.replace(/\*\*([^\s*][\s\S]*?[^\s*]|\S)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/__([^\s_][\s\S]*?[^\s_]|\S)__/g, '<strong>$1</strong>');

  t = t.replace(/(^|[^*])\*([^\s*][\s\S]*?[^\s*]|\S)\*(?!\*)/g, '$1<em>$2</em>');
  t = t.replace(/(^|[^_\w])_([^\s_][\s\S]*?[^\s_]|\S)_(?!\w)/g, '$1<em>$2</em>');

  return t;
}

function sanitizeUrl(url: string): string {
  const trimmed = url.trim();
  if (/^(https?:|mailto:|tel:|\/|#|\.\/|\.\.\/)/i.test(trimmed)) {
    return trimmed.replace(/"/g, '%22');
  }
  return '#';
}
