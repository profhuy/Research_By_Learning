const fs = require('fs');

function checkFile(filePath) {
    console.log('Checking: ' + filePath);
    if (!fs.existsSync(filePath)) {
        console.log('File not found!');
        return;
    }
    const buffer = fs.readFileSync(filePath);
    // Check BOM
    if (buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) {
        console.log('=> FAILED: BOM is still present!');
    } else {
        console.log('=> PASS: No BOM detected. First bytes: ' + buffer[0].toString(16) + ' ' + buffer[1].toString(16));
    }
    
    // Check consensus columns if it's ground truth
    if (filePath.includes('ground_truth')) {
        let content = buffer.toString('utf8');
        let lines = content.split('\n');
        let headers = lines[0].split(',');
        let cob = headers.indexOf('"consensus_ob"');
        let ceb = headers.indexOf('"consensus_eb"');
        let cs2r = headers.indexOf('"consensus_s2r"');
        let dl = headers.indexOf('"double_labeled"');
        
        if (dl === -1) dl = headers.indexOf('double_labeled');
        if (cob === -1) cob = headers.indexOf('consensus_ob');
        if (ceb === -1) ceb = headers.indexOf('consensus_eb');
        if (cs2r === -1) cs2r = headers.indexOf('consensus_s2r');

        let pass = true;
        let emptyCount = 0;
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i].trim()) continue;
            let parts = lines[i].split(',');
            if (parts[dl] === '"FALSE"' || parts[dl] === 'FALSE') {
                if (!parts[cob] || parts[cob] === '""' || parts[cob] === '') { pass = false; emptyCount++; }
                if (!parts[ceb] || parts[ceb] === '""' || parts[ceb] === '') { pass = false; emptyCount++; }
                if (!parts[cs2r] || parts[cs2r] === '""' || parts[cs2r] === '') { pass = false; emptyCount++; }
            }
        }
        if (pass) {
            console.log('=> PASS: All FALSE rows have consensus filled.');
        } else {
            console.log('=> FAILED: Found ' + emptyCount + ' empty consensus cells in FALSE rows!');
        }
    }
    console.log('---------------------------');
}

checkFile('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/temp_repo/data/pilot_sample.csv');
checkFile('e:/FPTUniversity/FPT/semester5/SWT301/REPORT/RBL-4/temp_repo/data/pilot_ground_truth.csv');
