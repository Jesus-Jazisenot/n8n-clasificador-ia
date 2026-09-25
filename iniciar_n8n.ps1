# Arranca n8n en Docker (http://localhost:5678) con la llave de Gemini de docucita.
# La llave se pasa como variable de entorno: nunca queda escrita dentro del flujo.
$linea = Select-String -Path "$env:USERPROFILE\docucita\.env" -Pattern '^GEMINI_API_KEY=' | Select-Object -First 1
if (-not $linea) { Write-Error "No encontré GEMINI_API_KEY en docucita\.env"; exit 1 }
$key = $linea.Line.Split('=', 2)[1].Trim().Trim('"')

if (docker ps -a --format '{{.Names}}' | Select-String -Quiet '^n8n$') {
    docker start n8n | Out-Null
} else {
    docker run -d --name n8n -p 5678:5678 `
        -v n8n_data:/home/node/.n8n `
        -e GEMINI_API_KEY=$key `
        -e GEMINI_MODEL=gemini-flash-lite-latest `
        -e N8N_BLOCK_ENV_ACCESS_IN_NODE=false `
        -e GENERIC_TIMEZONE=America/Mazatlan -e TZ=America/Mazatlan `
        docker.n8n.io/n8nio/n8n:latest | Out-Null
}
Write-Host "n8n arrancando en http://localhost:5678 (tarda ~20 s)"
