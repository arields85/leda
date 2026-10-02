<#
Moves the local checkout from D:\Proyectos\Prisma-PM to D:\Proyectos\Leda-PM (and the
worktrees folder), as planned in odd/tasks/renombre-a-leda.md (R13).

Run it from a Windows PowerShell whose current folder is NOT inside either folder, after
closing Claude Code, editors and terminals that use them, and stopping the listener:

    powershell -ExecutionPolicy Bypass -File D:\Proyectos\Prisma-PM\tools\mudar_carpeta.ps1 -DryRun
    powershell -ExecutionPolicy Bypass -File D:\Proyectos\Prisma-PM\tools\mudar_carpeta.ps1

-DryRun only checks the preconditions and prints the plan; it changes nothing.
Nothing is deleted: the old virtualenv is kept as .venv-viejo until the new one imports
leda, and the old agent memory folder is copied, not moved.
#>
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'

$OldRoot  = 'D:\Proyectos\Prisma-PM'
$NewRoot  = 'D:\Proyectos\Leda-PM'
$OldTrees = 'D:\Proyectos\Prisma-PM-worktrees'
$NewTrees = 'D:\Proyectos\Leda-PM-worktrees'
$Claude   = Join-Path $env:USERPROFILE '.claude\projects'
$OldMem   = Join-Path $Claude 'D--Proyectos-Prisma-PM\memory'
$NewMem   = Join-Path $Claude 'D--Proyectos-Leda-PM\memory'

function Step($text) { Write-Host "== $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host "STOP: $text" -ForegroundColor Red; exit 1 }

# --- Preconditions -------------------------------------------------------------------
Step 'Checking preconditions'
if (-not (Test-Path $OldRoot))  { Fail "$OldRoot does not exist (already moved?)" }
if (Test-Path $NewRoot)         { Fail "$NewRoot already exists" }
if ((Test-Path $OldTrees) -and (Test-Path $NewTrees)) { Fail "$NewTrees already exists" }
$here = (Get-Location).Path
if ($here.StartsWith($OldRoot, 'OrdinalIgnoreCase') -or $here.StartsWith($OldTrees, 'OrdinalIgnoreCase')) {
    Fail "the current folder ($here) is inside the folder to move: cd somewhere else first"
}
$busy = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and ($_.CommandLine -like "*$OldRoot*" -or $_.CommandLine -like "*$OldTrees*") -and
    $_.ProcessId -ne $PID
}
if ($busy) {
    $busy | ForEach-Object { Write-Host ("  in use by PID {0}: {1}" -f $_.ProcessId, $_.Name) }
    Fail 'close the processes above (Claude Code, editors, listener, tests) and run again'
}
foreach ($wt in @('flujo-de-un-mensaje', 'alta-y-google')) {
    $p = Join-Path $OldTrees $wt
    if (Test-Path $p) {
        $dirty = git -C $p status --porcelain
        if ($dirty) { Fail "worktree $wt has uncommitted changes" }
    }
}
if (git -C $OldRoot status --porcelain) { Fail 'the main checkout has uncommitted changes' }
Write-Host '  ok'

Step 'Plan'
Write-Host "  1. Rename $OldRoot -> $NewRoot and $OldTrees -> $NewTrees"
Write-Host '  2. git worktree repair for flujo-de-un-mensaje and alta-y-google'
Write-Host '  3. Rebuild .venv with the same packages (old one kept as .venv-viejo until verified)'
Write-Host "  4. Copy the agent memory to $NewMem (the old folder stays)"
Write-Host '  5. Delete the stale CodeGraph indexes and initialize the new one'
Write-Host '  6. Verify: git, import leda, leda estado'
if ($DryRun) { Write-Host 'Dry run: nothing changed.' -ForegroundColor Yellow; exit 0 }

# --- 1. Move -------------------------------------------------------------------------
Step 'Renaming folders'
# A folder in use cannot be renamed on Windows: the first rename fails before any change.
# If the second one fails, undo the first so nothing is left half moved.
Rename-Item -LiteralPath $OldRoot -NewName (Split-Path $NewRoot -Leaf)
if (Test-Path $OldTrees) {
    try { Rename-Item -LiteralPath $OldTrees -NewName (Split-Path $NewTrees -Leaf) }
    catch {
        Rename-Item -LiteralPath $NewRoot -NewName (Split-Path $OldRoot -Leaf)
        Fail "could not rename $OldTrees (in use?); $OldRoot was restored: $($_.Exception.Message)"
    }
}

