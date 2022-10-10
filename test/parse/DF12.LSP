;Door insertion in a wall
;[  DO  ]

(defun setting()
  (setq oldblip (getvar "BLIPMODE")
        oldcmd  (getvar "CMDECHO" )
;        oldpb   (getvar "PICKBOX" )
        CLAYER (GETVAR "CLAYER")
        ALAA  (GETVAR "OSMODE")
        )
   (setvar "CMDECHO" 0)
;   (setvar "PICKBOX" 0)
   (setvar "BLIPMODE" 0)
   (SETVAR "OSMODE" 512)
)

(defun resetting()
   (setvar "BLIPMODE"  oldblip )
;   (setvar "PICKBOX"  oldpb    )
   (setvar "CMDECHO" oldcmd    )
   (SETVAR "OSMODE"  ALAA )
 (command "LAYER" "s"  CLAYER "")
)


(defun Get4()
 (SETQ
      Point3 (GETPOINT "\nInsertion point :")
      Angle2 (GETANGLE Point3 "\nDirection of oppining : ")
      Point4 (polar Point3 Angle2 (/ (atof width) 100.0 ))
 )
); End Get2Points

(defun break4()
 (SETQ
      X5 (POLAR Point3 (+ Angle2 (/ PI 2)) 0.06)
      X6 (POLAR Point4 (+ Angle2 (/ PI 2)) 0.06)
      X7 (POLAR Point4 (+ Angle2 (* PI 1.5)) 0.06)
      X8 (POLAR Point3 (+ Angle2 (* PI 1.5)) 0.06))
 (COMMAND "LAYER" "M" "WALL" "S" "WALL" "C" "2" "" "")
  (command "BREAK" X5 X6)
  (command "BREAK" X8 X7)
  (command "LINE" X5 X8 "")
  (command "LINE" X6 X7 "")
);End break

(defun Insert4()
 (setq
   mirror (- (GETANGLE Point3 "\nDirection of inside : ") Angle2)
 )
 (command "layer" "M" "DOOR" "S" "DOOR" "C" "5" "" "")
 (if (OR
        (AND (< mirror 3.1415) (> mirror 0.0) )
        (< mirror -3.1415)
     )
        (setq YFactor -1)
        (setq YFactor 1)
  )
(command "insert" i Point3 "1" YFactor
   (/ (* 180 (angle Point4 Point3)) pi))
);End Insert

; Main Rotine
(defun c:df12()
 (setting)
 (Get4)
 (break4)
        (setq i (strcat "c:\\Acad-Lib\\DOOR\\DoorPlan\\wall12\\folding\\df12" width))
 (Insert4)
 (resetting)
); END df12.LSP
