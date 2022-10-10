;******************> InputStructuralData InpStrDt.lsp
(DeFun InputStructuralData ()
(InitGet (+ 2 4))
(SetQ
        LifeLoad
          (TypeOfUsing)
        DeadLoad
          (InputMinMax "\nDead Load Kg/m2 " DeadLoad 0.00 5000.0)
         ;Walls + Partitions <500> Par
        Par 500.00
        HeightOfColumn
          (InputMinMax "\nHeight of columns in cm "  HeightOfColumn 200.00 1500.0)
        CubeStrengthOfConcrete28
          (InputMinMax "\nCube strength of concrete C28 Kg/cm2 " CubeStrengthOfConcrete28 150.00 700.0)
        StressOfSteel
          (InputMinMax "\nStress of steel  Kg/cm2 " StressOfSteel 1000.00 3000.0)
        %OfSteel
          (InputMinMax "\n% of steal  u " %OfSteel 0.40 6.0)
        NoOfFloors
          (InputMinMax "\nNo. of floors " NoOfFloors  1.00 20.0)
        StressOfSoil
          (InputMinMax "\nStress of soil  Kg/cm2 " StressOfSoil 0.10 10.0)
        ThicknessOfPC
          (InputMinMax "\nThickness Of Plane Concrete of Foundation cm " ThicknessOfPC 10.00 60.0)
        PlaneConcreteFoundation
          (InputKWord "\nPlane concrete in foundation : "  "Yes" "Yes No")
        StructuralData 1
)
(InitGet (+ 2 4))
)
