; VISPER x CURSOR MODEL
; AutoHotkey script to copy files from current Explorer folder to specific target folders based on file extension
; Triggered by Ctrl + Shift + M
; .mp4 and .mov files go to Video Components folder
; .wav, .mp3, and .xlsx files go to Audio Components folder
; Make sure the active window is the source folder in File Explorer

#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#Persistent  ; Keep the script running in the background

^+m::  ; Hotkey: Ctrl + Shift + M
    ; Check if active window is Explorer
    IfWinActive, ahk_class CabinetWClass
    {
        ; Get the path of the active Explorer window
        WinGet, active_id, ID, A
        for window in ComObjCreate("Shell.Application").Windows
        {
            if (window.hwnd = active_id)
            {
                sourceFolder := window.Document.Folder.Self.Path
                break
            }
        }

        if !sourceFolder
        {
            MsgBox, Could not retrieve the source folder path.
            return
        }

        ; Define the hardcoded target folders
        videoFolder := "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\Video Components"
        audioFolder := "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\Audio Components"

        ; Verify if target folders exist, attempt to create them if they don't
        if !InStr(FileExist(videoFolder), "D")
        {
            try
            {
                FileCreateDir, %videoFolder%
            }
            catch
            {
                MsgBox, Could not create or access video folder: %videoFolder%
                return
            }
        }

        if !InStr(FileExist(audioFolder), "D")
        {
            try
            {
                FileCreateDir, %audioFolder%
            }
            catch
            {
                MsgBox, Could not create or access audio folder: %audioFolder%
                return
            }
        }

        ; Copy files based on their extensions (no per-file MsgBox)
        copied := 0
        failed := 0
        failedDetails := ""
        Loop, Files, %sourceFolder%\*.*, F  ; Include all files
        {
            ; Skip folders
            if InStr(FileExist(A_LoopFileFullPath), "D")
                continue

            ; Get file extension (manual lowercase conversion for compatibility)
            SplitPath, A_LoopFileFullPath,,, fileExt
            StringLower, fileExt, fileExt

            ; Determine target folder based on extension
            target := ""
            if (fileExt = "mp4" || fileExt = "mov")
            {
                target := videoFolder
            }
            else if (fileExt = "wav" || fileExt = "mp3" || fileExt = "xlsx")
            {
                target := audioFolder
            }
            else
            {
                continue  ; Skip files with unhandled extensions
            }

            if (target != "")
            {
                try
                {
                    FileCopy, %A_LoopFileFullPath%, %target%\%A_LoopFileName%, 1  ; 1 = overwrite
                    if ErrorLevel = 0
                    {
                        if FileExist(target . "\" . A_LoopFileName)
                        {
                            copied++
                        }
                        else
                        {
                            failed++
                            failedDetails .= "Copy of " . A_LoopFileName . " to " . target . " completed but file not found.`n"
                        }
                    }
                    else
                    {
                        failed++
                        failedDetails .= "Failed to copy " . A_LoopFileName . " to " . target . " (ErrorLevel: " . ErrorLevel . ")`n"
                    }
                }
                catch e
                {
                    failed++
                    failedDetails .= "Failed to copy " . A_LoopFileName . " to " . target . " (Exception: " . e . ")`n"
                }
            }
        }

        ; Provide summary feedback
        if (copied > 0 && failed = 0)
            MsgBox, Successfully copied %copied% file(s) to their respective folders.
        else if (copied > 0 && failed > 0)
            MsgBox, Copied %copied% file(s) to their respective folders, but %failed% file(s) failed to copy.`n`nDetails:`n%failedDetails%
        else if (failed > 0)
            MsgBox, Failed to copy %failed% file(s).`n`nDetails:`n%failedDetails%
        else
            MsgBox, No matching files (.mp4, .mov, .wav, .mp3, .xlsx) were found in %sourceFolder%.
    }
    else
    {
        MsgBox, Please activate the source folder in File Explorer.
    }
return