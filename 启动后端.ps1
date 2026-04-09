chcp 65001
$env:PYTHONUTF8 = "1"
Set-Location "D:\pyCharmProjects\workSpace02"
& ".\.conda\crm_ai\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

