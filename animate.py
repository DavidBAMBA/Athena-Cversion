# visit -cli -s animate.py

def SaveFrames():
    SetTimeSliderState(0)
    num_states = TimeSliderGetNStates()
    for state in range(num_states):
        SetTimeSliderState(state)
        DrawPlots()
        SaveWindowAttributes.swa = SaveWindowAttributes()
        SaveWindowAttributes.swa.family = 0
        SaveWindowAttributes.swa.format = SaveWindowAttributes.PNG
        SaveWindowAttributes.swa.fileName = "frame_%04d.png" % state
        SaveWindow(SaveWindowAttributes.swa)

# Main execution
vtk_file_path = "/home/yo/Documents/Athena-Cversion/bin/rt.0030.vtk"
OpenDatabase(vtk_file_path)  # Adjust your file path/pattern
AddPlot("Pseudocolor", "VariableName")  # Replace with your variable
DrawPlots()
SaveFrames()
