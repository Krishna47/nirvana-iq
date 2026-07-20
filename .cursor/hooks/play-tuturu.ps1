# Cursor stop hook: play Tuturu completion sound
$soundPath = "D:\Music\Anime Sounds\tuturu.mp3"
if (-not (Test-Path $soundPath)) { exit 0 }
try {
    Add-Type -AssemblyName presentationCore
    $player = New-Object System.Windows.Media.MediaPlayer
    $player.Open([uri]((Resolve-Path $soundPath).Path))
    $player.Play()
    Start-Sleep -Milliseconds 2200
} catch {
    # fail open
}
exit 0
