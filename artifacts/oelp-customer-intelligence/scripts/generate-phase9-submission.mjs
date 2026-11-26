import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import pptxgen from "pptxgenjs";
import { Document, HeadingLevel, ImageRun, Paragraph, Table, TableCell, TableRow, TextRun, WidthType, Packer } from "docx";
import { marked } from "marked";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "../../..");
const submissionDir = path.join(root, "docs/submission");
const generatedDir = path.join(root, "generated-artifacts/phase9");
const assetsDir = path.join(submissionDir, "assets");
const reportSourcePath = path.join(submissionDir, "FINAL_PROJECT_REPORT.source.md");
const notesPath = path.join(submissionDir, "PRESENTATION_SPEAKER_NOTES.md");
const registryPath = path.join(root, "research/sources.json");
const chromiumPath = "/repl/tools/bin/chromium";

fs.mkdirSync(generatedDir, { recursive: true });
fs.mkdirSync(path.join(assetsDir, "screenshots"), { recursive: true });

const sourceRegistry = JSON.parse(fs.readFileSync(registryPath, "utf8")).sources;
const sourceByKey = new Map(sourceRegistry.map((source) => [source.key, source]));
const sourceMarkdown = fs.readFileSync(reportSourcePath, "utf8");
const citationOrder = [];
const finalMarkdown = sourceMarkdown.replace(/\[@([a-z0-9-]+)\]/g, (match, key) => {
  const source = sourceByKey.get(key);
  if (!source) throw new Error(`Unknown literature citation key: ${key}`);
  if (!citationOrder.includes(key)) citationOrder.push(key);
  return `[${citationOrder.indexOf(key) + 1}](<${source.url}>)`;
});
const references = [
  "",
  "## References",
  "",
  ...citationOrder.map((key, index) => {
    const source = sourceByKey.get(key);
    const limitation = source.limitations ? ` ${source.limitations}` : "";
    const publicationDetails = source.publication_details ? ` ${source.publication_details}.` : "";
    return `${index + 1}. ${source.citation_author ?? "Author not listed"} (${source.publication_date}). **${source.title}.**${publicationDetails} ${source.url} (evidence: \`${source.saved_evidence_path}\`).${limitation}`;
  }),
  "",
];
const reportMarkdown = `${finalMarkdown.trimEnd()}\n${references.join("\n")}`;
fs.writeFileSync(path.join(submissionDir, "FINAL_PROJECT_REPORT.md"), reportMarkdown);

const reportHtml = marked.parse(reportMarkdown, { gfm: true });
const htmlAssetPaths = reportHtml.replaceAll('src="assets/', 'src="../../docs/submission/assets/');
const reportHtmlPath = path.join(generatedDir, "FINAL_PROJECT_REPORT.html");
fs.writeFileSync(
  reportHtmlPath,
  `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Final Project Report</title>
  <style>
    @page { size: A4; margin: 17mm 18mm 18mm; }
    * { box-sizing: border-box; }
    body { color:#243247; font: 10.6pt/1.48 Georgia, "Times New Roman", serif; }
    h1,h2,h3,h4 { color:#12344a; font-family:Arial,sans-serif; line-height:1.22; }
    h1 { font-size:21pt; margin:0 0 14pt; page-break-before:always; }
    h1:first-child { page-break-before:avoid; font-size:28pt; }
    h2 { font-size:15pt; margin:18pt 0 8pt; }
    h3 { font-size:12pt; margin:14pt 0 6pt; }
    p { margin:0 0 8pt; text-align:justify; }
    ul,ol { margin:0 0 10pt 20pt; padding:0; }
    li { margin:0 0 4pt; }
    blockquote { margin:10pt 18pt; color:#53657b; border-left:3px solid #178c91; padding-left:10pt; }
    table { border-collapse:collapse; width:100%; font:8.5pt/1.3 Arial,sans-serif; margin:8pt 0 12pt; }
    th { background:#e8f1f2; color:#12344a; text-align:left; }
    td,th { border:1px solid #cbd5df; padding:5pt 6pt; vertical-align:top; }
    tr { page-break-inside:avoid; }
    img { display:block; max-width:100%; max-height:6.2in; margin:12pt auto 5pt; object-fit:contain; }
    .page-break { break-after:page; page-break-after:always; height:0; }
    a { color:#086c79; text-decoration:underline; overflow-wrap:anywhere; }
    code { font:9pt "Courier New",monospace; color:#25445b; }
    strong { color:#153950; }
  </style></head><body>${htmlAssetPaths}</body></html>`,
);

