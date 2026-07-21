const fs = require("fs");

// ---------- CSV Parser ----------
function parseCSV(path) {
    const text = fs.readFileSync(path, "utf8");

    const rows = [];
    let row = [];
    let value = "";
    let insideQuote = false;

    for (let i = 0; i < text.length; i++) {
        const c = text[i];

        if (c === '"') {
            if (insideQuote && text[i + 1] === '"') {
                value += '"';
                i++;
            } else {
                insideQuote = !insideQuote;
            }
        } else if (c === "," && !insideQuote) {
            row.push(value);
            value = "";
        } else if ((c === "\n" || c === "\r") && !insideQuote) {
            if (value !== "" || row.length > 0) {
                row.push(value);
                rows.push(row);
                row = [];
                value = "";
            }
        } else {
            value += c;
        }
    }

    if (value.length || row.length) {
        row.push(value);
        rows.push(row);
    }

    const headers = rows[0];
    const out = [];

    for (let i = 1; i < rows.length; i++) {
        let obj = {};
        headers.forEach((h, j) => obj[h] = rows[i][j]);
        out.push(obj);
    }

    return out;
}

// ---------- Cohen Kappa ----------
function kappa(gt, pred) {

    const labels = [...new Set([...gt, ...pred])];

    const n = gt.length;

    let agree = 0;

    gt.forEach((v, i) => {
        if (v === pred[i]) agree++;
    });

    const p0 = agree / n;

    let pe = 0;

    labels.forEach(label => {

        const pg = gt.filter(x => x === label).length / n;

        const pp = pred.filter(x => x === label).length / n;

        pe += pg * pp;

    });

    if (1 - pe === 0) {

        return null;

    }

    return (p0 - pe) / (1 - pe);

}

// ---------- Accuracy ----------
function accuracy(gt, pred){

    let correct=0;

    gt.forEach((v,i)=>{

        if(v===pred[i]) correct++;

    });

    return correct/gt.length;

}

// ---------- Confusion Matrix ----------
function confusion(gt,pred){

    const labels=[...new Set([...gt,...pred])];

    let matrix={};

    labels.forEach(r=>{

        matrix[r]={};

        labels.forEach(c=>matrix[r][c]=0);

    });

    gt.forEach((v,i)=>{

        matrix[v][pred[i]]++;

    });

    return matrix;

}

// ---------- Load ----------
const ground=parseCSV("data/pilot_ground_truth.csv");

const model=parseCSV("results/pilot_llm_output.csv");

// ---------- Join ----------
let map={};

model.forEach(r=>{

    map[r.issue_id]=r;

});

const dimensions=[

    ["OB","consensus_ob","llm_ob_label"],

    ["EB","consensus_eb","llm_eb_label"],

    ["S2R","consensus_s2r","llm_s2r_label"]

];

let output="Dimension,Accuracy,Kappa\n";

dimensions.forEach(d=>{

    let gt=[];

    let pred=[];

    ground.forEach(r=>{

        if(map[r.issue_id]){

            gt.push(r[d[1]]);

            pred.push(map[r.issue_id][d[2]]);

        }

    });

    const acc=accuracy(gt,pred);

    const kap=kappa(gt,pred);

    console.log("\n====================");

    console.log(d[0]);

    console.log("Accuracy:",acc.toFixed(4));

    console.log("Kappa:",kap===null?"UNDEFINED":kap.toFixed(4));

    console.table(confusion(gt,pred));

    output+=`${d[0]},${acc.toFixed(4)},${kap===null?"UNDEFINED":kap.toFixed(4)}\n`;

});

fs.writeFileSync("results/summary.csv",output);

console.log("\nsummary.csv generated.");
