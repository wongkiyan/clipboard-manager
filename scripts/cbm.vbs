Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 1. 動態取得專案根目錄並設定工作目錄
vbsFullName = WScript.ScriptFullName
vbsDirectory = fso.GetParentFolderName(vbsFullName)
projectRoot = fso.GetParentFolderName(vbsDirectory)
WshShell.CurrentDirectory = projectRoot

' 2. 設定 pythonw.exe 與進入點 main.py 的路徑
pythonwPath = fso.BuildPath(projectRoot, ".venv\Scripts\pythonw.exe")
scriptPath = fso.BuildPath(projectRoot, "src\main.py")

' 3. 收集所有從命令列傳進來的參數 (例如 slash, clear)
Dim args, i
args = ""
For i = 0 To WScript.Arguments.Count - 1
    args = args & " """ & WScript.Arguments(i) & """"
Next

' 4. 🚀 核心無痕執行：最後的 0 代表完全隱藏視窗，False 代表不需要等待程式結束才釋放
WshShell.Run """" & pythonwPath & """ """ & scriptPath & """" & args, 0, False