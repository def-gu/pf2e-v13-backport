import { createRequire } from "node:module";
const FOUNDRY_APP = process.env.FOUNDRY_APP ?? "/home/gm/fvtt-app-v13";
const require = createRequire(`${FOUNDRY_APP}/package.json`);
const { ClassicLevel } = require("classic-level");
const D = "merged-out/packs-compiled";
for (const [pack, parent, emb] of [["journals","!journal!","!journal.pages!"],
                                   ["pathfinder-monster-core","!actors!","!actors.items!"],
                                   ["criticaldeck","!journal!","!journal.pages!"]]) {
    const db = new ClassicLevel(`${D}/${pack}`, { valueEncoding: "json" });
    await db.open();
    let p = 0, e = 0, sample = null, orphan = 0;
    const ids = new Set();
    for await (const [k, v] of db.iterator()) {
        if (k.startsWith(parent)) { p++; ids.add(k.slice(parent.length)); if (!sample) sample = v; }
        else if (k.startsWith(emb)) e++;
    }
    for await (const [k] of db.iterator()) {
        if (!k.startsWith(emb)) continue;
        const pid = k.slice(emb.length).split(".")[0];
        if (!ids.has(pid)) orphan++;
    }
    console.log(`${pack}: ${p} parents, ${e} embedded, orphans=${orphan}`);
    console.log(`   sample "${sample?.name}" children=${(sample?.pages ?? sample?.items)?.length} _stats.coreVersion=${sample?._stats?.coreVersion}`);
    await db.close();
}
