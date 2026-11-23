import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const barrelPath = path.resolve(directory, "../../api-zod/src/index.ts");
const content = await readFile(barrelPath, "utf8");
const lines = content
  .split(/\r?\n/)
  .filter((line) => !/^export \* from ['"]\.\/generated\/api['"];?$/.test(line));

if (!lines.some((line) => /^export \* as schemas from ['"]\.\/generated\/api['"];?$/.test(line))) {
  lines.push('export * as schemas from "./generated/api";');
}

await writeFile(barrelPath, `${lines.filter(Boolean).join("\n")}\n`);
