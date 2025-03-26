# WooAgent System Test Script

# -------------------------------------------------------------------------
# סקריפט בדיקה למערכת WooAgent
# בודק את פעולת המערכת כיחידה אחת - צד שרת, צד לקוח והסוכן
# -------------------------------------------------------------------------

# הגדרות צבעים להודעות
$GREEN = [ConsoleColor]::Green
$RED = [ConsoleColor]::Red
$YELLOW = [ConsoleColor]::Yellow
$CYAN = [ConsoleColor]::Cyan

# פונקציה להדפסת הודעות
function Write-Status {
    param (
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White,
        [switch]$NoNewLine
    )
    
    if ($NoNewLine) {
        Write-Host $Message -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Test-Port {
    param (
        [int]$Port = 3001
    )
    
    try {
        $conn = New-Object System.Net.Sockets.TcpClient
        $conn.Connect("localhost", $Port)
        $conn.Close()
        return $true
    } catch {
        return $false
    }
}

# פונקציות לבדיקת זמינות
function Wait-ForPort {
    param (
        [int]$Port = 3001,
        [int]$Timeout = 30,
        [string]$ServiceName = "Backend Server"
    )
    
    Write-Status "ממתין לזמינות $ServiceName בפורט $Port..." -Color $CYAN
    
    $timer = [Diagnostics.Stopwatch]::StartNew()
    
    while ($timer.Elapsed.TotalSeconds -lt $Timeout) {
        if (Test-Port -Port $Port) {
            Write-Status "✅ $ServiceName זמין בפורט $Port" -Color $GREEN
            return $true
        }
        
        Start-Sleep -Seconds 1
        Write-Status "." -Color $YELLOW -NoNewLine
    }
    
    Write-Status "`n❌ $ServiceName לא זמין גם אחרי $Timeout שניות" -Color $RED
    return $false
}

# בדיקת תלויות
function Test-Dependencies {
    Write-Status "בודק תלויות..." -Color $CYAN
    
    # בדיקת Node.js
    $nodeVersion = node --version
    if ($LASTEXITCODE -ne 0) {
        Write-Status "❌ Node.js אינו מותקן או לא זמין" -Color $RED
        return $false
    }
    Write-Status "✅ Node.js מותקן: $nodeVersion" -Color $GREEN
    
    # בדיקת npm
    $npmVersion = npm --version
    if ($LASTEXITCODE -ne 0) {
        Write-Status "❌ npm אינו מותקן או לא זמין" -Color $RED
        return $false
    }
    Write-Status "✅ npm מותקן: $npmVersion" -Color $GREEN
    
    # בדיקת Python
    $pythonVersion = python --version
    if ($LASTEXITCODE -ne 0) {
        Write-Status "❌ Python אינו מותקן או לא זמין" -Color $RED
        return $false
    }
    Write-Status "✅ Python מותקן: $pythonVersion" -Color $GREEN
    
    return $true
}

# בדיקת תקשורת עם השרת
function Test-APIEndpoint {
    param (
        [string]$Endpoint = "http://localhost:3001/api",
        [string]$Description = "API Endpoint"
    )
    
    try {
        Write-Status "בודק נגישות ל-$Description..." -Color $CYAN
        $response = Invoke-RestMethod -Uri $Endpoint -TimeoutSec 5
        Write-Status "✅ הנתיב $Description נגיש" -Color $GREEN
        return $true
    } catch {
        Write-Status "❌ הנתיב $Description אינו נגיש: $_" -Color $RED
        return $false
    }
}

# פונקציה להפעלת שרת הבאקאנד
function Start-BackendServer {
    Write-Status "מפעיל את שרת הבאקאנד..." -Color $CYAN
    
    $backendPath = "C:\Users\slava\Desktop\AiAgents\EgentVer2\wooagent-backend"
    
    # בדיקה אם התיקייה קיימת
    if (-not (Test-Path $backendPath)) {
        Write-Status "❌ תיקיית הבאקאנד לא נמצאה: $backendPath" -Color $RED
        return $false
    }
    
    # התקנת תלויות אם צריך
    Set-Location $backendPath
    if (-not (Test-Path "$backendPath\node_modules")) {
        Write-Status "מתקין תלויות עבור הבאקאנד..." -Color $YELLOW
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Status "❌ התקנת תלויות הבאקאנד נכשלה" -Color $RED
            return $false
        }
    }
    
    # הפעלת השרת בתהליך נפרד
    Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $backendPath -WindowStyle Hidden
    
    # המתנה להפעלת השרת
    return (Wait-ForPort -Port 3001 -ServiceName "Backend Server" -Timeout 30)
}

# פונקציה להפעלת סוכן ה-AI
function Start-AgentProcess {
    Write-Status "מפעיל את סוכן ה-AI..." -Color $CYAN
    
    $agentPath = "C:\Users\slava\Desktop\AiAgents\EgentVer2\woo_agent"
    
    # בדיקה אם התיקייה קיימת
    if (-not (Test-Path $agentPath)) {
        Write-Status "❌ תיקיית הסוכן לא נמצאה: $agentPath" -Color $RED
        return $false
    }
    
    # התקנת תלויות אם צריך
    Set-Location $agentPath
    if (-not (Test-Path "$agentPath\venv")) {
        Write-Status "יוצר סביבה וירטואלית Python עבור הסוכן..." -Color $YELLOW
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Status "❌ יצירת סביבה וירטואלית נכשלה" -Color $RED
            return $false
        }
        
        # הפעלת הסביבה הוירטואלית
        & "$agentPath\venv\Scripts\Activate.ps1"
        
        Write-Status "מתקין תלויות Python עבור הסוכן..." -Color $YELLOW
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Status "❌ התקנת תלויות Python נכשלה" -Color $RED
            return $false
        }
    }
    
    # הפעלת הסוכן
    Write-Status "מפעיל את הסוכן..." -Color $CYAN
    Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $agentPath -WindowStyle Hidden
    
    # המתנה להפעלת הסוכן (יכול להיות שהסוכן מתחבר רק דרך backend, צריך להתאים בדיקה זו)
    Start-Sleep -Seconds 5  # נותן זמן לסוכן לעלות
    
    # בדיקה האם הסוכן פעיל דרך ה-API
    return (Test-APIEndpoint -Endpoint "http://localhost:3001/api/agent/status" -Description "Agent Status API")
}

