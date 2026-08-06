param(
    [string]$Model = "gemini-3.6-flash",
    [ValidateSet("free_safe", "parallel")]
    [string]$ExecutionProfile = "free_safe",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$secureKey = $null
$bstr = [IntPtr]::Zero
$python = if (Test-Path ".\.venv\Scripts\python.exe") {
    ".\.venv\Scripts\python.exe"
}
else {
    "python"
}

try {
    Write-Host "ORPHEUS Ω · prueba local segura con Gemini" -ForegroundColor Cyan
    Write-Host "La clave no se guardará en archivos ni se mostrará en pantalla." -ForegroundColor DarkGray
    Write-Host "Perfil recomendado: free_safe (todos los agentes, sin ráfagas paralelas)." -ForegroundColor DarkGray

    $secureKey = Read-Host "Pega tu Gemini API key" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)

    if ([string]::IsNullOrWhiteSpace($plainKey)) {
        throw "No se recibió una API key."
    }

    # Variables de proceso: solo existen en esta terminal y en el servidor hijo.
    $env:GEMINI_API_KEY = $plainKey
    $env:ORPHEUS_RUNTIME_MODE = "local"
    $env:ORPHEUS_LLM_BACKEND = "gemini_api"
    $env:ORPHEUS_MODEL = $Model
    $env:ORPHEUS_EXECUTION_PROFILE = $ExecutionProfile

    # Elimina la copia administrada tan pronto como la variable de entorno queda establecida.
    $plainKey = $null

    Write-Host ""
    Write-Host "Backend: gemini_api" -ForegroundColor Green
    Write-Host "Modelo:  $Model" -ForegroundColor Green
    Write-Host "Perfil:  $ExecutionProfile" -ForegroundColor Green
    if ($ExecutionProfile -eq "free_safe") {
        Write-Host "Agentes: 18 habilitados; escuadrones ejecutados por turnos." -ForegroundColor Green
    }
    Write-Host "Python:  $python" -ForegroundColor Green
    Write-Host "Abrir:   http://127.0.0.1:$Port/" -ForegroundColor Green
    Write-Host "Detén el servidor con Ctrl+C; la clave se eliminará de esta sesión." -ForegroundColor Yellow
    Write-Host ""

    & $python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
}
finally {
    Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:GOOGLE_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_RUNTIME_MODE -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_LLM_BACKEND -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_MODEL -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_EXECUTION_PROFILE -ErrorAction SilentlyContinue

    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ($null -ne $secureKey) {
        $secureKey.Dispose()
    }

    Write-Host "Variables temporales eliminadas." -ForegroundColor DarkGray
}
