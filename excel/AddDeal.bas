Attribute VB_Name = "AddDeal"
'==============================================================================
' IC Go/No-Go — add-a-deal macros
'==============================================================================
' Three buttons:
'
'   ImportProForma  ── THE "DROP A SPREADSHEET IN" BUTTON. Pops a file picker,
'                      reads the pro forma you choose, pulls the metrics, drops
'                      them into the next empty "New Deal" slot, recalculates,
'                      and shows the GO / NO-GO verdict. No typing.
'   AddDeal         ── copies the NEW DEAL FORM ("Add a Deal" sheet) into the
'                      next slot.
'   ClearForm       ── empties the form.
'
'   Only input rows are written; the derived cells (is-development, LTV,
'   yield-on-cost, market VLOOKUPs) stay as live formulas, so the verdict is
'   decided off the Springfield & Hamburg statics either way.
'
' One-time setup (the dashboard is delivered as .xlsx; macros need .xlsm)
'   1. Open IC_GoNoGo_Dashboard.xlsx in Excel.
'   2. File > Save As > Excel Macro-Enabled Workbook (*.xlsm).
'   3. Press Alt+F11 (VBA editor) > File > Import File... > pick this AddDeal.bas.
'   4. On the "Add a Deal" sheet: Insert > Shapes (a rounded rectangle), label it
'      "Import Pro Forma", right-click > Assign Macro... > ImportProForma.
'   5. (Optional) add buttons for AddDeal and ClearForm the same way.
'   Trust note: Excel will ask to enable macros when reopening the .xlsm.
'
' Note on the market: a pro forma rarely names its county cleanly, so after an
' import you may need to pick the deal's county from the dropdown on the slot's
' "Market (county)" cell — that fills population/growth/pipeline/rank and clears
' the population gate. The engine of record for messy files is the Python
' importer:  python -m deal_agent.ic.cli add --proforma X.xlsx --market "<county>"
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

'==============================================================================
' ImportProForma — pick a spreadsheet, extract it, score it.
'==============================================================================
Public Sub ImportProForma()
    Dim path As Variant
    path = Application.GetOpenFilename( _
        "Excel files (*.xlsx;*.xlsm;*.xls),*.xlsx;*.xlsm;*.xls", , _
        "Select a pro forma to import")
    If VarType(path) = vbBoolean Then Exit Sub      ' user cancelled

    Dim wsD As Worksheet, wsDash As Worksheet, wsS As Worksheet
    Set wsD = ThisWorkbook.Sheets("Deals")
    Set wsDash = ThisWorkbook.Sheets("Dashboard")
    Set wsS = ThisWorkbook.Sheets("Scores")

    ' find the first empty "New Deal" slot
    Dim targetCol As Long, totalRow As Long
    totalRow = Application.Match("Total cost", wsD.Range("A:A"), 0)
    targetCol = FindEmptySlot(wsD, totalRow)
    If targetCol = 0 Then
        MsgBox "No empty 'New Deal' slots left. Copy a New Deal column on the Deals tab to add one.", _
            vbExclamation, "IC Go/No-Go": Exit Sub
    End If

    ' open the chosen file read-only and extract
    Dim src As Workbook, prevAlerts As Boolean
    prevAlerts = Application.DisplayAlerts
    Application.ScreenUpdating = False: Application.DisplayAlerts = False
    On Error GoTo Fail
    Set src = Workbooks.Open(CStr(path), ReadOnly:=True, UpdateLinks:=0)

    Dim m As Object, isDev As Boolean, county As String
    Set m = CreateObject("Scripting.Dictionary")
    isDev = ExtractMetrics(src, m, county)
    src.Close SaveChanges:=False

    ' derive total cost from the capital stack if it wasn't labelled
    If Not m.Exists("total_cost") Then
        If m.Exists("equity") And m.Exists("debt") Then m("total_cost") = m("equity") + m("debt")
    End If

    ' write into the slot
    Dim nm As String
    nm = Left(Dir(CStr(path)), InStrRev(Dir(CStr(path)), ".") - 1)
    wsD.Cells(1, targetCol).Value = nm
    wsD.Cells(Application.Match("Deal type", wsD.Range("A:A"), 0), targetCol).Value = _
        IIf(isDev, "Development", "Income/Core (DST/Stabilized)")
    If Len(county) > 0 Then PutField wsD, targetCol, "Market (county)", county

    PutField wsD, targetCol, "Total cost", m, "total_cost"
    PutField wsD, targetCol, "Equity", m, "equity"
    PutField wsD, targetCol, "Debt", m, "debt"
    PutField wsD, targetCol, "Going-in cap", m, "going_in_cap"
    PutField wsD, targetCol, "Exit cap", m, "exit_cap"
    PutField wsD, targetCol, "NOI", m, "noi"
    PutField wsD, targetCol, "Op-ex ratio", m, "opex_ratio"
    PutField wsD, targetCol, "Unlevered IRR", m, "unlevered_irr"
    PutField wsD, targetCol, "Levered IRR", m, "levered_irr"
    PutField wsD, targetCol, "NRSF", m, "nrsf"
    PutField wsD, targetCol, "Site acreage", m, "site_acreage"
    PutField wsD, targetCol, "Units", m, "units"

    Application.CalculateFull
    Application.ScreenUpdating = True: Application.DisplayAlerts = prevAlerts

    wsDash.Activate
    wsDash.Range("B3").Value = nm

    Dim vcol As Variant, msg As String
    vcol = Application.Match(nm, wsS.Range("1:1"), 0)
    msg = "Imported '" & nm & "'." & vbCrLf & vbCrLf
    If Not IsError(vcol) Then
        msg = msg & "Verdict: " & wsS.Cells(14, CLng(vcol)).Value & _
            "   (score " & wsS.Cells(12, CLng(vcol)).Value & "/100)" & vbCrLf & vbCrLf
    End If
    If Len(county) = 0 Then
        msg = msg & "Couldn't read the market from the file — pick the county from the " & _
            "dropdown on the slot's 'Market (county)' cell to complete the market gates."
    End If
    MsgBox msg, vbInformation, "IC Go/No-Go"
    Exit Sub
