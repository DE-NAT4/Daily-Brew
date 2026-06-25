$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$aws_profile = if ($args[0]) { $args[0] } else { "MohammedAalam" }
$project_name = if ($args[1]) { $args[1] } else { "ma-test" }
$deployment_bucket = "$project_name-deployment-bucket"

Push-Location "$PSScriptRoot\..\cloudformation"

Write-Output ""
Write-Output "Deploying deployment bucket stack..."
Write-Output ""
aws cloudformation deploy `
    --stack-name "$project_name-deployment-stack" `
    --template-file deployment-bucket-stack.yml `
    --region eu-west-1 `
    --capabilities CAPABILITY_IAM `
    --profile $aws_profile `
    --parameter-overrides `
      ProjectName=$project_name

Write-Output ""
Write-Output "Packaging ETL stack..."
Write-Output ""
aws cloudformation package `
    --template-file etl-stack.yml `
    --s3-bucket $deployment_bucket `
    --output-template-file etl-stack-packaged.yml `
    --profile $aws_profile

Write-Output ""
Write-Output "Deploying ETL stack..."
Write-Output ""
aws cloudformation deploy `
    --stack-name "$project_name-etl-stack" `
    --template-file etl-stack-packaged.yml `
    --region eu-west-1 `
    --capabilities CAPABILITY_IAM `
    --profile $aws_profile `
    --parameter-overrides `
      ProjectName=$project_name

Pop-Location

Write-Output ""
Write-Output "Deployment complete."
Write-Output ""
