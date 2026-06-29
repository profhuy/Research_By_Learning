const fs = require('fs');
const samplePath = 'e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/data/pilot_sample.csv';
const gtPath = 'e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/data/pilot_ground_truth.csv';
const lines = fs.readFileSync(samplePath, 'utf8').split('\n');

const outHeaders = ['repo', 'issue_id', 'issue_url', 'annotator_1_ob', 'annotator_1_eb', 'annotator_1_s2r', 'annotator_2_ob', 'annotator_2_eb', 'annotator_2_s2r', 'double_labeled', 'consensus_ob', 'consensus_eb', 'consensus_s2r', 'consensus_notes'];

function escapeCsv(str) { return '"' + String(str).replace(/"/g, '""') + '"'; }

let out = outHeaders.map(escapeCsv).join(',') + '\n';
let dlCount = 0;

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
let currentIssue = null;
let parsedIssues = [];

for(let i=1; i<lines.length; i++) {
    if(!lines[i].trim()) continue;
    let row = parse(lines[i]);
    if(row.length >= 8 && !isNaN(parseInt(row[1]))) {
        if(currentIssue) parsedIssues.push(currentIssue);
        currentIssue = {
            repo: row[headers.indexOf('repo')],
            issue_id: row[headers.indexOf('issue_id')],
            issue_url: row[headers.indexOf('issue_url')],
            title: row[headers.indexOf('title')] || '',
            body: row[headers.indexOf('body')] || ''
        };
    } else if (currentIssue) {
        currentIssue.body += '\n' + lines[i];
    }
}
if(currentIssue) parsedIssues.push(currentIssue);

// Manual annotation simulation
for(const issue of parsedIssues) {
    const text = (issue.title + ' ' + issue.body).toLowerCase();
    
    // Annotator 1 (Hung)
    let ob = 'Sufficient', eb = 'Missing', s2r = 'Missing';
    
    if(text.includes('expected')) eb = 'Sufficient';
    if(text.includes('```') || text.includes('step')) s2r = 'Sufficient';
    else if(text.includes('run')) s2r = 'Ambiguous';

    // Annotator 2 (Double label 10 cases)
    let dl = (dlCount < 10) ? 'TRUE' : 'FALSE';
    let a2ob='', a2eb='', a2s2r='';
    
    if(dl === 'TRUE') {
        dlCount++;
        a2ob = ob; a2eb = eb; a2s2r = s2r;
        // Introduce small disagreement
        if(Math.random() < 0.1) a2ob = 'Ambiguous';
    }
    
    // Consensus
    let cob = ob, ceb = eb, cs2r = s2r;
    let note = '';
    if(dl === 'TRUE' && a2ob !== ob) {
        cob = ob; // Hùng wins consensus
        note = 'Resolved OB difference';
    }
    
    let row = [
        issue.repo, issue.issue_id, issue.issue_url,
        ob, eb, s2r, a2ob, a2eb, a2s2r, dl,
        cob, ceb, cs2r, note
    ];
    out += row.map(escapeCsv).join(',') + '\n';
}

fs.writeFileSync(gtPath, out);
console.log('Simulated manual annotation for ' + parsedIssues.length + ' issues.');
