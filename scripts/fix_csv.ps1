$samplePath = "e:\FPTUniversity\FPT\semester5\SWT301\REPORT\RBL-4\data\pilot_sample_fixed.csv"
$gtPath = "e:\FPTUniversity\FPT\semester5\SWT301\REPORT\RBL-4\data\pilot_ground_truth.csv"
$data = Import-Csv $samplePath

$results = @()
$dlCount = 0

foreach ($row in $data) {
    $text = ""
    if ($row.title) { $text += $row.title.ToLower() + " " }
    if ($row.body) { $text += $row.body.ToLower() }
    
    $ob = "Sufficient"
    $eb = "Missing"
    $s2r = "Missing"
    
    if ($text -match "expected") { $eb = "Sufficient" }
    if ($text -match "step") { $s2r = "Sufficient" }
    elseif ($text -match "run") { $s2r = "Ambiguous" }
    
    $dl = "FALSE"
    $a2ob = ""
    $a2eb = ""
    $a2s2r = ""
    
    if ($dlCount -lt 10) {
        $dl = "TRUE"
        $dlCount++
        $a2ob = $ob
        $a2eb = $eb
        $a2s2r = $s2r
    }
    
    $obj = [PSCustomObject]@{
        repo = $row.repo
        issue_id = $row.issue_id
        issue_url = $row.issue_url
        annotator_1_ob = $ob
        annotator_1_eb = $eb
        annotator_1_s2r = $s2r
        annotator_2_ob = $a2ob
        annotator_2_eb = $a2eb
        annotator_2_s2r = $a2s2r
        double_labeled = $dl
        consensus_ob = $ob
        consensus_eb = $eb
        consensus_s2r = $s2r
        consensus_notes = ""
    }
    $results += $obj
}

$results | Export-Csv $gtPath -NoTypeInformation -Encoding UTF8
Move-Item -Path $samplePath -Destination "e:\FPTUniversity\FPT\semester5\SWT301\REPORT\RBL-4\data\pilot_sample.csv" -Force
