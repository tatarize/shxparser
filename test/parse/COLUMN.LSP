;--------------------------- INTERNAL ERROR HANDLER --------------------------|

(DeFun ssx-err (s)                    ; If an error (such as CTRL-C) occurs
                                      ; while this command is active...
(if (/= s "Function cancelled")
    (Princ (strcat "\nError: " s))
)
(SetQ *error* olderr)                 ; Restore old *error* handler
(Princ)
)

;-------------------------------- MAIN PROGRAM -------------------------------|
;(c) TiTle GAAA
;17 Mar 90
;18 Mar 90
;23 Mar 90
;26 Mar 90
;31 Mar 90
;1  Apr 90
;2  Apr 90
;3  Apr 90
;4  Apr 90
;5  Apr 90
;6  May 91  Adding Column & Footing Schedule To Drawing

;***************>
(DeFun c:Clear ()
(SetQ StructuralData Nil)
)
;--------------------------------  Column  -------------------------------|
;***************>
(DeFun InputColumnData (/ t1 t2 t3 t4)
        ;Input base point
 (InitGet (+ 2 4))
 (SetQ
        ColumnBasePoint (GetPoint "\nBase point of column: ")
                ;Input Span Right SpanRight
        SpanRight (GetDist "\nSpan Right to column: " ColumnBasePoint)
                ;Input Span lift  SpanLift
        SpanLift  (GetDist "\nSpan Lift  to column: " ColumnBasePoint)
                ;Input Span Up    SpanUp
        SpanUp    (GetDist "\nSpan Up    to column: " ColumnBasePoint)
                ;Input Span down  SpanDown
        SpanDown  (GetDist "\nSpan Down  to column: " ColumnBasePoint)

        Column (ColumnType)
 )
)

;***************>
(DeFun CalculationOfColumn (/ t1 t2 t3 t4)
 (SetQ
        Area  (* (/ (+ SpanRight SpanLift) 2.0)  (/ (+ SpanUp SpanDown) 2.0) )
        W (+ LifeLoad DeadLoad Par)  ;Load
        F       (* Area W NoOfFloors 1.10)
        FConcrete    (* 0.24 CubeStrengthOfConcrete28)
        AreaConcrete (/ F (* (* FConcrete (+ 1.0 (* %OfSteel 0.15))) Omg) )
        AreaSteel (* %OfSteel (/ AreaConcrete 100.0))
 )
)
;***************>
(DeFun ColumnArea ()
(SetQ  xx

        (cond
                ((eq (FLetter CType) "R")
                     (SetQ LengthOfColumn (/ AreaConcrete Widthofcolumn)
                           DirectionOfColumn
                            (GetAngle "\nDirection Of Column: " ColumnBasePoint)))
                ((eq (FSLetter CType) "CU")
                     (SetQ LengthOfColumn (/ AreaConcrete Widthofcolumn)
                           DirectionOfColumn
                            (GetAngle "\nDirection Of Column: " ColumnBasePoint)))
                ((eq (FLetter CType) "S")
                     (SetQ LengthOfColumn (SqRt AreaConcrete)
                           DirectionOfColumn 0.00
                     )
                )
                ((eq (FSLetter CType) "CI")
                     (SetQ LengthOfColumn (SqRt (/ AreaConcrete PI))
                           DirectionOfColumn 0.00
                     )
                )
                ((eq (FLetter CType) "H")
                     (SetQ LengthOfColumn (* (SqRt AreaConcrete ) 1.0746)
                           DirectionOfColumn 0.00
                     )
                )
                ((eq (FLetter CType) "O")
                     (SetQ LengthOfColumn (* (SqRt AreaConcrete ) 1.09897)
                           DirectionOfColumn 0.00
                     )
                )
        )
        OldLengthOfColumn LengthOfColumn
        LengthOfColumn (TenInt LengthOfColumn)
        CG  (Polar ColumnBasePoint DirectionOfColumn (/ (- (/ LengthOfColumn 2) 10.0) 100.0))

        ColumnName (NameOfColumn)
)
)

