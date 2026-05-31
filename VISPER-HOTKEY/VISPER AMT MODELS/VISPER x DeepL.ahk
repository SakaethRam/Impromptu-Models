; ==========================================
; ARKIN X AUTOMATION DOMAIN
; VISPER X DEEPL TRANSLATION MODEL
; ===========================================

; ========================================
; Hotkey: Ctrl+Shift+T = Run Translation
; ========================================

^+t::

    ; ================================
    ; RETRIEVE SOURCE TEXT FROM SRT
    ; ================================

    IfWinActive, ahk_exe notepad.exe
    {
        Send, ^a
        Sleep, 100
        Send, ^c
        Sleep, 200
        ClipWait, 2
        text := Clipboard
    }

    translated := ""

    ; =============================================
    ; SEND TEXT TO DEEPL AND COPY TRANSLATED TEXT
    ; =============================================

    IfWinExist, ahk_exe deepl.exe
        WinActivate
    Sleep, 400

    ; ============================================================
    ; CLICK COORDINATES IN DEEPL TO PASTE SOURCE TEXT (VIA SRT)
    ; ============================================================

    Click, 300, 185   ; 
    Sleep, 200
    Clipboard := text
    Sleep, 150
    Send, ^a
    Sleep, 100
    Send, ^v
    Sleep, 60000  ; TRANSLATION PROCESSING DELAY 

    ; ======================================================
    ; CLICK COORDINATES IN DEEPL TO COPY TRANSLATED TEXT
    ; ======================================================

    Click, 1000, 180   ; 
    Sleep, Sleep, 60000 ; TRANSLATION PROCESSING DELAY
    Clipboard := text
    Sleep, 150
    Send, ^a
    Sleep, 100
    Send, ^c
    Sleep, 400  ; 

    ; =========================================================
    ; PASTE TRANSLATED TEXT BACK INTO SRT FILE (OVER-WRITING)
    ; =========================================================

    IfWinExist, ahk_exe notepad.exe
    {
        WinActivate
        Sleep, 200
        Send, ^a
        Sleep, 200
        Send, ^v
    }

return