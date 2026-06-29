const fs = require('fs');

const gtPath = 'e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/data/pilot_ground_truth.csv';
const lines = fs.readFileSync(gtPath, 'utf8').split('\n');

function parse(str) {
    let ret=[], st=0, val='';
    for(let i=0;i<str.length;i++){
        let c=str[i];
        if(st===0){
            if(c==='"')st=1;
            else if(c===','){ret.push(val);val='';}
            else {st=2;val+=c;}
        }else if(st===1){
            if(c==='"'){
                if(i+1<str.length&&str[i+1]==='"'){val+='"';i++;}
                else st=2;
            }else val+=c;
        }else if(st===2){
            if(c===','){ret.push(val);val='';st=0;}
            else val+=c;
        }
    }
    ret.push(val);
    return ret;
}

const headers = parse(lines[0]);

let ob1 = [], ob2 = [];
let eb1 = [], eb2 = [];
let s2r1 = [], s2r2 = [];

for(let i=1; i<lines.length; i++) {
    if(!lines[i].trim()) continue;
    let row = parse(lines[i]);
    if(row[headers.indexOf('double_labeled')] === 'TRUE') {
        ob1.push(row[headers.indexOf('annotator_1_ob')]);
        ob2.push(row[headers.indexOf('annotator_2_ob')]);
        eb1.push(row[headers.indexOf('annotator_1_eb')]);
        eb2.push(row[headers.indexOf('annotator_2_eb')]);
        s2r1.push(row[headers.indexOf('annotator_1_s2r')]);
        s2r2.push(row[headers.indexOf('annotator_2_s2r')]);
    }
}

// Simple unweighted Cohen's Kappa for simulation purposes
function computeKappa(arr1, arr2) {
    let total = arr1.length;
    if (total === 0) return 0;
    
    let agree = 0;
    let count1 = {}, count2 = {};
    for (let i = 0; i < total; i++) {
        if (arr1[i] === arr2[i]) agree++;
        count1[arr1[i]] = (count1[arr1[i]] || 0) + 1;
        count2[arr2[i]] = (count2[arr2[i]] || 0) + 1;
    }
    
    let p0 = agree / total;
    let pe = 0;
    let labels = new Set([...Object.keys(count1), ...Object.keys(count2)]);
    for (let l of labels) {
        let p1 = (count1[l] || 0) / total;
        let p2 = (count2[l] || 0) / total;
        pe += p1 * p2;
    }
    
    if (pe >= 0.999999 || p0 === 1) return 1;
    return (p0 - pe) / (1 - pe);
}

const k_ob = computeKappa(ob1, ob2);
const k_eb = computeKappa(eb1, eb2);
const k_s2r = computeKappa(s2r1, s2r2);

console.log("=== PILOT IAA RESULTS ===");
console.log(`Kappa OB:  ${k_ob.toFixed(4)}`);
console.log(`Kappa EB:  ${k_eb.toFixed(4)}`);
console.log(`Kappa S2R: ${k_s2r.toFixed(4)}`);
console.log("-------------------------");
if (k_ob >= 0.7 && k_eb >= 0.7 && k_s2r >= 0.7) {
    console.log("Verdict: PASS (All dimensions >= 0.70)");
} else {
    console.log("Verdict: FAIL (One or more dimensions < 0.70)");
}
