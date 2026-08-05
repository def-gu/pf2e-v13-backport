import { readdir, readFile, rm, mkdir } from "node:fs/promises";
import { join, resolve } from "node:path";
import { createRequire } from "node:module";

const FOUNDRY_APP = process.env.FOUNDRY_APP ?? "/home/gm/fvtt-app-v13";
const require = createRequire(`${FOUNDRY_APP}/package.json`);
const { ClassicLevel } = require("classic-level");

const SRC = resolve(process.argv[2] ?? "merged-out/packs");
const DEST = resolve(process.argv[3] ?? "merged-out/packs-compiled");
const MANIFEST = resolve(process.argv[4] ?? "merged-out/side/system.json");

const CORE_VERSION = "13.348";
const SYSTEM_VERSION = "7.12.2";

const LAYOUT = {
    Actor: ["actors", "items", "actors.items"],
    Item: ["items", null, null],
    JournalEntry: ["journal", "pages", "journal.pages"],
    Macro: ["macros", null, null],
    RollTable: ["tables", "results", "tables.results"],
};

const manifest = JSON.parse(await readFile(MANIFEST, "utf-8"));
const byDir = new Map(
    manifest.packs.map(p => [p.path.replace(/\/$/, "").split("/").pop(), p]),
);

let totalParents = 0, totalChildren = 0, totalFolders = 0, packs = 0;

for (const entry of await readdir(SRC, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const meta = byDir.get(entry.name);
    if (!meta) { console.error(`  ! ${entry.name}: not in manifest, skipped`); continue; }
    const layout = LAYOUT[meta.type];
    if (!layout) { console.error(`  ! ${entry.name}: type ${meta.type}, skipped`); continue; }
    const [collection, embField, embCollection] = layout;

    const dbPath = join(DEST, entry.name);
    await rm(dbPath, { recursive: true, force: true });
    await mkdir(dbPath, { recursive: true });
    const db = new ClassicLevel(dbPath, { valueEncoding: "json" });
    await db.open();
    const batch = db.batch();

    let parents = 0, children = 0, folders = 0;
    for (const fn of await readdir(join(SRC, entry.name))) {
        if (!fn.endsWith(".json")) continue;
        const parsed = JSON.parse(await readFile(join(SRC, entry.name, fn), "utf-8"));

        if (fn === "_folders.json") {
            for (const f of Array.isArray(parsed) ? parsed : []) {
                if (f?._id) { batch.put(`!folders!${f._id}`, f); folders++; }
            }
            continue;
        }
        if (!parsed?._id) continue;

        const doc = { ...parsed };
        doc._stats = {
            ...(doc._stats ?? {}),
            coreVersion: CORE_VERSION,
            systemId: "pf2e",
            systemVersion: SYSTEM_VERSION,
            compendiumSource: `Compendium.pf2e.${meta.name}.${meta.type}.${doc._id}`,
        };

        if (embField && Array.isArray(doc[embField])) {
            const ids = [];
            for (const raw of doc[embField]) {
                if (!raw?._id) continue;
                const child = { ...raw };
                child._stats = {
                    ...(child._stats ?? {}),
                    coreVersion: CORE_VERSION,
                    systemId: "pf2e",
                    systemVersion: SYSTEM_VERSION,
                };
                batch.put(`!${embCollection}!${doc._id}.${child._id}`, child);
                ids.push(child._id);
                children++;
            }
            doc[embField] = ids;
        }

        batch.put(`!${collection}!${doc._id}`, doc);
        parents++;
    }

    await batch.write();
    await db.close();
    totalParents += parents; totalChildren += children; totalFolders += folders;
    packs++;
    if (children > 2000 || parents > 2000) {
        console.log(`  ${entry.name.padEnd(30)} ${String(parents).padStart(5)} docs, ${String(children).padStart(6)} embedded`);
    }
}

console.log(`\n${packs} packs | ${totalParents} documents | ${totalChildren} embedded | ${totalFolders} folders`);
console.log(`-> ${DEST}`);