const markdownTokens = marked.lexer(reportMarkdown, { gfm: true });
const docxChildren = [];
let pageBreakPending = false;
const pageSize = { width: 11906, height: 16838 };

function inlineRuns(tokens, style = {}) {
  const result = [];
  for (const token of tokens ?? []) {
    if (token.type === "text" || token.type === "escape") {
      result.push(new TextRun({ text: token.text ?? "", ...style }));
    } else if (token.type === "strong" || token.type === "em") {
      result.push(...inlineRuns(token.tokens, { ...style, bold: token.type === "strong" || style.bold, italics: token.type === "em" || style.italics }));
    } else if (token.type === "codespan") {
      result.push(new TextRun({ text: token.text, font: "Courier New", size: 18, ...style }));
    } else if (token.type === "link") {
      result.push(...inlineRuns(token.tokens, { ...style, color: "087B83", underline: {} }));
    } else if (token.type === "image") {
      const imagePath = path.resolve(submissionDir, token.href);
      if (!fs.existsSync(imagePath)) throw new Error(`Missing report image: ${imagePath}`);
      const dimensions = pngDimensions(imagePath);
      const scale = Math.min(620 / dimensions.width, 360 / dimensions.height);
      result.push(new ImageRun({
        data: fs.readFileSync(imagePath),
        transformation: { width: dimensions.width * scale, height: dimensions.height * scale },
        type: "png",
      }));
    } else if (token.type === "br") {
      result.push(new TextRun({ text: "", breakLine: true }));
    } else if (token.text) {
      result.push(new TextRun({ text: token.text, ...style }));
    }
  }
  return result.length ? result : [new TextRun({ text: "" })];
}

function docxParagraph(tokens, options = {}) {
  const pageBreakBefore = options.pageBreakBefore || pageBreakPending;
  pageBreakPending = false;
  return new Paragraph({
    spacing: { after: options.spacingAfter ?? 120, line: 280 },
    alignment: options.alignment,
    pageBreakBefore,
    heading: options.heading,
    indent: options.indent,
    bullet: options.bullet,
    children: inlineRuns(tokens, options.runStyle),
  });
}

function plainCellRuns(cellTokens) {
  return inlineRuns(cellTokens ?? []);
}

function pngDimensions(filePath) {
  const header = fs.readFileSync(filePath).subarray(16, 24);
  return { width: header.readUInt32BE(0), height: header.readUInt32BE(4) };
}

