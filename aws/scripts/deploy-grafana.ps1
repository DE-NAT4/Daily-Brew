$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$aws_profile = if ($args[0]) { $args[0] } else { "MohammedAalam" }
$project_name = if ($args[1]) { $args[1] } else { "daily-brew-group" }
$ec2_ingress_ip = if ($args[2]) { $args[2] } else { (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim() }
$grafana_password_file = "$PSScriptRoot\..\grafana\.grafana-admin-password"

if (-not (Test-Path $grafana_password_file)) {
    $bytes = New-Object byte[] 24
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $grafana_password = [Convert]::ToBase64String($bytes).Replace("+", "A").Replace("/", "B").Replace("=", "C")
    Set-Content -Path $grafana_password_file -Value $grafana_password
}
else {
    $grafana_password = Get-Content -Path $grafana_password_file -Raw
    $grafana_password = $grafana_password.Trim()
}

Push-Location "$PSScriptRoot\..\cloudformation"

Write-Output ""
Write-Output "Deploying Grafana stack..."
Write-Output "Allowed IP: $ec2_ingress_ip"
Write-Output ""

aws cloudformation deploy `
    --stack-name "$project_name-grafana-stack" `
    --template-file grafana-stack.yml `
    --region eu-west-1 `
    --capabilities CAPABILITY_IAM `
    --profile $aws_profile `
    --parameter-overrides `
      ProjectName=$project_name `
      EC2InstanceIngressIp=$ec2_ingress_ip `
      GrafanaAdminPassword=$grafana_password

Pop-Location

Write-Output ""
Write-Output "Grafana deployment complete."
Write-Output ""
