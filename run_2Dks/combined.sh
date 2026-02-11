#!/bin/bash

# Script para combinar archivos VTK de Athena MPI
# Uso: ./combined.sh <variable>
# Ejemplo: ./combined.sh d

var=${1:-d}
output_dir="output_combined-${var}"

# Crear directorio de salida
mkdir -p "$output_dir"

# Ruta al programa join_vtk
join_vtk="/home/davidbamba/repositories/Athena-Cversion/vis/vtk/join_vtk"

# Detectar automáticamente el número de snapshots
total_files=$(ls id0/*.${var}.vtk 2>/dev/null | wc -l)
if [ "$total_files" -eq 0 ]; then
    echo "Error: No se encontraron archivos *.${var}.vtk en id0/"
    exit 1
fi
total_files=$((total_files - 1))  # índice empieza en 0

echo "=========================================="
echo "Combinando archivos VTK de Athena"
echo "=========================================="
echo "Variable: $var"
echo "Snapshots: 0 a $total_files"
echo "Salida: $output_dir/"
echo ""

# Bucle para combinar los archivos
for ((file_number=0; file_number<=total_files; file_number++)); do
    file_index=$(printf "%04d" $file_number)

    # Lista de archivos a combinar
    temp_file_list=()

    # Archivo de id0 (formato diferente)
    file_id0="id0/2Dks.${file_index}.${var}.vtk"
    if [ -f "$file_id0" ]; then
        temp_file_list+=("$file_id0")
    fi

    # Archivos de id1 a id31
    for ((dir_num=1; dir_num<=31; dir_num++)); do
        file="id${dir_num}/2Dks-id${dir_num}.${file_index}.${var}.vtk"
        if [ -f "$file" ]; then
            temp_file_list+=("$file")
        fi
    done

    # Combinar si hay archivos
    if [ ${#temp_file_list[@]} -gt 0 ]; then
        echo -ne "\rProcesando snapshot $file_index (${#temp_file_list[@]} subdominios)..."
        $join_vtk -o "${output_dir}/2Dks_${var}_${file_index}.vtk" "${temp_file_list[@]}" > /dev/null 2>&1
    fi
done

echo -e "\n"
echo "=========================================="
echo "Listo! Archivos en: $output_dir/"
echo "=========================================="
ls -lh "$output_dir/" | head -10