for (const token of markdownTokens) {
  if (token.type === "space") continue;
  if (token.type === "html") {
    if (token.text.includes("page-break")) pageBreakPending = true;
    continue;
  }
  if (token.type === "heading") {
    const headingMap = { 1: HeadingLevel.TITLE, 2: HeadingLevel.HEADING_1, 3: HeadingLevel.HEADING_2, 4: HeadingLevel.HEADING_3 };
    const firstTitle = token.depth === 1 && docxChildren.length === 0;
    docxChildren.push(docxParagraph(token.tokens, {
      heading: headingMap[token.depth],
      pageBreakBefore: token.depth === 1 ? !firstTitle : pageBreakPending,
      spacingAfter: token.depth === 1 ? 220 : 140,
      runStyle: { bold: token.depth <= 2, color: token.depth <= 2 ? "12344A" : "29536A" },
    }));
    continue;
  }
  if (token.type === "paragraph") {
    const isMetadata = token.text?.startsWith("**Student:**") || token.text?.startsWith("**Faculty / supervisor:**") || token.text?.startsWith("**Institution:**") || token.text?.startsWith("**Programme / course:**") || token.text?.startsWith("**Submission date:**");
    docxChildren.push(docxParagraph(token.tokens, {
      alignment: isMetadata ? "center" : undefined,
      runStyle: isMetadata ? { color: "516476" } : {},
    }));
    continue;
  }
  if (token.type === "list") {
    token.items.forEach((item, index) => {
      const tokens = item.tokens?.find((child) => child.type === "text")?.tokens;
      const prefix = token.ordered ? `${index + 1}. ` : "";
      docxChildren.push(new Paragraph({
        spacing: { after: 70, line: 270 },
        indent: { left: 360, hanging: token.ordered ? 0 : 180 },
        children: [new TextRun({ text: token.ordered ? prefix : "• " }), ...inlineRuns(tokens ?? marked.lexer(item.text ?? "")[0]?.tokens)],
      }));
    });
    continue;
  }
  if (token.type === "table") {
    const makeRow = (cells, header = false) => new TableRow({
      tableHeader: header,
      children: cells.map((cell) => new TableCell({
        width: { size: 100 / cells.length, type: WidthType.PERCENTAGE },
        shading: header ? { fill: "E8F1F2" } : undefined,
        margins: { top: 70, bottom: 70, left: 80, right: 80 },
        children: [new Paragraph({
          spacing: { after: 0 },
          children: plainCellRuns(cell.tokens),
        })],
      })),
    });
    docxChildren.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [makeRow(token.header, true), ...token.rows.map((row) => makeRow(row))],
    }));
    docxChildren.push(new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "" })] }));
    continue;
  }
  if (token.type === "image") {
    const imagePath = path.resolve(submissionDir, token.href);
    if (!fs.existsSync(imagePath)) throw new Error(`Missing report image: ${imagePath}`);
    const dimensions = pngDimensions(imagePath);
    const maxWidth = 640;
    const width = Math.min(maxWidth, dimensions.width);
    const height = Math.min(390, (dimensions.height / dimensions.width) * width);
    docxChildren.push(new Paragraph({
      alignment: "center",
      spacing: { before: 100, after: 80 },
      children: [new ImageRun({
        data: fs.readFileSync(imagePath),
        transformation: { width, height },
        type: "png",
      })],
    }));
    docxChildren.push(new Paragraph({
      alignment: "center",
      spacing: { after: 140 },
      children: [new TextRun({ text: token.text, italics: true, size: 18, color: "526477" })],
    }));
    continue;
  }
  if (token.type === "blockquote") {
    const quote = token.tokens?.flatMap((child) => child.tokens ?? []).filter((child) => child.type === "text") ?? [];
    docxChildren.push(docxParagraph(quote, { indent: { left: 360 }, runStyle: { italics: true, color: "526477" } }));
    continue;
  }
  if (token.type === "code") {
    docxChildren.push(new Paragraph({
      spacing: { before: 80, after: 100 },
      shading: { fill: "F1F4F6" },
      children: [new TextRun({ text: token.text, font: "Courier New", size: 17 })],
    }));
  }
}

const reportDoc = new Document({
  creator: "OELP Customer Intelligence",
  title: "Customer Segmentation and Retention Analysis Using Machine Learning and Statistical Modelling",
  description: "Final academic report; values are sourced from saved project evaluation artifacts.",
  sections: [{
    properties: {
      page: { size: pageSize, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } },
    },
    children: docxChildren,
  }],
});
const docxBuffer = await Packer.toBuffer(reportDoc);
fs.writeFileSync(path.join(submissionDir, "FINAL_PROJECT_REPORT.docx"), docxBuffer);

