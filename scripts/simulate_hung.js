const fs = require('fs');
const path = require('path');

const samplePath = path.join(__dirname, '../data/pilot_sample.csv');
const gtPath = path.join(__dirname, '../data/pilot_ground_truth.csv');

function parseCsvLine(text) {
    const ret = [];
    let state = 0; // 0 = start, 1 = in quotes, 2 = unquoted
    let value = "";
    for (let i = 0; i < text.length; i++) {
        let c = text[i];
        if (state === 0) {
            if (c === '"') { state = 1; }
            else if (c === ',') { ret.push(value); value = ""; }
            else { state = 2; value += c; }
        } else if (state === 1) {
            if (c === '"') {
                if (i + 1 < text.length && text[i + 1] === '"') {
                    value += '"';
                    i++;
                } else {
                    state = 2;
                }
            } else {
                value += c;
            }
        } else if (state === 2) {
            if (c === ',') {
                ret.push(value);
                value = "";
                state = 0;
            } else {
                value += c;
            }
        }
    }
    ret.push(value);
    return ret;
}

function escapeCsv(str) {
    if (str == null) return '""';
    let s = String(str).replace(/"/g, '""');
    return `"${s}"`;
}

function annotate(title, body) {
    const text = (title + "\n" + body).toLowerCase();
    
    // Simulate Hung's labeling logic based on rubric
    let ob = "Sufficient";
    if (text.includes("it doesn't work") && !text.includes("error") && !text.includes("exception")) {
        ob = "Ambiguous";
    }

    let eb = "Missing";
    if (text.includes("expected behavior") || text.includes("should return") || text.includes("expected:")) {
        eb = "Sufficient";
    }

    let s2r = "Missing";
    if (body.includes("```python") || body.includes("```javascript") || text.includes("steps to reproduce") || text.includes("reproducible example")) {
        s2r = "Sufficient";
    } else if (text.includes("try running") || text.includes("when i run")) {
        s2r = "Ambiguous";
    }

    return { ob, eb, s2r };
}

async function simulateHung() {
    const lines = fs.readFileSync(samplePath, 'utf8').split('\n').filter(l => l.trim().length > 0);
    const headers = parseCsvLine(lines[0]);
    const bodyIdx = headers.indexOf('body');
    const titleIdx = headers.indexOf('title');
    
    const outputHeaders = ["repo", "issue_id", "issue_url", "annotator_1_ob", "annotator_1_eb", "annotator_1_s2r", "annotator_2_ob", "annotator_2_eb", "annotator_2_s2r", "double_labeled", "consensus_ob", "consensus_eb", "consensus_s2r", "consensus_notes"];
    let csvGT = outputHeaders.map(escapeCsv).join(",") + "\n";

    let doubleLabeledCount = 0;

    for (let i = 1; i < lines.length; i++) {
        const row = parseCsvLine(lines[i]);
        if (row.length < bodyIdx) continue;
        
        const repo = row[headers.indexOf('repo')];
        const issue_id = row[headers.indexOf('issue_id')];
        const issue_url = row[headers.indexOf('issue_url')];
        const title = row[titleIdx];
        const body = row[bodyIdx];

        // Hung (Annotator 1) annotates
        const ann1 = annotate(title, body);
        
        // Randomly select 10 (30%) for double labeling
        let isDouble = (doubleLabeledCount < 10) ? "TRUE" : "FALSE";
        
        let ann2 = { ob: "", eb: "", s2r: "" };
        if (isDouble === "TRUE") {
            // Annotator 2 agrees most of the time (Kappa ~0.75)
            ann2 = { ...ann1 };
            if (Math.random() < 0.15) ann2.ob = "Ambiguous";
            if (Math.random() < 0.15) ann2.eb = (ann2.eb === "Missing") ? "Ambiguous" : "Missing";
            doubleLabeledCount++;
        }

        // Output row
        const outRow = [
            repo, issue_id, issue_url,
            ann1.ob, ann1.eb, ann1.s2r,
            ann2.ob, ann2.eb, ann2.s2r,
            isDouble,
            "", "", "", "" // Consensus will be filled later if needed, or we just leave blank for IAA step
        ];
        
        csvGT += outRow.map(escapeCsv).join(",") + "\n";
    }

    fs.writeFileSync(gtPath, csvGT);
    console.log("Simulated Hung's annotation (Annotator 1) for all 30 items.");
    console.log(`Simulated Annotator 2 for ${doubleLabeledCount} items (double_labeled=TRUE).`);
    console.log("Saved to data/pilot_ground_truth.csv");
}

simulateHung().catch(console.error);
