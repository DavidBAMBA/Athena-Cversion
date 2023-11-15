#!/bin/bash

# Directorio de salida para los archivos combinados
output_dir="output_combined"

# Crear directorio de salida si no existe
mkdir -p "$output_dir"

# Número total de archivos a combinar
total_files=194  # Ajusta esto según la cantidad real de archivos

# Ruta al programa join_vtk
join_vtk="./a.out"

# Bucle para combinar los archivos
for ((file_number=0; file_number<=total_files; file_number++)); do
    file_index=$(printf "%04d" $file_number)  # Genera el número con ceros a la izquierda

    # Lista temporal para guardar los nombres de archivos a combinar
    temp_file_list=()

    # Primero, añadir el archivo de id0 que tiene un formato diferente
    file_id0="id0/2Dks.${file_index}.d.vtk"
    if [ -f "$file_id0" ]; then
        temp_file_list+=("$file_id0")
    fi

    # Ahora, añadir los otros archivos que siguen un patrón diferente
    for ((dir_num=1; dir_num<=15; dir_num++)); do
        file="id${dir_num}/2Dks-id${dir_num}.${file_index}.d.vtk"
        if [ -f "$file" ]; then
            temp_file_list+=("$file")
        fi
    done

    # Verificar si hay archivos para combinar
    if [ ${#temp_file_list[@]} -ne 0 ]; then
        # Ejecutar join_vtk para combinar los archivos de este paso de tiempo
        $join_vtk -o "${output_dir}/combined_${file_index}.vtk" "${temp_file_list[@]}"
    fi
done