const slides = [
  {
    title: "Customer Segmentation and Retention Analysis",
    kicker: "FINAL ACADEMIC PROJECT",
    subtitle: "Machine learning, statistical modelling, and evidence-bounded decision support",
    layout: "cover",
    bullets: ["UCI Online Retail II · Year 1", "11 research notebooks · React + FastAPI dashboard", "Student / supervisor / institution: complete before submission"],
  },
  {
    title: "Why retention analysis is difficult",
    kicker: "RESEARCH MOTIVATION",
    layout: "cards",
    cards: [
      ["No formal cancellation", "A purchase gap does not identify permanent churn in a non-contractual retailer."],
      ["Different customer rhythms", "A fixed inactivity threshold can ignore personal purchase timing and sparse history."],
      ["Prediction ≠ intervention", "High predicted risk does not show who would respond to a retention action."],
    ],
  },
  {
    title: "Research problem and objectives",
    kicker: "SCOPE",
    layout: "bullets",
    bullets: [
      "Create a reproducible pipeline from transactions to customer histories.",
      "Describe RFM groups and purchase-gap distributions without labeling them as churn.",
      "Evaluate finite-horizon purchase and spending estimates on matured temporal splits.",
      "Expose reliability, method support, and limits in an application dashboard.",
    ],
  },
  {
    title: "Dataset and historical cohort",
    kicker: "STUDY DESIGN",
    layout: "stats",
    stats: [
      ["2009–2010", "Year 1 observation window"],
      ["19,213", "valid invoice events"],
      ["4,312", "full-period descriptive RFM customers"],
      ["3,373", "locked TEST customers per horizon"],
    ],
    caption: "Official TEST cutoff: 10 September 2010. Outcome windows mature at different dates.",
  },
  {
    title: "From transactions to decision support",
    kicker: "RESEARCH PIPELINE",
    layout: "image",
    image: "assets/diagrams/research_pipeline.png",
    bullets: ["Offline notebooks 01–11", "Saved evaluations and frozen models", "Read-only API and typed React client"],
  },
  {
    title: "RFM segmentation is descriptive",
    kicker: "NOTEBOOK 04",
    layout: "cards",
    cards: [
      ["Two clusters", "Selected descriptive K-means solution for 4,312 customers."],
      ["Stable assignments", "Mean seed ARI 0.998; minimum 0.9935."],
      ["Interpretation limit", "Not a prospective churn score, risk rank, or treatment-response segment."],
    ],
  },
  {
    title: "Personalized Purchase Clock",
    kicker: "NOTEBOOK 06",
    layout: "split-image",
    image: "assets/diagrams/purchase_clock_architecture.png",
    bullets: [
      "Discrete-time purchase hazard by interval.",
      "Cumulative probability of at least one purchase by 30, 60, or 90 days.",
      "A finite-horizon non-purchase is not permanent churn.",
    ],
  },
  {
    title: "Purchase prediction on locked TEST",
    kicker: "NOTEBOOK 06",
    layout: "chart",
    image: "assets/figures/purchase_clock_test_metrics.png",
    bullets: ["n = 3,373 at each horizon", "ROC-AUC, average precision, and Brier answer different questions"],
  },
  {
    title: "Spending forecast: best MAE, remaining bias",
    kicker: "NOTEBOOK 07",
    layout: "chart",
    image: "assets/figures/spending_forecast_test_metrics.png",
    bullets: ["Personalized two-stage estimate has lowest saved MAE at all horizons.", "Negative mean bias indicates aggregate underprediction.", "Forecasted revenue is not realized revenue."],
  },
  {
    title: "Behavior evidence is mixed",
    kicker: "NOTEBOOKS 08–09",
    layout: "cards",
    cards: [
      ["Supported", "H1 unusual personal gap and H3 falling revenue rate in multiple horizons."],
      ["Inconclusive", "H2 and H4 do not support a clear conclusion."],
      ["Not evaluable", "H5 needs a chronologically eligible saved model vintage that is unavailable."],
    ],
    bullets: ["Calibration and subgroup diagnostics describe cohorts, not individual guarantees.", "Input sensitivity is not causal explanation."],
  },
  {
    title: "Trajectories: shape, support, and uncertainty",
    kicker: "NOTEBOOK 11",
    layout: "chart",
    image: "assets/figures/trajectory_test_support_and_fda.png",
    bullets: ["Three descriptive shape clusters; 1,100 TEST customers eligible.", "659 curves support functional PCA.", "98.82% variance is TRAIN-fitted; TEST reconstruction RMSE is 0.006248."],
  },
  {
    title: "Revenue screening is not causal uplift",
    kicker: "NOTEBOOK 10",
    layout: "split-image",
    image: "assets/diagrams/expected_revenue_calculation.png",
    bullets: [
      "Expected revenue = purchase probability × conditional expected spending.",
      "Reference-based exposure is null / not estimable.",
      "Scenario response, uplift, and cost inputs are hypothetical.",
    ],
  },
  {
    title: "Research dashboard and system",
    kicker: "APPLICATION",
    layout: "screenshot",
    image: "assets/screenshots/research-overview.png",
    bullets: [
      "10 routes: overview, segments, customer, behavior, forecasting, performance, revenue, trajectories, upload, research.",
      "FastAPI serves frozen artifacts; notebooks stay offline.",
      "Example walkthrough customer: 18102; do not reveal TEST outcome.",
    ],
  },
  {
    title: "Validation protects the saved evidence",
    kicker: "ENGINEERING",
    layout: "cards",
    cards: [
      ["195 Python tests", "Phase 8 merged baseline"],
      ["32 React tests", "Plus 28 Chromium end-to-end tests"],
      ["37 GET checks", "Plus 67 protected artifact matches"],
    ],
    bullets: ["Cold trajectory summary: 4.26s → 312ms; initial-route gzip: −60.3%.", "Typecheck and production build passed on the merged baseline.", "Production deploy, Firefox/WebKit, and manual screen-reader checks were not covered."],
  },
  {
    title: "Conclusions and next evidence needed",
    kicker: "TAKEAWAYS",
    layout: "bullets",
    bullets: [
      "Saved Personalized Purchase Clock is strongest among saved probability comparators on this historical TEST.",
      "Spending MAE is lowest, while bias and aggregate underprediction remain.",
      "Revenue exposure is not estimable; behavior evidence is mixed; trajectory incremental value is inconclusive.",
      "Future causal retention claims need prospective treatment assignment and response data.",
    ],
  },
];

