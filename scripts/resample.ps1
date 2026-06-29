$ErrorActionPreference = "Stop"

$rawPath = "data\raw\all_issues.csv"
$pilotPath = "data\pilot_sample_new.csv"

Write-Host "Reading $rawPath ..."
$allIssues = Import-Csv $rawPath

Write-Host ("Loaded {0} issues." -f $allIssues.Count)

# Use Random seed to shuffle
$random = New-Object System.Random(12345)

# Shuffle all issues
$shuffled = $allIssues | Sort-Object { $random.Next() }

# Take up to 250 for main sample
$sample = $shuffled | Select-Object -First 250

# Shuffle the sample again to pick pilot
$sampleShuffled = $sample | Sort-Object { $random.Next() }

$pilotIndices = New-Object System.Collections.Generic.HashSet[int]
for ($i = 0; $i -lt 30; $i++) {
    [void]$pilotIndices.Add($i)
}

# Add columns selected_for_pilot and notes
$result = @()
for ($i = 0; $i -lt $sampleShuffled.Count; $i++) {
    $item = $sampleShuffled[$i] | Select-Object *, @{Name='selected_for_pilot';Expression={ if ($pilotIndices.Contains($i)) { 'TRUE' } else { 'FALSE' } }}, @{Name='notes';Expression={''}}
    if ($pilotIndices.Contains($i)) {
        $result += $item
    }
}

# Sort result by repo and issue_id
$sortedPilot = $result | Sort-Object repo, @{Expression={[int]$_.issue_id}; Ascending=$true}

$sortedPilot | Export-Csv -Path $pilotPath -NoTypeInformation -Encoding UTF8

Write-Host ("Saved {0} pilot issues to {1}" -f $sortedPilot.Count, $pilotPath)