;***************>
;--------------------------------  Foundation  -------------------------------|
;Foundation Calculation Without using PC
(DeFun CalculationOfFoundation1 ()
 (SetQ
        OldAreaRC  (/ (* F 1.1) StressOfSoil)
        LengthOfFoundation1
             (/ (+ (- WidthOfColumn ThicknessOfPC)
                   (SqRt (+ (* (- ThicknessOfPC WidthOfColumn)
                               (- ThicknessOfPC WidthOfColumn)
                            )
                            (* 4 OldAreaRC)
                          )
                   )
                 )
                 2
              )
        LengthOfFoundation2
             (/ (- (- WidthOfColumn ThicknessOfPC)
                   (SqRt (+ (* (- ThicknessOfPC WidthOfColumn)
                               (- ThicknessOfPC WidthOfColumn)
                            )
                            (* 4 OldAreaRC)
                          )
                   )
                 )
                 2
              )
                ;Dimensions of Renforced Concrete Foundation
        OldLengthOfFoundationRC (Max LengthOfFoundation1 LengthOfFoundation2)
        LengthOfFoundationRC    (TenInt OldLengthOfFoundationRC)
        WidthOfFoundationRC     (+ LengthOfFoundationRC (- ThicknessOfPC WidthOfColumn))
        AreaRC                  (* LengthOfFoundationRC WidthOfFoundationRC)
        WidthOfFoundationPC   (+ ThicknessOfPC ThicknessOfPC WidthOfFoundationRC)
        LengthOfFoundationPC  (+ ThicknessOfPC ThicknessOfPC LengthOfFoundationRC)
 )
(PBoxCenter CG (/ LengthOfFoundationRC 100.0) (/ WidthOfFoundationRC 100.0))
(CgangeLastToHidden)
)

;***************>
;Foundation Calculation Using PC
(DeFun CalculationOfFoundation2 ()
 (SetQ
        OldAreaPC  (/ (* F 1.1) StressOfSoil)
        LengthOfFoundation1
             (/ (+ (- WidthOfColumn ThicknessOfPC)
                   (SqRt (+ (* (- ThicknessOfPC WidthOfColumn)
                               (- ThicknessOfPC WidthOfColumn)
                            )
                            (* 4 OldAreaPC)
                          )
                   )
                 )
                 2
              )
        LengthOfFoundation2
             (/ (- (- WidthOfColumn ThicknessOfPC)
                   (SqRt (+ (* (- ThicknessOfPC WidthOfColumn)
                               (- ThicknessOfPC WidthOfColumn)
                            )
                            (* 4 OldAreaPC)
                          )
                   )
                 )
                 2
              )
                ;Dimensions of Plane Concrete Foundation
        OldLengthOfFoundationPC (Max LengthOfFoundation1 LengthOfFoundation2)
                ;Dimensions of Renforced Concrete Foundation
        OldLengthOfFoundationRC (- OldLengthOfFoundationPC (* 2 ThicknessOfPC))

        LengthOfFoundationPC       (TenInt OldLengthOfFoundationPC)
        LengthOfFoundationRC       (TenInt OldLengthOfFoundationRC)
        WidthOfFoundationPC  (+ LengthOfFoundationPC (- ThicknessOfPC WidthOfColumn))
        WidthOfFoundationRC  (- WidthOfFoundationPC  (* 2 ThicknessOfPC))
        AreaRC                  (* LengthOfFoundationRC WidthOfFoundationRC)
        AreaPC                  (* LengthOfFoundationPC WidthOfFoundationPC)

 )
(PBoxCenter CG (/ LengthOfFoundationRC 100.0) (/ WidthOfFoundationRC 100.0))
(CgangeLastToHidden)
(PBoxCenter CG (/ LengthOfFoundationPC 100.0) (/ WidthOfFoundationPC 100.0))
(CgangeLastToHidden)
)

