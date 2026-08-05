import { readdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { createRequire } from "node:module";

const FOUNDRY_APP = process.env.FOUNDRY_APP ?? "/home/gm/fvtt-app-v13";
const require = createRequire(`${FOUNDRY_APP}/package.json`);
const { ClassicLevel } = require("classic-level");

const DIR = resolve(process.argv[2]);
const CORE = process.argv[3] ?? "13.348";
const SYSTEM = process.argv[4] ?? "7.12.2";

const manifestPath = join(DIR, "module.json");
const manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
const before = JSON.stringify(manifest.compatibility);
manifest.compatibility = { minimum: "13", verified: "13.351", maximum: "13" };
for (const s of manifest.relationships?.systems ?? []) {
    if (s.id === "pf2e") s.compatibility = { minimum: "7.12.0", verified: SYSTEM };
}
manifest.version = `${manifest.version}-v13`;
await writeFile(manifestPath, JSON.stringify(manifest, null, 4), "utf-8");
console.log(`manifest: compatibility ${before} -> ${JSON.stringify(manifest.compatibility)}`);

const packsDir = join(DIR, "packs");
if (!existsSync(packsDir)) {
    console.log("no packs directory, nothing else to do");
    process.exit(0);
}

let touched = 0, scanned = 0;
for (const p of await readdir(packsDir, { withFileTypes: true })) {
    if (!p.isDirectory()) continue;
    const db = new ClassicLevel(join(packsDir, p.name), { valueEncoding: "json" });
    await db.open();
    const batch = db.batch();
    let n = 0;
    for await (const [key, doc] of db.iterator()) {
        scanned++;
        if (!doc?._stats?.coreVersion) continue;
        if (String(doc._stats.coreVersion).startsWith("13.")) continue;
        doc._stats.coreVersion = CORE;
        if (doc._stats.systemVersion) doc._stats.systemVersion = SYSTEM;
        batch.put(key, doc);
        n++;
    }
    await batch.write();
    await db.close();
    touched += n;
    console.log(`  ${p.name.padEnd(36)} restamped ${n}`);
}
console.log(`\nscanned ${scanned} documents, restamped ${touched} to coreVersion ${CORE}`);
