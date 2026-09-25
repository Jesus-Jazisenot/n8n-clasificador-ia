# Manda 3 mensajes de ejemplo al flujo y enseña qué contestó.
# Uso: .\probar.ps1            (flujo activo, URL de producción)
#      .\probar.ps1 -Prueba    (con "Execute workflow" abierto en el editor)
param([switch]$Prueba)
$ruta = if ($Prueba) { 'webhook-test' } else { 'webhook' }
$url = "http://localhost:5678/$ruta/mensaje-cliente"

$mensajes = @(
    @{ nombre = 'Ana';    mensaje = 'Hola, cuánto cuesta instalar un minisplit de 1 tonelada en mi recámara?' },
    @{ nombre = 'Carlos'; mensaje = 'El clima que me instalaron la semana pasada está echando chispas y huele a quemado!!' },
    @{ nombre = 'Lupita'; mensaje = 'Quiero agendar una limpieza para mis 2 minisplits antes de que empiece el calor' }
)
foreach ($m in $mensajes) {
    $body = $m | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri $url -Method Post -Body ([Text.Encoding]::UTF8.GetBytes($body)) -ContentType 'application/json; charset=utf-8'
    Write-Host "`n>> $($m.nombre): $($m.mensaje)" -ForegroundColor Cyan
    Write-Host "   categoría: $($r.categoria) | urgente: $($r.urgente) | acción: $($r.accion)"
    Write-Host "   respuesta: $($r.respuesta)" -ForegroundColor Green
    Start-Sleep 5
}