# פונקציה לבדיקת הפרונטאנד
function Test-Frontend {
    Write-Status "בודק את הפרונטאנד..." -Color $CYAN
    
    $frontendPath = "C:\Users\slava\Desktop\AiAgents\EgentVer2\wooagent-frontend"
    
    # בדיקה אם התיקייה קיימת
    if (-not (Test-Path $frontendPath)) {
        Write-Status "❌ תיקיית הפרונטאנד לא נמצאה: $frontendPath" -Color $RED
        return $false
    }
    
    # בדיקה אם אפשר לבנות את הפרונטאנד
    Set-Location $frontendPath
    
    # התקנת תלויות אם צריך
    if (-not (Test-Path "$frontendPath\node_modules")) {
        Write-Status "מתקין תלויות עבור הפרונטאנד..." -Color $YELLOW
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Status "❌ התקנת תלויות הפרונטאנד נכשלה" -Color $RED
            return $false
        }
    }
    
    # בדיקת build
    Write-Status "בודק אם הפרונטאנד מתקמפל..." -Color $CYAN
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Status "❌ הקמפול של הפרונטאנד נכשל" -Color $RED
        return $false
    }
    
    Write-Status "✅ הפרונטאנד התקמפל בהצלחה" -Color $GREEN
    return $true
}

