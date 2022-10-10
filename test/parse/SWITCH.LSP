;Function To insert Electricity Sympols in 4 points in room
;(c) Alaa Abdel-Wahab 9.1.90
(defun c:Switch()
        (setq p1 (getpoint "\nFirst  Point: ")
              p2 (getpoint "\nSecond Point: ")
              p3 (getpoint "\nThird  Point: ")
              p4 (getpoint "\nForth  Point: ")
              C  (getpoint "\nCenter Point: ")
        )
        (command "insert" "*c:/library/elec/switch" p1  "" "0")
        (command "insert" "*c:/library/elec/switch" p2  "" "90")
        (command "insert" "*c:/library/elec/switch" p3  "" "180")
        (command "insert" "*c:/library/elec/switch" p4  "" "270")
        (command "insert" "c:/library/elec/Lamp" c "" "" "0")
        (command "LINE" c)
)