;--------------------------------  Functions  -------------------------------|
;*---------------->
(DeFun TypeOfUsing ()
      (SetQ Type (GetString "\nType of Using Resid/Office/Shop/Garag/Life Load Kg/m2: "))
        (SetQ LifeLoad
           (cond
                ((= (FLetter Type) "R")   (SetQ LifeLoad 200.0))
                ((= (FLetter Type) "O")   (SetQ LifeLoad 300.0))
                ((= (FLetter Type) "S")   (SetQ LifeLoad 400.0))
                ((= (FLetter Type) "G")   (SetQ LifeLoad 750.0))
                (SetQ LifeLoad (atof Type))
            )
         )
)
;*---------------->
(DeFun Omega ()
        (Cond
               ((>= 15.0 (/ HeightOfColumn WidthOfColumn))   ; Short Column
                (SetQ Omg 1.0))
                                    ;else Long  Column
                ((< 15.0 (/ HeightOfColumn WidthOfColumn))
                (SetQ Omg (- 1.0 (* 0.04 (- (/ HeightOfColumn WidthOfColumn) 15.0)))))
        )
)
;*---------------->
(DeFun ColumnType ()
(InitGet (+ 2 4))

        (SetQ CType
         (InputKWord "\nColumn Type  Rect/Square/CIrcle/Hex/Oct/CUrve "
           CType "Rect Square CIrcle Hex Oct CUrve"))
        (cond
                ((eq (FLetter CType) "R")
                 (SetQ
                     WidthOfColumn (InputMinMax "\nWidth of column cm " WidthOfColumn  20.0 500.0)
                     Omg   (Omega)
                 )
                )
                ((eq (FSLetter CType) "CU")
                 (SetQ
                     WidthOfColumn (InputMinMax "\nWidth of column cm " WidthOfColumn  20.0 500.0)
                     Omg   (Omega)
                 )
                )
                ((eq (FLetter CType) "S")  (SetQ Omg   1.0))
                ((eq (FSLetter CType) "CI") (SetQ Omg   1.0))
                ((eq (FLetter CType) "H")  (SetQ Omg   1.0))
                ((eq (FLetter CType) "O")  (SetQ Omg   1.0))
         )
)
;*---------------->
(DeFun NameOfColumn ()
  (SetQ PreFix
        (cond
                ((Or
                   (eq (FLetter CType) "R")
                   (eq (FSLetter CType) "CU")
                 )
                 (SetQ PreFix (StrCat (ItoA (Fix (/ WidthOfColumn 10.0)))
                                      (ItoA (Fix (/ (TenInt LengthOfColumn) 10.0)))
                               )
                 )
                )
                ((Or  (eq (FLetter CType) "S")   (eq (FSLetter CType) "CI")
                      (eq (FLetter CType) "H")   (eq (FLetter CType) "O")
                 )
                 (SetQ PreFix         (ItoA (Fix (/ (TenInt LengthOfColumn) 10.0))))
                )
         )
   )
  (SetQ ColumnName (StrCat "Col" CType PreFix))
)

