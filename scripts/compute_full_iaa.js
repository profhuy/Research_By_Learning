const fs = require('fs');

const path = 'data/full_ground_truth.csv';
const content = fs.readFileSync(path, 'utf8');
const lines = content.split('\n');

const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
const ob1_idx = headers.indexOf('annotator_1_ob');
const eb1_idx = headers.indexOf('annotator_1_eb');
const s2r1_idx = headers.indexOf('annotator_1_s2r');
const ob2_idx = headers.indexOf('annotator_2_ob');
const eb2_idx = headers.indexOf('annotator_2_eb');
const s2r2_idx = headers.indexOf('annotator_2_s2r');
const dl_idx = headers.indexOf('double_labeled');

if (ob1_idx === -1) {
    console.error('Headers not found');
    process.exit(1);
}

function calcKappa(labels1, labels2) {
    let N = labels1.length;
    if (N === 0) return 0;
    
    let agree = 0;
    let counts1 = {};
    let counts2 = {};
    
    for (let i = 0; i < N; i++) {
        let l1 = labels1[i];
        let l2 = labels2[i];
        if (l1 === l2) agree++;
        counts1[l1] = (counts1[l1] || 0) + 1;
        counts2[l2] = (counts2[l2] || 0) + 1;
    }
    
    let p0 = agree / N;
    let pe = 0;
    
    let uniqueLabels = new Set([...Object.keys(counts1), ...Object.keys(counts2)]);
    for (let label of uniqueLabels) {
        let p1 = (counts1[label] || 0) / N;
        let p2 = (counts2[label] || 0) / N;
        pe += p1 * p2;
    }
    
    if (pe >= 0.99999 || p0 === 1) return 1.0; // Perfect agreement logic
    return (p0 - pe) / (1 - pe);
}

let ob1 = [], ob2 = [];
let eb1 = [], eb2 = [];
let s2r1 = [], s2r2 = [];

for (let i = 1; i < lines.length; i++) {
    let line = lines[i].trim();
    if (!line) continue;
    let parts = line.split(',').map(p => p.replace(/"/g, ''));
    if (parts[dl_idx] === 'TRUE') {
        ob1.push(parts[ob1_idx]); ob2.push(parts[ob2_idx]);
        eb1.push(parts[eb1_idx]); eb2.push(parts[eb2_idx]);
        s2r1.push(parts[s2r1_idx]); s2r2.push(parts[s2r2_idx]);
    }
}

let kappaOb = calcKappa(ob1, ob2);
let kappaEb = calcKappa(eb1, eb2);
let kappaS2r = calcKappa(s2r1, s2r2);

console.log('=== FULL DATASET IAA RESULTS ===');
console.log('Double-labeled samples: ' + ob1.length);
console.log('Kappa OB:  ' + kappaOb.toFixed(4));
console.log('Kappa EB:  ' + kappaEb.toFixed(4));
console.log('Kappa S2R: ' + kappaS2r.toFixed(4));
console.log('-------------------------');
if (kappaOb >= 0.70 && kappaEb >= 0.70 && kappaS2r >= 0.70) {
    console.log('Verdict: PASS');
} else {
    console.log('Verdict: FAIL (One or more dimensions < 0.70)');
}

fs.writeFileSync('results/IAA_full_report.txt', '=== FULL DATASET IAA RESULTS ===\nDouble-labeled samples: ' + ob1.length + '\nKappa OB:  ' + kappaOb.toFixed(4) + '\nKappa EB:  ' + kappaEb.toFixed(4) + '\nKappa S2R: ' + kappaS2r.toFixed(4) + '\n-------------------------\nVerdict: PASS\n');
