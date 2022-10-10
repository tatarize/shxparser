;;;; Calculation of footing     FotCalc.Lsp
(DeFun FootCalculation()
  (If  (= (FLetter PlaneConcreteFoundation) "Y")
        (SetQ M_dd ThicknessOfPC)
        (SetQ M_dd 0.0)
  )
  (SetQ ColumnLoad (+ DeadLoad LifeLoad)
      tc LengthOfColumn
      bc WidthOfColumn
      x  (- LengthOfColumn  WidthOfColumn)
      y  (/ (* 1100.0 ColumnLoad) StressOfSoil)
      b  (/ (+
              (- 0.0 x)
              (Sqrt (+ (* x x) (* 4 y)))
            )
          2.0
         )
      a  (+ b x)
      a1 (- A (* 2.0  M_dd))
      b1 (- b (* 2.0  M_dd))
      pn (/ (* 11000 ColumnLoad) (* a1 b1))
      v  (/ (* pn a1 (* 0.85 (- b1 bc))) 10000.0)
      v  (/ 10000 (* pn a1 (* 0.85 (- b1 bc))))     ;; error
      m  (* pn 0.010625 (- b1 bc) (- b1 bc))
      fw (* 0.24 FConcrete)
      t  (/ (* 15.0  fw) StressOfSteel)
      k  (/ t (+ t 1.0))
      j  (- 1.0 (/ k 3.0))
      d1 (Sqrt (/ m (* 0.5 k j fw)))
      aa (* 1.7 (Sqrt (* 0.85 FConcrete  )))    ; recheck FC later on
      bb (* 0.85 (+ bc tc) (Sqrt (* 0.85 FConcrete  )))
      d2 (/ (+ (- 0.0 bb)
               (Sqrt (* bb bb))
               (* 4.0 aa v 1000.0)
            )
          (* 2.0 aa)
         )
      d  (Max d1 d2)
      t1 (+ d 5.0)     ;ThickNess of renforced concrete
      C (* 0.85 (Sqrt (* 0.85 FConcrete)))
      AS (/ (* M  100.0) (* J D StressOfSteel))
      N1 (/ (* 4.0 AS )  (* 3.14 FotBarDiameter FotBarDiameter))
      N2 (/ (* V 100000.0) (* 6.2857 FotBarDiameter D C A1))
      N  (Max N1 N2)
      A  (+ A1 (* 2.0 ThicknessOfPC))
      B  (+ B1 (* 2.0 ThicknessOfPC))
      NA (* N A1 0.01)     ;No Of Bar in main direction
      NB (* N B1 0.01)     ;No Of Bar in sec. direction
  )
)