Fail:
    On Error Resume Next
    If Not src Is Nothing Then src.Close SaveChanges:=False
    Application.ScreenUpdating = True: Application.DisplayAlerts = prevAlerts
    MsgBox "Could not import: " & Err.Description, vbExclamation, "IC Go/No-Go"
End Sub

' Scan every sheet for labelled line items; fill dict `m` (field -> number) and
' `county`. Returns True if the file looks like a development deal. Mirrors the
' Python extractor (deal_agent/ic/extract.py).
Private Function ExtractMetrics(src As Workbook, ByRef m As Object, ByRef county As String) As Boolean
    Dim ws As Worksheet, ur As Range, r As Long, c As Long
    Dim label As String, num As Double, haveNum As Boolean, txtRight As String
    Dim blob As String
    For Each ws In src.Worksheets
        Set ur = ws.UsedRange
        Dim rows As Long, cols As Long
        rows = Application.Min(ur.rows.Count, 400): cols = Application.Min(ur.Columns.Count, 30)
        For r = 1 To rows
            label = "": haveNum = False: txtRight = ""
            For c = 1 To cols
                Dim v As Variant: v = ur.Cells(r, c).Value
                If VarType(v) = vbString Then
                    If Len(Trim(v)) > 0 Then
                        blob = blob & " " & LCase(v)
                        If label = "" Then label = LCase(Trim(v)) Else If txtRight = "" Then txtRight = Trim(CStr(v))
                    End If
                ElseIf IsNumeric(v) And Not haveNum And Len(CStr(v)) > 0 And VarType(v) <> vbBoolean Then
                    num = CDbl(v): haveNum = True
                End If
            Next c
            If Len(label) > 0 Then MapLabel m, label, num, haveNum, txtRight, county
        Next r
    Next ws
    ExtractMetrics = (InStr(blob, "development budget") > 0 Or InStr(blob, "construction") > 0 _
        Or InStr(blob, "yield on cost") > 0 Or InStr(blob, "hard cost") > 0 _
        Or InStr(blob, "pay app") > 0 Or InStr(blob, "lease up") > 0)
End Function

