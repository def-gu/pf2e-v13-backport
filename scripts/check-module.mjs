import { readdir, readFile, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { createRequire } from "node:module";

const FOUNDRY_APP = process.env.FOUNDRY_APP ?? "/home/gm/fvtt-app-v13";
const require = createRequire(`${FOUNDRY_APP}/package.json`);
const { ClassicLevel } = require("classic-level");

const DIR = resolve(process.argv[2] ?? ".");
const CORE_GENERATION = 13;

if (!existsSync(join(DIR, "module.json"))) {
    console.error(`no module.json in ${DIR}`);
    process.exit(2);
}

const manifest = JSON.parse(await readFile(join(DIR, "module.json"), "utf-8"));

async function coreSymbols() {
    const names = new Set();
    const patterns = [
        /export\s+(?:default\s+)?(?:async\s+)?(?:class|function|const|let|var)\s+([A-Za-z_$][\w$]*)/g,
        /^\s{2,6}(?:static\s+)?(?:async\s+)?(?:get\s+|set\s+)?([A-Za-z_$][\w$]*)\s*[(=]/gm,
    ];
    const reexport = /export\s*\{([^}]*)\}/g;
    for (const sub of ["common", "client"]) {
        const root = join(FOUNDRY_APP, sub);
        const stack = [root];
        while (stack.length) {
            const dir = stack.pop();
            let entries;
            try { entries = await readdir(dir, { withFileTypes: true }); } catch { continue; }
            for (const e of entries) {
                const p = join(dir, e.name);
                if (e.isDirectory()) {
                    stack.push(p);
                    names.add(e.name);
                    continue;
                }
                if (!e.name.endsWith(".mjs")) continue;
                names.add(e.name.replace(/\.mjs$/, "").replace(/^_/, ""));
                const src = await readFile(p, "utf-8");
                for (const re of patterns) {
                    for (const m of src.matchAll(re)) names.add(m[1]);
                }
                for (const m of src.matchAll(reexport)) {
                    for (const piece of m[1].split(",")) {
                        const name = piece.trim().split(/\s+as\s+/).pop()?.trim();
                        if (name && /^[A-Za-z_$][\w$]*$/.test(name)) names.add(name);
                    }
                }
            }
        }
    }
    return names;
}

async function scanSources() {
    const refs = new Map();
    const stack = [DIR];
    const wanted = /foundry\.[A-Za-z][\w$]*(?:\.[A-Za-z][\w$]*)+/g;
    while (stack.length) {
        const dir = stack.pop();
        let entries;
        try { entries = await readdir(dir, { withFileTypes: true }); } catch { continue; }
        for (const e of entries) {
            if (e.name === "node_modules" || e.name === ".git" || e.name === "packs") continue;
            const p = join(dir, e.name);
            if (e.isDirectory()) { stack.push(p); continue; }
            if (!/\.(m?js|ts|svelte)$/.test(e.name)) continue;
            const src = await readFile(p, "utf-8");
            for (const m of src.matchAll(wanted)) {
                const leaf = m[0].split(".").pop();
                if (!refs.has(leaf)) refs.set(leaf, new Set());
                refs.get(leaf).add(`${m[0]} (${p.slice(DIR.length + 1)})`);
            }
        }
    }
    return refs;
}

async function scanPacks() {
    const dir = join(DIR, "packs");
    const out = { total: 0, newer: 0, versions: new Map(), unreadable: [] };
    if (!existsSync(dir)) return out;
    for (const e of await readdir(dir, { withFileTypes: true })) {
        if (!e.isDirectory()) continue;
        const db = new ClassicLevel(join(dir, e.name), { valueEncoding: "json" });
        try { await db.open(); } catch { out.unreadable.push(e.name); continue; }
        for await (const [, doc] of db.iterator()) {
            out.total += 1;
            const v = doc?._stats?.coreVersion;
            if (!v) continue;
            out.versions.set(v, (out.versions.get(v) ?? 0) + 1);
            if (Number(String(v).split(".")[0]) > CORE_GENERATION) out.newer += 1;
        }
        await db.close();
    }
    return out;
}

const problems = [];
const notes = [];

const compat = manifest.compatibility ?? {};
const min = Number(String(compat.minimum ?? "").split(".")[0]);
const max = Number(String(compat.maximum ?? "").split(".")[0]);
if (min > CORE_GENERATION) {
    problems.push(`manifest requires core ${compat.minimum}, needs lowering to ${CORE_GENERATION}`);
}
if (max && max < CORE_GENERATION) {
    problems.push(`manifest caps core at ${compat.maximum}, needs raising to ${CORE_GENERATION}`);
}

for (const rel of manifest.relationships?.systems ?? []) {
    const rmin = String(rel.compatibility?.minimum ?? "");
    if (rel.id === "pf2e" && Number(rmin.split(".")[0]) > 7) {
        problems.push(`requires pf2e ${rmin}, needs lowering to 7.12.0`);
    }
}

for (const rel of manifest.relationships?.requires ?? []) {
    notes.push(`depends on module ${rel.id}, must be installed separately`);
}

const core = await coreSymbols();
const refs = await scanSources();
const missing = [...refs.keys()].filter(n => !core.has(n)).sort();

const packs = await scanPacks();

console.log(`module   ${manifest.id} ${manifest.version ?? ""}`);
console.log(`title    ${manifest.title ?? ""}`);
console.log("");

if (missing.length) {
    problems.push(`${missing.length} core API references absent from this Foundry build`);
    console.log("core API absent from v13");
    for (const n of missing) {
        for (const where of [...refs.get(n)].slice(0, 3)) console.log(`   ${where}`);
    }
    console.log("");
} else {
    console.log(`core API   all ${refs.size} referenced symbols exist in v13`);
}

if (packs.total) {
    const list = [...packs.versions].map(([v, c]) => `${v} x${c}`).join(", ");
    console.log(`packs      ${packs.total} documents, core versions ${list || "unstamped"}`);
    if (packs.newer) problems.push(`${packs.newer} documents stamped with a core version above ${CORE_GENERATION}`);
    if (packs.unreadable.length) {
        notes.push(`could not read ${packs.unreadable.join(", ")}, stop Foundry and run again`);
    }
} else {
    console.log("packs      none");
}

console.log("");
if (problems.length) {
    console.log("blocking");
    for (const p of problems) console.log(`   ${p}`);
    console.log("");
    console.log(`run  node scripts/port-module.mjs ${DIR}`);
    if (missing.length) console.log("code changes are also required, porting alone will not be enough");
} else {
    console.log("nothing blocking, the module should load on v13 as is");
}
for (const n of notes) console.log(`note   ${n}`);

process.exitCode = missing.length ? 1 : 0;