const notesMarkdown = fs.readFileSync(notesPath, "utf8");
const noteHeadings = [...notesMarkdown.matchAll(/^## Slide \d+\s+—\s+.+$/gm)];
const noteSections = noteHeadings.map((heading, index) => {
  const start = heading.index + heading[0].length;
  const end = noteHeadings[index + 1]?.index ?? notesMarkdown.length;
  return notesMarkdown.slice(start, end).trim();
});
if (slides.length !== 15 || noteSections.length !== 15) {
  throw new Error(`Expected 15 slides and notes; found ${slides.length} slides and ${noteSections.length} notes.`);
}

function imagePathFromHref(href) {
  return path.resolve(submissionDir, href);
}

function imageFit(filePath, x, y, maxW, maxH) {
  const { width, height } = pngDimensions(filePath);
  const scale = Math.min(maxW / width, maxH / height);
  const w = width * scale;
  const h = height * scale;
  return { x: x + (maxW - w) / 2, y: y + (maxH - h) / 2, w, h };
}

function addBase(slide, index, kicker) {
  slide.background = { color: "F6F8FA" };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.12, line: { color: "117E83", transparency: 100 }, fill: { color: "117E83" } });
  slide.addText("OELP CUSTOMER INTELLIGENCE", { x: 0.55, y: 0.28, w: 5.5, h: 0.22, fontFace: "Aptos", fontSize: 9, bold: true, charSpacing: 1.1, color: "577080", margin: 0 });
  slide.addText(kicker, { x: 0.55, y: 0.56, w: 8.5, h: 0.22, fontFace: "Aptos", fontSize: 10, bold: true, charSpacing: 1.2, color: "117E83", margin: 0 });
  slide.addText(String(index).padStart(2, "0"), { x: 12.35, y: 7.08, w: 0.45, h: 0.2, fontFace: "Aptos", fontSize: 9, color: "758392", align: "right", margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 6.98, w: 12.25, h: 0, line: { color: "D9E1E8", width: 1 } });
}

function addTitle(slide, title, y = 0.9, w = 12.0) {
  slide.addText(title, { x: 0.55, y, w, h: 0.7, fontFace: "Aptos Display", fontSize: 27, bold: true, color: "15384F", margin: 0, breakLine: false, fit: "shrink" });
}