;*---------------->
(DeFun InsertColumn ()
        (command "INSERT" "c:\\acad-lib\\civil\\civil\\c20100" ColumnBasePoint "1" "1" "0"
        AreaSteel AreaConcrete W)
  (Princ ColumnName)
        (command "Rotate" "l" "" ColumnBasePoint)

)
;--------------------------  General Functions  -----------------------------|
;***************>       Update the number to the next tens 46.5 >> 50.0
(DeFun TenInt (LastLength / NewLength)
        (SetQ NewLength (Float (* 10 (Fix (/ LastLength 10.0)))))
        (If  (/= NewLength LastLength )
             (SetQ NewLength (+ 10.0 NewLength))
             (SetQ NewLength NewLength)
         )
)
;***************>       Update the number to the next even 46.5 >> 6.0
(DeFun EvenInt (LastLength / NewLength)
        (SetQ NewLength (Float (* 2 (Fix (/ LastLength 2.0)))))
        (If  (/= NewLength LastLength )
             (SetQ NewLength (+ 2.0 NewLength))
             (SetQ NewLength NewLength)
         )
)
;***************>       Return First letter if string in capital
(DeFun FLetter (String /)
  (SetQ FirstLetter (SubStr (StrCase String) 1 1))
)
;***************>       Return First and second letter if string in capital
(DeFun FSLetter (String /)
  (SetQ FirstLetter (SubStr (StrCase String) 1 2))
)
;***************>       Print New Line
(DeFun NewLine ()
(Princ "\n")
)
;***************>       Radian To Degree Converter
(DeFun RtoD (D)
        (/ (* D 180.0) PI)
)
;***************>       Input With Min & Max limits
(DeFun InputMinMax (Text Default Minimum Maximum)
        (SetQ InputData -1000000000.0)

        (While (Or
                    (< InputData Minimum)
                    (> InputData Maximum)
               )
               (Progn
                (Setq InputData (GetReal (StrCat Text "<" (RtoS Default) ">:")))
                (If (Null InputData) (SetQ InputData Default))
                (If (< InputData Minimum)
                    (Princ
                    (StrCat "\nValue must not less than " (RtoS Minimum) " Try Again :")
                    )
                )
                (If (> InputData Maximum)
                    (Princ
                    (StrCat "\nValue must not exceed " (RtoS Maximum) " Try Again:")
                    )
                )
               )
        )
(SetQ InputData InputData)
)
;***************>       Input Key Word With Default
(DeFun InputKWord (Text Default Options)
        (InitGet Options)
        (SetQ X -1000000000.0)
        (SetQ X (GetKWord (StrCat Text "<"  Default ">:")))
        (If (Null X) (Setq X Default ))
        (InitGet (+ 2 4))
        (Setq X X)
)



;***************>       Pbox.lsp  2.5   p.720     Draw Box From 2 Corners
(DeFun pbox (FirstCorner SecondCorner /)
    (command "pline"
                FirstCorner
                ".x" SecondCorner
                ".y" FirstCorner
                SecondCorner
                ".x" FirstCorner
                ".y" SecondCorner "c")
(Princ)
)
;***************>       Draw Box From Center  Corners
(DeFun PBoxCenter (CenterOfBox XDist YDist / HI LO X1 X2 X3 X4)
(SetQ
        XDist (/ XDist 2.0)
        YDist (/ YDist 2.0)
        HI (POLAR CenterOfBox (* PI 0.5) YDist)
        LO (POLAR CenterOfBox (* PI 1.5) YDist)
        X1 (POLAR HI 0  XDist)
        X2 (POLAR LO 0  XDist)
        X3 (POLAR LO PI XDist)
        X4 (POLAR HI PI XDist)
)
(command "pLINE" X1 X2 X3 X4 "C")
(Princ)
)      
;***************>       Draw 2 Straight Paralel lines
;(c) Alaa AbdelWahab ,Jeddah
;Last update 17 Nov. 89

(defun STRAIGHT()    ;<<<<<<<<<<<<<< To be Update <<<<<<<<<<<<
(SETQ WW 0.1)
 (SETQ  PT1 (GETPOINT "\nFirst point: ")
        PT2 (GETPOINT "\nEnd point: " pt1)
        A (ANGLE PT1 PT2)
        X1 (POLAR PT1 (+ A (/ PI 2)) WW)
        X2 (POLAR PT2 (+ A (/ PI 2)) WW)
        X3 (POLAR PT2 (+ A (* PI 1.5)) WW)
        X4 (POLAR PT1 (+ A (* PI 1.5)) WW)
 )
 (command "LINE" X1 X2 "")
 (command "LINE" X4 X3 "")
 (princ)
)


