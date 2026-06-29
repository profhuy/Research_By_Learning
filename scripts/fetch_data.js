const https = require('https');
const fs = require('fs');
const path = require('path');

const REPOS = ['pandas-dev/pandas', 'scikit-learn/scikit-learn', 'microsoft/vscode'];
const SEED = 42;
const TARGET_N = 250;
const PILOT_PCT = 0.12;
const MIN_BODY_WORDS = 50;
const MAX_PAGES = 5; // To avoid hitting rate limits without token

const dataDir = path.join(__dirname, '../data');
const rawDir = path.join(dataDir, 'raw');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir);
if (!fs.existsSync(rawDir)) fs.mkdirSync(rawDir);

// Simple pseudo-random generator
function mulberry32(a) {
    return function() {
        var t = a += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
}

function countWords(str) {
    if (!str) return 0;
    return str.split(/\s+/).filter(w => w.length > 0).length;
}

function isLikelyEnglish(str) {
    if (!str) return false;
    let asciiCount = 0;
    for (let i = 0; i < str.length; i++) {
        if (str.charCodeAt(i) < 128) asciiCount++;
    }
    return (asciiCount / str.length) > 0.85;
}

function fetchPage(repo, page) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.github.com',
            path: `/repos/${repo}/issues?state=all&labels=bug&per_page=100&page=${page}&sort=created&direction=desc`,
            headers: {
                'User-Agent': 'NodeJS-RBL4-Script',
                'Accept': 'application/vnd.github.v3+json'
            }
        };

        const req = https.get(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
                } else if (res.statusCode === 403) {
                    resolve("RATE_LIMIT");
                } else {
                    reject(new Error(`Status ${res.statusCode}`));
                }
            });
        });
        req.on('error', reject);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeCsv(str) {
    if (str == null) return '""';
    let s = String(str).replace(/"/g, '""');
    return `"${s}"`;
}

async function main() {
    console.log("=== RBL-4 GitHub Issue Fetcher (Node.js) ===");
    let allIssues = [];

    for (const repo of REPOS) {
        console.log(`\nFetching ${repo}...`);
        for (let page = 1; page <= MAX_PAGES; page++) {
            console.log(`  Page ${page}...`);
            const data = await fetchPage(repo, page);
            if (data === "RATE_LIMIT") {
                console.log("  Rate limited! Stopping fetch for this repo.");
                break;
            }
            if (data.length === 0) break;

            let valid = 0;
            for (const issue of data) {
                if (issue.pull_request) continue;
                if (!issue.body) continue;
                if (countWords(issue.body) < MIN_BODY_WORDS) continue;
                if (!isLikelyEnglish(issue.body)) continue;

                allIssues.push({
                    repo: repo.split('/')[1],
                    issue_id: issue.number,
                    issue_url: issue.html_url,
                    title: issue.title,
                    body: issue.body,
                    created_at: issue.created_at,
                    state: issue.state,
                    labels: issue.labels.map(l => l.name).join(',')
                });
                valid++;
            }
            console.log(`    Got ${valid} valid issues.`);
            await sleep(1500); // Wait to respect API limits
        }
    }

    console.log(`\nTotal valid issues fetched: ${allIssues.length}`);

    // Dedup
    const seen = new Set();
    const unique = [];
    for (const issue of allIssues) {
        const key = issue.repo + issue.issue_id;
        if (!seen.has(key)) {
            seen.add(key);
            unique.push(issue);
        }
    }
    allIssues = unique;
    console.log(`After dedup: ${allIssues.length} unique issues.`);

    // Random sample full dataset N
    const rand = mulberry32(SEED);
    allIssues.sort((a, b) => {
        const r1 = rand();
        const r2 = rand();
        return r1 - r2;
    });

    const finalSample = allIssues.slice(0, TARGET_N);
    console.log(`Sampled N=${finalSample.length} for full dataset.`);

    // Write all_issues.csv
    const headers = ["repo", "issue_id", "issue_url", "title", "body", "created_at", "state", "labels"];
    let csvAll = headers.map(escapeCsv).join(",") + "\n";
    for (const issue of finalSample) {
        csvAll += headers.map(h => escapeCsv(issue[h])).join(",") + "\n";
    }
    fs.writeFileSync(path.join(rawDir, 'all_issues.csv'), csvAll);

    // Random sample pilot
    const pilotSize = Math.max(1, Math.floor(finalSample.length * PILOT_PCT));
    console.log(`Selecting pilot size: ${pilotSize}`);

    const rand2 = mulberry32(SEED);
    // Shuffle again for pilot
    const shuffledForPilot = [...finalSample].sort(() => rand2() - 0.5);
    const pilotIds = new Set(shuffledForPilot.slice(0, pilotSize).map(i => i.repo + i.issue_id));

    let pilotOutput = [];
    const pilotHeaders = [...headers, "selected_for_pilot", "notes", "annotator_1_ob", "annotator_1_eb", "annotator_1_s2r", "annotator_2_ob", "annotator_2_eb", "annotator_2_s2r", "double_labeled", "consensus_ob", "consensus_eb", "consensus_s2r", "consensus_notes"];

    for (const issue of finalSample) {
        if (pilotIds.has(issue.repo + issue.issue_id)) {
            const out = { ...issue };
            out.selected_for_pilot = "TRUE";
            out.notes = "";
            out.annotator_1_ob = "";
            out.annotator_1_eb = "";
            out.annotator_1_s2r = "";
            out.annotator_2_ob = "";
            out.annotator_2_eb = "";
            out.annotator_2_s2r = "";
            out.double_labeled = ""; // Hùng sẽ tự điền TRUE cho 30% mẫu
            out.consensus_ob = "";
            out.consensus_eb = "";
            out.consensus_s2r = "";
            out.consensus_notes = "";
            pilotOutput.push(out);
        }
    }

    // Write pilot_sample.csv
    // Sort pilot output by repo and ID for easier reading
    pilotOutput.sort((a, b) => a.repo.localeCompare(b.repo) || a.issue_id - b.issue_id);

    let csvPilot = pilotHeaders.map(escapeCsv).join(",") + "\n";
    for (const issue of pilotOutput) {
        csvPilot += pilotHeaders.map(h => escapeCsv(issue[h] || "")).join(",") + "\n";
    }
    fs.writeFileSync(path.join(dataDir, 'pilot_sample.csv'), csvPilot);
    
    // Create an empty template for pilot_ground_truth.csv as well
    let csvGT = pilotHeaders.slice(0, 3).concat(pilotHeaders.slice(9)).map(escapeCsv).join(",") + "\n";
    // Usually pilot_ground_truth is just a copy of pilot_sample without body text to be lightweight
    let gtHeaders = ["repo", "issue_id", "issue_url", "annotator_1_ob", "annotator_1_eb", "annotator_1_s2r", "annotator_2_ob", "annotator_2_eb", "annotator_2_s2r", "double_labeled", "consensus_ob", "consensus_eb", "consensus_s2r", "consensus_notes"];
    let csvGroundTruth = gtHeaders.map(escapeCsv).join(",") + "\n";
    for (const issue of pilotOutput) {
        csvGroundTruth += gtHeaders.map(h => escapeCsv(issue[h] || "")).join(",") + "\n";
    }
    fs.writeFileSync(path.join(dataDir, 'pilot_ground_truth.csv'), csvGroundTruth);

    console.log("Done! Saved to data/pilot_sample.csv and data/pilot_ground_truth.csv");
}

main().catch(console.error);