function addBullets(slide, bullets, x = 0.7, y = 1.85, w = 5.2, fontSize = 17) {
  let cursor = y;
  for (const bullet of bullets ?? []) {
    slide.addShape(pptx.ShapeType.ellipse, { x, y: cursor + 0.12, w: 0.11, h: 0.11, line: { color: "117E83", transparency: 100 }, fill: { color: "117E83" } });
    const lines = Math.max(1, Math.ceil(bullet.length / 47));
    const h = Math.min(0.9, 0.37 + (lines - 1) * 0.21);
    slide.addText(bullet, { x: x + 0.25, y: cursor, w: w - 0.25, h, fontFace: "Aptos", fontSize, color: "334A5B", margin: 0, valign: "top", breakLine: false, fit: "shrink" });
    cursor += h + 0.21;
  }
}

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OELP Customer Intelligence";
pptx.subject = "Final academic project presentation";
pptx.title = "Customer Segmentation and Retention Analysis";
pptx.company = "OELP Customer Intelligence";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const htmlSlides = [];
for (let index = 0; index < slides.length; index += 1) {
  const data = slides[index];
  const slide = pptx.addSlide();
  slide.addNotes(noteSections[index]);
  const slideNumber = index + 1;
  if (data.layout === "cover") {
    slide.background = { color: "15384F" };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.18, h: 7.5, line: { color: "18A0A0", transparency: 100 }, fill: { color: "18A0A0" } });
    slide.addText(data.kicker, { x: 0.95, y: 0.65, w: 9.8, h: 0.3, fontFace: "Aptos", fontSize: 12, charSpacing: 2, bold: true, color: "73D3CC", margin: 0 });
    slide.addText(data.title, { x: 0.95, y: 1.45, w: 10.7, h: 1.45, fontFace: "Aptos Display", fontSize: 34, bold: true, color: "FFFFFF", margin: 0, breakLine: false, fit: "shrink" });
    slide.addText(data.subtitle, { x: 0.98, y: 3.15, w: 10.2, h: 0.62, fontFace: "Aptos", fontSize: 19, color: "D9E7EE", margin: 0 });
    slide.addShape(pptx.ShapeType.line, { x: 0.98, y: 4.02, w: 10.3, h: 0, line: { color: "496577", width: 1.1 } });
    data.bullets.forEach((bullet, i) => slide.addText(bullet, { x: 0.98, y: 4.35 + i * 0.43, w: 10.6, h: 0.3, fontFace: "Aptos", fontSize: 14, color: "C7D6DE", margin: 0 }));
    slide.addText("01", { x: 12.35, y: 7.08, w: 0.45, h: 0.2, fontFace: "Aptos", fontSize: 9, color: "A6BAC6", align: "right", margin: 0 });
  } else {
    addBase(slide, slideNumber, data.kicker);
    addTitle(slide, data.title);
    if (data.layout === "cards") {
      const cards = data.cards ?? [];
      const cols = cards.length === 3 ? 3 : 2;
      const gap = 0.23;
      const cardW = (12.1 - gap * (cols - 1)) / cols;
      const cardY = 1.9;
      const cardH = 2.55;
      cards.forEach(([heading, body], cardIndex) => {
        const col = cardIndex % cols;
        const row = Math.floor(cardIndex / cols);
        const x = 0.62 + col * (cardW + gap);
        const y = cardY + row * (cardH + 0.25);
        slide.addShape(pptx.ShapeType.roundRect, { x, y, w: cardW, h: cardH, rectRadius: 0.12, line: { color: "D5E0E6", width: 1 }, fill: { color: cardIndex % 2 ? "FFFFFF" : "EAF4F4" } });
        slide.addText(heading, { x: x + 0.23, y: y + 0.27, w: cardW - 0.46, h: 0.45, fontFace: "Aptos Display", fontSize: 17, bold: true, color: "15384F", margin: 0, fit: "shrink" });
        slide.addText(body, { x: x + 0.23, y: y + 0.86, w: cardW - 0.46, h: 1.35, fontFace: "Aptos", fontSize: 14, color: "425A6A", margin: 0.02, valign: "top", fit: "shrink" });
      });
      if (data.bullets) addBullets(slide, data.bullets, 0.85, cardY + cardH + 0.3, 11.7, 14);
    } else if (data.layout === "stats") {
      const statW = 2.87;
      data.stats.forEach(([value, label], statIndex) => {
        const x = 0.63 + statIndex * 3.03;
        slide.addShape(pptx.ShapeType.roundRect, { x, y: 2.15, w: statW, h: 2.05, line: { color: "D7E0E6", width: 1 }, fill: { color: statIndex % 2 ? "FFFFFF" : "EAF4F4" } });
        slide.addText(value, { x: x + 0.15, y: 2.58, w: statW - 0.3, h: 0.55, fontFace: "Aptos Display", fontSize: 27, bold: true, color: "117E83", align: "center", margin: 0, fit: "shrink" });
        slide.addText(label, { x: x + 0.22, y: 3.31, w: statW - 0.44, h: 0.55, fontFace: "Aptos", fontSize: 13, color: "425A6A", align: "center", margin: 0, fit: "shrink" });
      });
      slide.addText(data.caption, { x: 0.8, y: 4.75, w: 11.8, h: 0.65, fontFace: "Aptos", fontSize: 16, color: "425A6A", align: "center", margin: 0, fit: "shrink" });
    } else if (data.layout === "chart") {
      const image = imagePathFromHref(data.image);
      const bounds = imageFit(image, 0.7, 1.72, 11.95, 4.15);
      slide.addImage({ path: image, ...bounds });
      addBullets(slide, data.bullets, 0.85, 5.95, 11.6, 12);
    } else if (data.layout === "image") {
      addBullets(slide, data.bullets, 0.75, 2.15, 3.45, 15);
      const image = imagePathFromHref(data.image);
      const bounds = imageFit(image, 4.45, 2.0, 8.2, 3.5);
      slide.addImage({ path: image, ...bounds });
    } else if (data.layout === "split-image" || data.layout === "screenshot") {
      addBullets(slide, data.bullets, 0.72, 1.88, 5.25, data.layout === "screenshot" ? 14 : 15);
      const image = imagePathFromHref(data.image);
      if (!fs.existsSync(image)) throw new Error(`Missing presentation image: ${image}`);
      const bounds = imageFit(image, 6.15, 1.78, 6.45, 4.6);
        slide.addShape(pptx.ShapeType.roundRect, { ...bounds, x: bounds.x - 0.1, y: bounds.y - 0.1, w: bounds.w + 0.2, h: bounds.h + 0.2, line: { color: "D5E0E6", width: 1 }, fill: { color: "FFFFFF" } });
      slide.addImage({ path: image, ...bounds });
    } else {
      addBullets(slide, data.bullets, 0.85, 2.0, 11.4, 18);
    }
  }
  const htmlBullets = data.bullets?.map((bullet) => `<li>${bullet}</li>`).join("") ?? "";
  const htmlCards = data.cards?.map(([heading, body]) => `<div class="card"><h3>${heading}</h3><p>${body}</p></div>`).join("") ?? "";
  const htmlStats = data.stats?.map(([value, label]) => `<div class="stat"><b>${value}</b><span>${label}</span></div>`).join("") ?? "";
  const htmlImage = data.image ? `<img class="visual" src="../../docs/submission/${data.image}" alt="">` : "";
  htmlSlides.push(`<section class="slide ${data.layout}"><div class="kicker">${data.kicker}</div><h1>${data.title}</h1>${data.subtitle ? `<h2>${data.subtitle}</h2>` : ""}${htmlCards ? `<div class="cards">${htmlCards}</div>` : ""}${htmlStats ? `<div class="stats">${htmlStats}</div><p class="caption">${data.caption}</p>` : ""}${htmlImage}${htmlBullets ? `<ul>${htmlBullets}</ul>` : ""}</section>`);
}

