$base = $PSScriptRoot

$backend = "sqlite:///$base/mlflow.db"
$artifacts_path = Join-Path $base "mlartifacts"
$artifacts_uri = "file:///" + ($artifacts_path -replace "\\","/")


mlflow server --backend-store-uri $backend --default-artifact-root $artifacts_uri