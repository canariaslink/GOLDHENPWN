import zlib
import os

# Obtener el directorio de trabajo actual
current_dir = os.getcwd()

# Nombres de los archivos
input_file_name = "goldhen.bin"  # Nombre del archivo original
output_elf_name = "decompressed_elf.bin"  # Nombre para guardar el ELF descomprimido
modified_elf_name = "modified_elf.bin"  # Nombre del ELF modificado
output_file_name = "recomposed_file.bin"  # Nombre para guardar el archivo recompuesto

# Rutas completas de los archivos
input_file_path = os.path.join(current_dir, input_file_name)
output_elf_path = os.path.join(current_dir, output_elf_name)
modified_elf_path = os.path.join(current_dir, modified_elf_name)
output_file_path = os.path.join(current_dir, output_file_name)

# Offset donde empieza la sección comprimida
offset = 0x2D20

# Función para descomponer el archivo original
def descomponer_archivo():
    with open(input_file_path, "rb") as file:
        file.seek(offset)
        compressed_data = file.read()
        
        try:
            # Descomprimir los datos
            decompressed_data = zlib.decompress(compressed_data)
            # Guardar el ELF descomprimido
            with open(output_elf_path, "wb") as elf_file:
                elf_file.write(decompressed_data)
            print(f"Archivo ELF descomprimido guardado en: {output_elf_path}")
        except Exception as e:
            print(f"Error al descomprimir los datos: {e}")

# Función para recomponer el archivo original
def recomponer_archivo():
    try:
        # Leer el ELF modificado
        with open(modified_elf_path, "rb") as modified_elf:
            modified_data = modified_elf.read()

        # Comprimir los datos modificados
        compressed_modified_data = zlib.compress(modified_data)

        # Leer el archivo original completo para obtener el tamaño de la sección comprimida original
        with open(input_file_path, "rb") as original_file:
            original_file.seek(offset)
            original_compressed_data_size = len(original_file.read())

        # Leer el archivo original completo para reinsertar los datos comprimidos modificados
        with open(input_file_path, "rb") as original_file:
            original_data = original_file.read()

        # Crear el archivo recompuesto con la sección modificada
        with open(output_file_path, "wb") as output_file:
            # Escribir la parte anterior al offset
            output_file.write(original_data[:offset])
            # Escribir la nueva sección comprimida
            output_file.write(compressed_modified_data)
            # Escribir la parte posterior al offset
            output_file.write(original_data[offset + original_compressed_data_size:])

        print(f"Archivo recompuesto guardado en: {output_file_path}")
    except Exception as e:
        print(f"Error al recomponer los datos: {e}")

# Menú de opciones para el usuario
def main():
    print("Elige una opción:")
    print("1. Descomponer el archivo (extraer y descomprimir el ELF)")
    print("2. Recomponer el archivo (comprimir y reinsertar el ELF modificado)")
    opcion = input("Ingresa el número de la opción deseada: ")

    if opcion == "1":
        descomponer_archivo()
    elif opcion == "2":
        recomponer_archivo()
    else:
        print("Opción no válida. Por favor, elige 1 o 2.")

if __name__ == "__main__":
    main()
