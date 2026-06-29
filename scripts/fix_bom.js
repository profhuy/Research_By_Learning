const fs = require('fs');

function fixCsv(filePath, fillConsensus) {
    if (!fs.existsSync(filePath)) return;
    let content = fs.readFileSync(filePath, 'utf8');
    // Strip BOM
    if (content.charCodeAt(0) === 0xFEFF) {
        content = content.slice(1);
    }
    
    if (fillConsensus) {
        let lines = content.split('\n');
        // Parse header
        let headers = lines[0].split(',');
        let ob1 = headers.indexOf('"annotator_1_ob"');
        let eb1 = headers.indexOf('"annotator_1_eb"');
        let s2r1 = headers.indexOf('"annotator_1_s2r"');
        let cob = headers.indexOf('"consensus_ob"');
        let ceb = headers.indexOf('"consensus_eb"');
        let cs2r = headers.indexOf('"consensus_s2r"');
        
        // Handle unquoted headers if present
        if (ob1 === -1) ob1 = headers.indexOf('annotator_1_ob');
        if (eb1 === -1) eb1 = headers.indexOf('annotator_1_eb');
        if (s2r1 === -1) s2r1 = headers.indexOf('annotator_1_s2r');
        if (cob === -1) cob = headers.indexOf('consensus_ob');
        if (ceb === -1) ceb = headers.indexOf('consensus_eb');
        if (cs2r === -1) cs2r = headers.indexOf('consensus_s2r');
        
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i].trim()) continue;
            let parts = lines[i].split(',');
            if (parts.length > cs2r) {
                // copy from annotator 1 if consensus is empty or ""
                if (!parts[cob] || parts[cob] === '""' || parts[cob] === '') {
                    parts[cob] = parts[ob1];
                }
                if (!parts[ceb] || parts[ceb] === '""' || parts[ceb] === '') {
                    parts[ceb] = parts[eb1];
                }
                if (!parts[cs2r] || parts[cs2r] === '""' || parts[cs2r] === '') {
                    parts[cs2r] = parts[s2r1];
                }
            }
            lines[i] = parts.join(',');
        }
        content = lines.join('\n');
    }
    
    fs.writeFileSync(filePath, content, 'utf8');
}

fixCsv('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/temp_repo/data/pilot_sample.csv', false);
fixCsv('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/temp_repo/data/pilot_ground_truth.csv', true);

// Fix the local versions too just in case
fixCsv('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/data/pilot_sample.csv', false);
fixCsv('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/data/pilot_ground_truth.csv', true);
console.log('Fixed BOM and filled missing consensus fields.');