const pptxPath = path.join(submissionDir, "FINAL_PRESENTATION.pptx");
await pptx.writeFile({ fileName: pptxPath });

const printHtml = path.join(generatedDir, "FINAL_PRESENTATION.html");
const printStyle = `
@page{size:13.333in 7.5in;margin:0}*{box-sizing:border-box}body{margin:0;background:#e9eef1;font:15px Arial,sans-serif;color:#334a5b}
.slide{position:relative;width:13.333in;height:7.2in;max-height:7.2in;padding:.5in .62in;background:#f6f8fa;break-inside:avoid;page-break-inside:avoid;overflow:hidden}
body:not(.single) .slide:not(:first-child){page-break-before:always;break-before:page}
.slide:before{content:"";position:absolute;left:0;top:0;width:100%;height:.12in;background:#117e83}
.kicker{font-size:12px;letter-spacing:2px;font-weight:700;color:#117e83;margin:0 0 22px}
h1{font-size:34px;line-height:1.1;color:#15384f;margin:0 0 28px;max-width:11.8in}h2{font-size:20px;color:#d9e7ee;font-weight:400}
ul{position:relative;z-index:2;max-width:5.5in;padding-left:23px;margin:30px 0;font-size:19px;line-height:1.55}li{margin:0 0 15px}
.cards{display:flex;gap:16px;margin-top:45px}.card,.stat{background:#eaf4f4;border:1px solid #d5e0e6;border-radius:12px;padding:22px;flex:1;min-height:175px}.card h3{color:#15384f;font-size:18px}.card p,.caption{font-size:15px;line-height:1.45}
.stats{display:flex;gap:18px;margin-top:70px}.stat{height:160px;display:flex;flex-direction:column;justify-content:center;text-align:center;background:#fff}.stat b{font-size:30px;color:#117e83;margin-bottom:12px}.stat span{font-size:14px}
.visual{position:absolute;right:.55in;top:1.7in;max-width:6.1in;max-height:4.8in;object-fit:contain}.image .visual{max-width:8.2in;max-height:3.8in;top:2.05in}.chart .visual{left:.65in;right:.65in;top:1.55in;max-width:12in;max-height:4.5in}.screenshot .visual{max-width:6.2in;max-height:4.75in}.split-image ul,.screenshot ul{max-width:5.2in;font-size:16px;margin-top:34px}
.cover{background:#15384f;color:#fff;padding:1in}.cover:before{width:.18in;height:100%;background:#18a0a0}.cover .kicker{color:#73d3cc;margin-bottom:38px}.cover h1{font-size:42px;color:#fff;max-width:10.7in;margin-bottom:22px}.cover h2{max-width:10in}.cover ul{max-width:11in;font-size:16px;line-height:1.35;margin-top:45px}.bullets ul{max-width:11in;margin-top:45px;font-size:20px}.caption{margin-top:40px;text-align:center}
`;
fs.writeFileSync(printHtml, `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Final Presentation</title><style>${printStyle}</style></head><body>${htmlSlides.join("\n")}</body></html>`);

