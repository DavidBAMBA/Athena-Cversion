# Script de VisIt: visualize_isosurface.py

# Asume que tus archivos VTK están en una subcarpeta llamada "data" 
# en el directorio actual donde está el script. Cambia la ruta según sea necesario.
vtk_file_path = "/home/yo/Documents/Athena-Cversion/bin/rt.0030.vtk"

# Abre la base de datos VTK.
OpenDatabase(vtk_file_path)

# Agrega un gráfico de pseudocolor para la variable 'density'.
AddPlot("Pseudocolor", "density")
DrawPlots()

# Agrega un operador de isosuperficie.
AddOperator("Isosurface")

# Configura los atributos del operador de isosuperficie.
isosurface_atts = IsosurfaceAttributes()
isosurface_atts.contourMethod = isosurface_atts.Value  # Utiliza un valor constante para el contorno
isosurface_atts.contourValue = 5.0                     # Establece el valor del isosuperficie a 5.0
SetOperatorOptions(isosurface_atts)

# Dibuja los gráficos con el operador aplicado.
DrawPlots()

# Aquí puedes añadir comandos para rotar la vista si es necesario.

# Guarda la ventana a un archivo de imagen.
swa = SaveWindowAttributes()
swa.format = swa.PNG
swa.fileName = "isosurface_density"
swa.width = 1024
swa.height = 768
SetSaveWindowAttributes(swa)
SaveWindow()
