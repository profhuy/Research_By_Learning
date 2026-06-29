const fs = require('fs');
const path = require('path');

const rawPath = path.join(__dirname, '../data/raw/all_issues.csv');
const newSamplePath = path.join(__dirname, '../data/pilot_sample_new.csv');

// simple random seed generator
function splitmix32(a) {
    return function() {
      a |= 0; a = a + 0x9e3779b9 | 0;
      var t = a ^ a >>> 16; t = Math.imul(t, 0x21f0aaad);
      t = t ^ t >>> 15; t = Math.imul(t, 0x735a2d97);
      return ((t = t ^ t >>> 15) >>> 0) / 4294967296;
    }
}

function parseCsvLine(text) {
    const ret = [];
    let state = 0; 
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

function main() {
    const lines = fs.readFileSync(rawPath, 'utf8').split('\n').filter(l => l.trim().length > 0);
    const headers = parseCsvLine(lines[0]);
    
    let allIssues = [];
    for (let i = 1; i < lines.length; i++) {
        const row = parseCsvLine(lines[i]);
        if (row.length === headers.length) {
            allIssues.push(row);
        }
    }
    
    let seed = 123;
    let rng = splitmix32(seed);
    
    // shuffle and take 250
    for (let i = allIssues.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [allIssues[i], allIssues[j]] = [allIssues[j], allIssues[i]];
    }
    
    let n = Math.min(250, allIssues.length);
    let sample = allIssues.slice(0, n);
    
    // shuffle sample to pick 30
    rng = splitmix32(seed + 1);
    let pilotSize = Math.max(1, Math.floor(n * 0.12)); // 30
    
    for (let i = sample.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [sample[i], sample[j]] = [sample[j], sample[i]];
    }
    
    let pilotIndices = new Set();
    for (let i = 0; i < pilotSize; i++) {
        pilotIndices.add(i);
    }
    
    // add 'selected_for_pilot' and 'notes' columns
    headers.push("selected_for_pilot");
    headers.push("notes");
    
    let pilotIssues = [];
    for (let i = 0; i < sample.length; i++) {
        if (pilotIndices.has(i)) {
            let r = [...sample[i]];
            r.push("TRUE");
            r.push("");
            pilotIssues.push(r);
        }
    }
    
    // Sort by repo and issue_id
    const repoIdx = headers.indexOf('repo');
    const idIdx = headers.indexOf('issue_id');
    
    pilotIssues.sort((a, b) => {
        if (a[repoIdx] !== b[repoIdx]) return a[repoIdx].localeCompare(b[repoIdx]);
        return parseInt(a[idIdx]) - parseInt(b[idIdx]);
    });
    
    let csvData = headers.map(escapeCsv).join(',') + '\n';
    for (let r of pilotIssues) {
        csvData += r.map(escapeCsv).join(',') + '\n';
    }
    
    fs.writeFileSync(newSamplePath, csvData);
    console.log(`Saved new pilot sample: ${newSamplePath} (${pilotIssues.length} rows)`);
}

main();
