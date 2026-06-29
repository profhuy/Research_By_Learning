$ErrorActionPreference = "Stop"

$rawPath = "data\raw\all_issues.csv"
$oldPilotPath = "data\pilot_sample.csv"
$newPilotPath = "data\pilot_sample_other_30.csv"

Write-Host "Reading $oldPilotPath ..."
$oldPilot = Import-Csv $oldPilotPath
$oldPilotIds = New-Object System.Collections.Generic.HashSet[string]
foreach ($row in $oldPilot) {
    if ($row.selected_for_pilot -eq 'TRUE') {
        [void]$oldPilotIds.Add($row.issue_url)
    }
}
Write-Host ("Found {0} issues in previous pilot." -f $oldPilotIds.Count)

Write-Host "Reading $rawPath ..."
$allIssues = Import-Csv $rawPath
Write-Host ("Loaded {0} total issues." -f $allIssues.Count)

$remainingIssues = @()
foreach ($row in $allIssues) {
    if (-not $oldPilotIds.Contains($row.issue_url)) {
        $remainingIssues += $row
    }
}
Write-Host ("Remaining issues to pick from: {0}" -f $remainingIssues.Count)

# Shuffle remaining
$random = New-Object System.Random(9999)
$shuffled = $remainingIssues | Sort-Object { $random.Next() }

# Take 30
$newPilotItems = $shuffled | Select-Object -First 30

$result = @()
foreach ($item in $newPilotItems) {
    $newItem = $item | Select-Object *, @{Name='selected_for_pilot';Expression={'TRUE'}}, @{Name='notes';Expression={''}}
    $result += $newItem
}

# Sort result
$sortedPilot = $result | Sort-Object repo, @{Expression={[int]$_.issue_id}; Ascending=$true}

$sortedPilot | Export-Csv -Path $newPilotPath -NoTypeInformation -Encoding UTF8

Write-Host ("Saved {0} NEW pilot issues to {1}" -f $sortedPilot.Count, $newPilotPath)