function printPdf(inputHtml, outputPdf, profileName) {
  const result = spawnSync(chromiumPath, [
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-pdf-header-footer",
    `--user-data-dir=/tmp/oelp-${profileName}`,
    `--print-to-pdf=${outputPdf}`,
    `file://${inputHtml}`,
  ], { encoding: "utf8", timeout: 120000 });
  if (result.status !== 0 || !fs.existsSync(outputPdf)) {
    throw new Error(`Chromium PDF export failed (${profileName}): ${result.stderr || result.stdout}`);
  }
}

printPdf(reportHtmlPath, path.join(submissionDir, "FINAL_PROJECT_REPORT.pdf"), "report");
const slidePdfPaths = [];
for (let index = 0; index < htmlSlides.length; index += 1) {
  const number = String(index + 1).padStart(2, "0");
  const slideHtmlPath = path.join(generatedDir, `FINAL_PRESENTATION_${number}.html`);
  const slidePdfPath = path.join(generatedDir, `FINAL_PRESENTATION_${number}.pdf`);
  fs.writeFileSync(slideHtmlPath, `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Slide ${number}</title><style>${printStyle}</style></head><body class="single">${htmlSlides[index]}</body></html>`);
  printPdf(slideHtmlPath, slidePdfPath, `slide-${number}`);
  const info = spawnSync("pdfinfo", [slidePdfPath], { encoding: "utf8" });
  const pages = Number(info.stdout?.match(/Pages:\s+(\d+)/)?.[1] ?? 0);
  if (pages < 1) throw new Error(`Slide ${number} did not export a PDF page.`);
  if (pages > 1) {
    const overflowText = spawnSync("pdftotext", ["-f", "2", "-l", String(pages), slidePdfPath, "-"], { encoding: "utf8" }).stdout.trim();
    if (overflowText.length > 0) throw new Error(`Slide ${number} content overflowed onto additional pages.`);
  }
  const singlePagePattern = path.join(generatedDir, `presentation-page-${number}-%d.pdf`);
  const extractResult = spawnSync("pdfseparate", ["-f", "1", "-l", "1", slidePdfPath, singlePagePattern], { encoding: "utf8" });
  if (extractResult.status !== 0) throw new Error(`Could not extract slide ${number}: ${extractResult.stderr || extractResult.stdout}`);
  slidePdfPaths.push(path.join(generatedDir, `presentation-page-${number}-1.pdf`));
}
const mergedPdf = path.join(submissionDir, "FINAL_PRESENTATION.pdf");
const mergeResult = spawnSync("pdfunite", [...slidePdfPaths, mergedPdf], { encoding: "utf8", timeout: 120000 });
if (mergeResult.status !== 0 || !fs.existsSync(mergedPdf)) {
  throw new Error(`Could not combine the 15 slide PDFs: ${mergeResult.stderr || mergeResult.stdout}`);
}

console.log(JSON.stringify({
  citations: citationOrder.length,
  reportMarkdown: path.join(submissionDir, "FINAL_PROJECT_REPORT.md"),
  reportDocxBytes: fs.statSync(path.join(submissionDir, "FINAL_PROJECT_REPORT.docx")).size,
  reportPdfBytes: fs.statSync(path.join(submissionDir, "FINAL_PROJECT_REPORT.pdf")).size,
  presentationSlides: slides.length,
  presentationPptxBytes: fs.statSync(pptxPath).size,
  presentationPdfBytes: fs.statSync(path.join(submissionDir, "FINAL_PRESENTATION.pdf")).size,
  printHtml,
}, null, 2));
