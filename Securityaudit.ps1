# PowerShell Script: Security Clean-up and Backdoor Check
$Output = "$env:USERPROFILE\Desktop\SecurityCheck_Results.txt"
"--- SECURITY AUDIT STARTED ---" | Out-File $Output

# STEP 1: Scan for Shell Files (.bat, .vbs, .ps1)
"Scanning for Shell Files..." | Tee-Object -FilePath $Output -Append
Get-ChildItem -Path C:\ -Recurse -Include *.bat, *.vbs, *.ps1 -ErrorAction SilentlyContinue | 
    Select-Object FullName | 
    Tee-Object -FilePath $Output -Append

# STEP 2: List All Scheduled Tasks
"`nScheduled Tasks:" | Tee-Object -FilePath $Output -Append
schtasks /query /fo LIST /v | Tee-Object -FilePath $Output -Append

# STEP 3: Show All Network Connections
"`nLive Network Connections:" | Tee-Object -FilePath $Output -Append
netstat -ano | Select-String "ESTABLISHED" | Tee-Object -FilePath $Output -Append

# STEP 4: List All Startup Programs
"`nStartup Programs (Registry & Folder):" | Tee-Object -FilePath $Output -Append
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | 
    Format-List | Tee-Object -FilePath $Output -Append

# STEP 5: Show Remote Desktop Status
"`nRemote Desktop Status:" | Tee-Object -FilePath $Output -Append
(Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server").fDenyTSConnections | 
    ForEach-Object { "RDP Enabled: $([bool](1 - $_))" } | Tee-Object -FilePath $Output -Append

# STEP 6: List Local Users
"`nLocal User Accounts:" | Tee-Object -FilePath $Output -Append
Get-LocalUser | Format-List Name, Enabled, LastLogon | Tee-Object -FilePath $Output -Append

# STEP 7: Disable Remote Registry (if running)
Stop-Service RemoteRegistry -ErrorAction SilentlyContinue
Set-Service RemoteRegistry -StartupType Disabled

"`nRemote Registry Disabled (if it was running)" | Tee-Object -FilePath $Output -Append

"--- SECURITY AUDIT COMPLETE ---" | Tee-Object -FilePath $Output -Append
Start-Sleep -Seconds 2
notepad $Output