Private Sub MapLabel(m As Object, label As String, num As Double, haveNum As Boolean, _
                     txtRight As String, ByRef county As String)
    ' market label (text to the right), first one wins
    If county = "" Then
        If Has(label, "county") Or Has(label, "market") Or Has(label, "location") _
           Or Has(label, "city") Or Has(label, "msa") Or Has(label, "cbsa") Then
            If Len(txtRight) > 0 Then county = txtRight
        End If
    End If
    If Not haveNum Then Exit Sub
    ' keyword -> field, priority order, first match wins, never overwrite
    If Has(label, "exit cap") Then SetRate m, "exit_cap", num: Exit Sub
    If Has(label, "syndicated cap rate") Then SetRate m, "going_in_cap", num: Exit Sub
    If Has(label, "going-in cap") Or Has(label, "going in cap") Or Has(label, "year 1 cap") _
       Or Has(label, "in-place cap") Then SetRate m, "going_in_cap", num: Exit Sub
    If Has(label, "net operating income") Or Has(label, "noi") Then SetNum m, "noi", num: Exit Sub
    If Has(label, "unlevered irr") Then SetRate m, "unlevered_irr", num: Exit Sub
    If Has(label, "levered irr") Then SetRate m, "levered_irr", num: Exit Sub
    If Has(label, "irr") Then SetRate m, "unlevered_irr", num: Exit Sub
    If Has(label, "partnership level budget") Or Has(label, "development budget") _
       Or Has(label, "total project cost") Or Has(label, "total capitalization") _
       Or Has(label, "total cost") Then SetNum m, "total_cost", num: Exit Sub
    If Has(label, "permanent debt") Or Has(label, "construction financing") _
       Or Has(label, "mortgage") Or Has(label, "loan amount") Or Has(label, "debt") _
       Then SetNum m, "debt", num: Exit Sub
    If Has(label, "equity") Then SetNum m, "equity", num: Exit Sub
    If Has(label, "net rentable") Or Has(label, "nrsf") Then SetNum m, "nrsf", num: Exit Sub
    If Has(label, "acreage") Or Has(label, "acres") Then SetNum m, "site_acreage", num: Exit Sub
    If Has(label, "units") Then SetNum m, "units", num: Exit Sub
End Sub

Private Function Has(label As String, kw As String) As Boolean
    Has = (InStr(label, kw) > 0)
End Function

Private Sub SetNum(m As Object, key As String, num As Double)
    If Not m.Exists(key) Then m(key) = num
End Sub

Private Sub SetRate(m As Object, key As String, num As Double)
    ' normalise percentages entered as 7 / 11.3 rather than 0.07 / 0.113
    If Not m.Exists(key) Then
        If Abs(num) > 1.5 Then m(key) = num / 100# Else m(key) = num
    End If
End Sub

Private Function FindEmptySlot(wsD As Worksheet, totalRow As Long) As Long
    Dim col As Long, lastCol As Long
    lastCol = wsD.Cells(1, wsD.Columns.Count).End(xlToLeft).Column
    For col = 2 To lastCol
        If InStr(1, CStr(wsD.Cells(1, col).Value), "New Deal") > 0 Then
            If Len(CStr(wsD.Cells(totalRow, col).Value)) = 0 Then FindEmptySlot = col: Exit Function
        End If
    Next col
    FindEmptySlot = 0
End Function

' Write a value into (label-row, col) on the Deals tab. Two forms:
'   PutField ws, col, "Market (county)", "Williamson County, Tennessee"
'   PutField ws, col, "Total cost", dict, "total_cost"   ' only if the key exists
Private Sub PutField(wsD As Worksheet, col As Long, dealLabel As String, _
                     ParamArray a() As Variant)
    Dim drow As Variant
    drow = Application.Match(dealLabel, wsD.Range("A:A"), 0)
    If IsError(drow) Then Exit Sub
    If UBound(a) = 0 Then
        wsD.Cells(CLng(drow), col).Value = a(0)
    Else
        Dim m As Object: Set m = a(0)
        If m.Exists(CStr(a(1))) Then wsD.Cells(CLng(drow), col).Value = m(CStr(a(1)))
    End If
End Sub
