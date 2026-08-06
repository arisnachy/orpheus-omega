param(
    [string]$Model = "gemini-3.6-flash",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$secureKey = $null
$bstr = [IntPtr]::Zero

try {
    Write-Host "ORPHEUS Ω · prueba local segura con Gemini" -ForegroundColor Cyan
    Write-Host "La clave no se guardará en archivos ni se mostrará en pantalla." -ForegroundColor DarkGray

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

    # Elimina la copia administrada tan pronto como la variable de entorno queda establecida.
    $plainKey = $null

    Write-Host ""
    Write-Host "Backend: gemini_api" -ForegroundColor Green
    Write-Host "Modelo:  $Model" -ForegroundColor Green
    Write-Host "Abrir:   http://127.0.0.1:$Port/adk" -ForegroundColor Green
    Write-Host "Detén el servidor con Ctrl+C; la clave se eliminará de esta sesión." -ForegroundColor Yellow
    Write-Host ""

    python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
}
finally {
    Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:GOOGLE_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_RUNTIME_MODE -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_LLM_BACKEND -ErrorAction SilentlyContinue
    Remove-Item Env:ORPHEUS_MODEL -ErrorAction SilentlyContinue

    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ($null -ne $secureKey) {
        $secureKey.Dispose()
    }

    Write-Host "Variables temporales eliminadas." -ForegroundColor DarkGray
}