# --- 2. Worktrees --------------------------------------------------------------------
Step 'Repairing worktrees'
$trees = @(Get-ChildItem -Directory $NewTrees -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
if ($trees.Count -gt 0) { git -C $NewRoot worktree repair @trees }
git -C $NewRoot worktree list

# --- 3. Virtualenv -------------------------------------------------------------------
Step 'Rebuilding the virtualenv'
$venv = Join-Path $NewRoot '.venv'
$old  = Join-Path $NewRoot '.venv-viejo'
$freeze = Join-Path $env:TEMP 'leda-venv-freeze.txt'
& (Join-Path $venv 'Scripts\python.exe') -m pip freeze --exclude-editable | Set-Content -Encoding ascii $freeze
$base = (& (Join-Path $venv 'Scripts\python.exe') -c 'import sys; print(sys.base_prefix)').Trim()
Rename-Item -LiteralPath $venv -NewName '.venv-viejo'
$py = Join-Path $venv 'Scripts\python.exe'
try {
    & (Join-Path $base 'python.exe') -m venv $venv
    if ($LASTEXITCODE) { throw 'venv creation failed' }
    & $py -m pip install -q --upgrade pip
    & $py -m pip install -q -r $freeze
    if ($LASTEXITCODE) { throw 'installing the frozen packages failed' }
    Push-Location $NewRoot
    & $py -m pip install -q --no-deps -e '.[dev]'
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc) { throw 'the editable install of leda failed' }
    $check = (& $py -c "import leda, importlib.util as u; print('ok' if leda.__file__.lower().startswith(r'$NewRoot'.lower()) and not u.find_spec('prisma') else 'bad')").Trim()
    if ($check -ne 'ok') { throw "the new virtualenv does not import leda from $NewRoot" }
}
catch {
    # Put the old virtualenv back so the checkout is never left without one.
    if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
    Rename-Item -LiteralPath $old -NewName '.venv'
    Fail "rebuilding .venv failed, the old one was restored: $($_.Exception.Message)"
}
Remove-Item -Recurse -Force $old
Write-Host '  ok: leda imports from the new folder'

# --- 4. Agent memory -----------------------------------------------------------------
Step 'Copying the agent memory'
if ((Test-Path $OldMem) -and -not (Test-Path $NewMem)) {
    New-Item -ItemType Directory -Force (Split-Path $NewMem) | Out-Null
    Copy-Item -Recurse $OldMem $NewMem
    Write-Host ("  copied {0} files" -f (Get-ChildItem $NewMem).Count)
} else { Write-Host '  skipped (no old memory, or the new one already exists)' }

# --- 5. CodeGraph --------------------------------------------------------------------
Step 'Resetting CodeGraph'
foreach ($root in @($NewRoot) + $trees) {
    $cg = Join-Path $root '.codegraph'
    if (Test-Path $cg) { Remove-Item -Recurse -Force $cg; Write-Host "  removed stale index in $root" }
}
if (Get-Command gentle-ai -ErrorAction SilentlyContinue) {
    gentle-ai codegraph init --cwd $NewRoot
} else { Write-Host '  gentle-ai not found: run "gentle-ai codegraph init --cwd D:\Proyectos\Leda-PM" later' }

# --- 6. Verify -----------------------------------------------------------------------
Step 'Verifying'
# Capture output and exit code before piping: piping a native command into
# Select-Object can stop it early and leave $LASTEXITCODE unreliable.
$status = git -C $NewRoot status --short --branch
if ($LASTEXITCODE) { Fail 'git does not work in the new folder' }
$status | Select-Object -First 1
# git prints worktree paths with forward slashes: normalize before comparing.
$listed = (git -C $NewRoot worktree list) -join "`n" -replace '/', '\'
if ($listed -match [regex]::Escape($OldRoot)) { Fail 'a worktree still points to the old folder' }
Push-Location $NewRoot
$estado = & $py -m leda estado corework
$rc = $LASTEXITCODE
Pop-Location
$estado | Select-Object -Last 1
if ($rc) { Fail 'leda estado failed from the new folder (is PostgreSQL running?)' }
Write-Host ''
Write-Host "Done. Open Claude Code in $NewRoot to finish (paths in docs and tools)." -ForegroundColor Green
