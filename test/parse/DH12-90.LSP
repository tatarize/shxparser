;Door insertion in a wall
;[  Dh12-90  ]

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


(defun Get1()
 (SETQ
      Point1 (GETPOINT "\nInsertion point :")
      Angle1 (GETANGLE Point1 "\nDirection of oppining : ")
      Point2 (polar Point1 Angle1 (/ (atof width) 100.0 ))
 )
); End Get2Points

(defun break1()
 (SETQ
      X1 (POLAR Point1 (+ Angle1 (/ Pi 2)) 0.06)
      X2 (POLAR Point2 (+ Angle1 (/ Pi 2)) 0.06)
      x3 (POLAR Point2 (+ Angle1 (* Pi 1.5)) 0.06)
      X4 (POLAR Point1 (+ Angle1 (* Pi 1.5)) 0.06))
 (COMMAND "LAYER" "M" "WALL" "S" "WALL" "C" "2" "" "")
 (command "BREAK" X1 X2)
 (command "BREAK" X4 X3)
 (command "LINE" X1 X4 "")
 (command "LINE" X2 X3 "")
);End break

(defun Insert1()
 (setq
   mirror (- (GETANGLE Point1 "\nDirection of inside : ") Angle1)
 )
 (command "layer" "M" "DOOR" "S" "DOOR" "C" "5" "" "")
 (if (OR
        (AND (< mirror 3.1415) (> mirror 0.0) )
        (< mirror -3.1415)
     )
        (setq YFactor -1)
        (setq YFactor 1)
  )
(command "insert" i Point1 "1" YFactor
   (/ (* 180 (angle Point2 Point1)) pi))
);End Insert

; Main Rotine
(defun c:Dh12-90()
 (setting)
 (Get1)
 (break1)
        (setq i (strcat "c:\\Acad-Lib\\DOOR\\DoorPlan\\wall12\\hinged90\\dh12" width))
 (Insert1)
 (resetting)
); END DOOR.LSP