# פונקציה לבדיקת המערכת המלאה
function Test-FullSystem {
    Write-Status "בודק את המערכת המלאה..." -Color $CYAN
    
    $success = $true
    
    # בדיקת תקשורת בין הבאקאנד לסוכן
    $agentStatus = Test-APIEndpoint -Endpoint "http://localhost:3001/api/agent/status" -Description "Agent Status API"
    if (-not $agentStatus) {
        $success = $false
    }
    
    # בדיקת נתיבי API נוספים
    $storeConfig = Test-APIEndpoint -Endpoint "http://localhost:3001/api/store/config" -Description "Store Config API"
    if (-not $storeConfig) {
        $success = $false
    }
    
    # בדיקת תקשורת צ'אט
    $chatEndpoint = Test-APIEndpoint -Endpoint "http://localhost:3001/api/chat/message" -Description "Chat API"
    if (-not $chatEndpoint) {
        $success = $false
    }
    
    return $success
}

# פונקציה לניקוי ועצירת כל התהליכים
function Stop-AllProcesses {
    Write-Status "מנקה ועוצר את כל התהליכים..." -Color $CYAN
    
    # עצירת תהליכי Node.js
    Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $_.Kill()
            Write-Status "עצר תהליך Node.js: $($_.Id)" -Color $YELLOW
        } catch {
            Write-Status "נכשל בעצירת תהליך Node.js: $($_.Id) - $_" -Color $RED
        }
    }
    
    # עצירת תהליכי Python
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $_.Kill()
            Write-Status "עצר תהליך Python: $($_.Id)" -Color $YELLOW
        } catch {
            Write-Status "נכשל בעצירת תהליך Python: $($_.Id) - $_" -Color $RED
        }
    }
    
    Write-Status "כל התהליכים נוקו" -Color $GREEN
}

# פונקציה ראשית להרצת הבדיקות
function Start-SystemTest {
    Write-Status "מתחיל בדיקת מערכת מלאה עבור WooAgent..." -Color $CYAN
    Write-Status "----------------------------------------" -Color $CYAN
    
    # ניקוי תהליכים קודמים
    Stop-AllProcesses
    
    # בדיקת תלויות
    $depsOk = Test-Dependencies
    if (-not $depsOk) {
        Write-Status "❌ בדיקת התלויות נכשלה, הבדיקה מופסקת" -Color $RED
        return
    }
    
    # הפעלת שרת הבאקאנד
    $backendOk = Start-BackendServer
    if (-not $backendOk) {
        Write-Status "❌ הפעלת שרת הבאקאנד נכשלה, הבדיקה מופסקת" -Color $RED
        Stop-AllProcesses
        return
    }
    
    # הפעלת הסוכן
    $agentOk = Start-AgentProcess
    if (-not $agentOk) {
        Write-Status "❌ הפעלת הסוכן נכשלה, הבדיקה מופסקת" -Color $RED
        Stop-AllProcesses
        return
    }
    
    # בדיקת הפרונטאנד
    $frontendOk = Test-Frontend
    if (-not $frontendOk) {
        Write-Status "❌ בדיקת הפרונטאנד נכשלה, הבדיקה מופסקת" -Color $RED
        Stop-AllProcesses
        return
    }
    
    # בדיקת המערכת המלאה
    $systemOk = Test-FullSystem
    if ($systemOk) {
        Write-Status "✅ בדיקת המערכת המלאה הצליחה!" -Color $GREEN
    } else {
        Write-Status "⚠️ בדיקת המערכת המלאה נתקלה בבעיות כלשהן" -Color $YELLOW
    }
    
    # ניקוי תהליכים
    Write-Status "האם לעצור את כל התהליכים שהופעלו לצורך הבדיקה? (Y/N)" -Color $CYAN
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Stop-AllProcesses
    } else {
        Write-Status "התהליכים ממשיכים לרוץ. זכור לעצור אותם ידנית בסיום." -Color $YELLOW
    }
    
    Write-Status "----------------------------------------" -Color $CYAN
    Write-Status "בדיקת המערכת הסתיימה" -Color $CYAN
}

# הפעלת הבדיקה
Start-SystemTest
