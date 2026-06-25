Attribute VB_Name = "AddDeal"
'==============================================================================
' IC Go/No-Go — one-click "Add Deal" macro
'==============================================================================
' What it does
'   Reads the NEW DEAL FORM on the "Add a Deal" sheet, copies it into the next
'   empty "New Deal" column on the Deals tab, recalculates, jumps to the
'   Dashboard with the new deal selected, and pops up its GO / NO-GO verdict.
'
'   Only the input rows are written; the derived cells (is-development, LTV,
'   yield-on-cost, and the market VLOOKUPs) stay as live formulas, so the
'   verdict is decided off the Springfield & Hamburg statics exactly like the
'   typed-in path.
'
' One-time setup (the dashboard is delivered as .xlsx; macros need .xlsm)
'   1. Open IC_GoNoGo_Dashboard.xlsx in Excel.
'   2. File > Save As > Excel Macro-Enabled Workbook (*.xlsm).
'   3. Press Alt+F11 (VBA editor) > File > Import File... > pick this AddDeal.bas.
'   4. Back on the "Add a Deal" sheet: Insert > Shapes (a rounded rectangle),
'      label it "Add Deal", right-click > Assign Macro... > AddDeal.
'   5. (Optional) add a second button assigned to ClearForm.
'   Trust note: Excel will ask to enable macros when reopening the .xlsm.
'==============================================================================

Option Explicit

Private Const FORM_NAME_ROW As Long = 21   ' "Deal name" input cell is B21
Private Const FORM_FIRST_FIELD As Long = 22 ' first mapped field (Deal type) is B22

' Form fields B22..B35 map, in order, to these labels in column A of the Deals tab.
Private Function FieldLabels() As Variant
    FieldLabels = Array("Deal type", "Market (county)", "Total cost", "Equity", _
        "Debt", "Going-in cap", "Exit cap", "NOI", "Op-ex ratio", "Unlevered IRR", _
        "Levered IRR", "NRSF", "Site acreage", "Units")
End Function

Public Sub AddDeal()
    Dim wsD As Worksheet, wsF As Worksheet, wsDash As Worksheet, wsS As Worksheet
    On Error GoTo Fail
    Set wsD = ThisWorkbook.Sheets("Deals")
    Set wsF = ThisWorkbook.Sheets("Add a Deal")
    Set wsDash = ThisWorkbook.Sheets("Dashboard")
    Set wsS = ThisWorkbook.Sheets("Scores")

    Dim totalRow As Long
    totalRow = Application.Match("Total cost", wsD.Range("A:A"), 0)

    ' find the first empty "New Deal" column
    Dim col As Long, lastCol As Long, targetCol As Long
    lastCol = wsD.Cells(1, wsD.Columns.Count).End(xlToLeft).Column
    For col = 2 To lastCol
        If InStr(1, CStr(wsD.Cells(1, col).Value), "New Deal") > 0 Then
            If Len(CStr(wsD.Cells(totalRow, col).Value)) = 0 Then
                targetCol = col: Exit For
            End If
        End If
    Next col
    If targetCol = 0 Then
        MsgBox "No empty 'New Deal' slots left. Copy a New Deal column on the Deals tab to add one.", _
            vbExclamation, "IC Go/No-Go": Exit Sub
    End If

    ' deal name
    Dim nm As String
    nm = Trim(CStr(wsF.Cells(FORM_NAME_ROW, 2).Value))
    If Len(nm) = 0 Then nm = "New Deal " & (targetCol - 1)
    wsD.Cells(1, targetCol).Value = nm

    ' copy each filled form field into its labelled row on the Deals tab
    Dim labels As Variant, i As Long, drow As Variant, v As Variant
    labels = FieldLabels()
    For i = 0 To UBound(labels)
        drow = Application.Match(labels(i), wsD.Range("A:A"), 0)
        If Not IsError(drow) Then
            v = wsF.Cells(FORM_FIRST_FIELD + i, 2).Value
            If Len(CStr(v)) > 0 Then wsD.Cells(CLng(drow), targetCol).Value = v
        End If
    Next i

    Application.CalculateFull

    ' show it on the dashboard
    wsDash.Activate
    wsDash.Range("B3").Value = nm

    ' report the verdict
    Dim vcol As Variant
    vcol = Application.Match(nm, wsS.Range("1:1"), 0)
    If Not IsError(vcol) Then
        MsgBox nm & ":  " & wsS.Cells(14, CLng(vcol)).Value & _
            "   (score " & wsS.Cells(12, CLng(vcol)).Value & "/100)", _
            vbInformation, "IC Go/No-Go"
    End If
    Exit Sub
Fail:
    MsgBox "Could not add the deal: " & Err.Description, vbExclamation, "IC Go/No-Go"
End Sub

' Clear the NEW DEAL FORM inputs (leaves the Deal type defaulted to Income/Core).
Public Sub ClearForm()
    Dim wsF As Worksheet, i As Long
    Set wsF = ThisWorkbook.Sheets("Add a Deal")
    wsF.Range("B" & FORM_NAME_ROW).ClearContents
    For i = 0 To UBound(FieldLabels())
        wsF.Cells(FORM_FIRST_FIELD + i, 2).ClearContents
    Next i
    wsF.Cells(FORM_FIRST_FIELD, 2).Value = "Income/Core (DST/Stabilized)"
End Sub