;***************>       Cgange Last To Hidden
(DeFun CgangeLastToHidden ()
        (Command "Change" "L" "" "P" "LT" "Hidden" "")
)
;***************>       Print Data
(DeFun c:Data ()
                              (NewLine)
(Princ  "  LifeLoad : ")                (Princ LifeLoad)
                              (NewLine)
(Princ  "  DeadLoad : ")                (Princ DeadLoad)
                              (NewLine)
(Princ  "  HeightOfColumn : ")          (Princ HeightOfColumn)
                              (NewLine)
(Princ  "  CubeStrengthOfConcrete28 : ")  (Princ CubeStrengthOfConcrete28)
                              (NewLine)
(Princ  "  StressOfSteel  : ")          (Princ StressOfSteel)
                              (NewLine)
(Princ  "  %OfSteel       : ")          (Princ %OfSteel)
                              (NewLine)
(Princ  "  NoOfFloors     : ")          (Princ NoOfFloors)
                              (NewLine)
(Princ  "  StressOfSoil   : ")          (Princ StressOfSoil)
                              (NewLine)
(Princ  "  ThicknessOfPC  : ")          (Princ ThicknessOfPC)
                              (NewLine)
(Princ  "  PlaneConcreteFoundation  : ")  (Princ PlaneConcreteFoundation)
                              (NewLine)
(Princ  "  SpanRight : ")               (Princ SpanRight)
(Princ  "  SpanLift  : ")               (Princ SpanLift)
(Princ  "  SpanUp    : ")               (Princ SpanUp)
(Princ  "  SpanDown  : ")               (Princ SpanDown)
                              (NewLine)
(Princ  "  Column    : ")               (Princ Column)
(Princ  "  Area      : ")               (Princ Area)
                              (NewLine)
(Princ  "  W         : ")               (Princ W)
                              (NewLine)
(Princ  "  F         : ")               (Princ F)
(Princ  "  FConcrete : ")               (Princ FConcrete)
                              (NewLine)
(Princ  "  AreaConcrete : ")            (Princ AreaConcrete)
(Princ  "  AreaSteel    : ")            (Princ AreaSteel)
                              (NewLine)

(Princ  "  AreaRC       : ")            (Princ OldAreaRC )
(Princ  "  >>  ")                       (Princ    AreaRC )
(If  (= (FLetter PlaneConcreteFoundation) "Y")
        (progn
(Princ  "  AreaPC       : ")            (Princ OldAreaPC )
(Princ  "  >>  ")                       (Princ    AreaPC )
        )
)
                              (NewLine)
(Princ  "  LengthOfFoundationRC    : ") (Princ OldLengthOfFoundationRC)
(Princ  "  >>  ")                       (Princ    LengthOfFoundationRC)
(Princ  "  WidthOfFoundationRC     : ") (Princ WidthOfFoundationRC)
                              (NewLine)
(Princ  "  LengthOfFoundationPC    : ") (Princ OldLengthOfFoundationPC)
(Princ  "  >>  ")                       (Princ    LengthOfFoundationPC)
(Princ  "  WidthOfFoundationPC     : ") (Princ WidthOfFoundationPC)
                              (NewLine)
(Princ  "  Type : ")                    (Princ Type)
                              (NewLine)
(Princ  "  LengthOfColumn : ")          (Princ OldLengthOfColumn)
(Princ  "  >>  ")                       (Princ LengthOfColumn)
                              (NewLine)
(Princ  "  ColumnName        : ")       (Princ ColumnName)
(Princ)
)

;>>>>>>>>>>>>>>>>>>>>>> Main Program <<<<<<<<<<<<<<<<<<<<<<#############
(DeFun c:Column ()
(while (Not SetDefaultStructuralData)
 (Load"c:\\acad-lib\\civil\\civil\\DfStrDat")    ;<<<<<
 (DefaultStructuralData)    ;<<<<<
 (SetQ DefaultStructuralData Nil)
)
(while (Not StrucTuralData)
 (Load"c:\\acad-lib\\civil\\civil\\InpStrDt")    ;<<<<<
 (InputStrucTuralData)    ;<<<<<
 (SetQ InputStrucTuralData Nil)    ;<<<<<
    (SetQ ColNumber 0)
    (SetQ StartSchCol (GetPoint "Schedule Start Point : "))
    (SetQ StartSchFot (Polar StartSchCol 0 10))
(Command "Insert"  "c:\\acad-lib\\civil\\civil\\SchHdCol" StartSchCol "1" "1" "0" )
(Command "Insert"  "c:\\acad-lib\\civil\\civil\\SchHdFot" StartSchFot "1" "1" "0" )
)
(SetQ StartSchCol (Polar StartSchCol (/ (* 3 Pi) 2)  1))
(SetQ StartSchFot (Polar StartSchFot (/ (* 3 Pi) 2)  1))
(SetQ ColNumber (+ ColNumber 1))
 (InputColumnData)        ;<<<<<
 (CalculationOfColumn)    ;<<<<<

(ColumnArea)
;(SetQ *error* olderr)
(If  (= (FLetter PlaneConcreteFoundation) "Y")
        (CalculationOfFoundation2)
        (CalculationOfFoundation1)
)

(PBoxCenter CG (/ LengthOfColumn 100.0) (/ WidthOfColumn 100.0))
(Command "Rotate" "l" "" CG (RtoD DirectionOfColumn))
(Command "Hatch"  "ANsi31" "0.5" "0"   "l" "")

(SetQ StrColNumber (StrCat "C" (ItoA ColNumber)))
(SetQ StrFotNumber (StrCat "F" (ItoA ColNumber)))
(SetQ ColBarDiameter
    (InputMinMax "\nSelect bar diameter for column : " ColBarDiameter 8.0 38.0)
)
(SetQ FotBarDiameter
    (InputMinMax "\nSelect bar diameter for footing: " FotBarDiameter 8.0 38.0)
)
(SetQ ColBarNo (Fix (EvenInt
                 (Max 4.0
                   (/
                     (* 4.0 AreaSteel)
                     (/ (* PI ColBarDiameter ColBarDiameter) 100.0)
                   )
                 )
               ))
)

(Load"c:\\acad-lib\\civil\\civil\\FotCalc")
(FootCalculation)
(SetQ FootCalculation Nil)
     ;; Column table Insertion
(Command "Insert"  "c:\\acad-lib\\civil\\civil\\SchCol" StartSchCol "1" "1" "0"
 StrColNumber   (Fix LengthOfColumn)  (Fix WidthOfColumn)
 (Fix ColBarDiameter) ColBarNo
)
 (SetQ
        ColumnTextPoint (Polar ColumnBasePoint (* PI 0.75) 0.5)
        FootTextPoint   (Polar ColumnBasePoint (* PI 0.75) 1.8)
 )
(Command "Text"  ColumnTextPoint   "0.2" "" StrColNumber)
(Command "Text"  FootTextPoint   "0.2" "" StrFotNumber)
     ;; Footing table Insertion
(Command "Insert"  "c:\\acad-lib\\civil\\civil\\SchFoot" StartSchFot "1" "1" "0"
StrFotNumber
 (Fix LengthOfFoundationPC) (Fix WidthOfFoundationPC)   (Fix ThicknessOfPC)
 (Fix LengthOfFoundationRC) (Fix WidthOfFoundationRC)   (Fix t1)
 (Fix FotBarDiameter)  (Fix NA) (Fix FotBarDiameter) (Fix NB)
)
 ;(InsertColumn)           ;<<<<<
(Princ)
)
;***************

