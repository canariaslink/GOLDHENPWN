import zlib
import os

# Obtener el directorio de trabajo actual
current_dir = os.getcwd()

# Nombres de los archivos
input_file_name = "goldhen.bin"  # Nombre del archivo original
output_elf_name = "decompressed_elf.bin"  # Nombre para guardar el ELF descomprimido
modified_elf_name = "modified_elf.bin"  # Nombre del ELF modificado
output_file_name = "recomposed_file.bin"  # Nombre para guardar el archivo recompuesto
elf_section_name = "extracted_elf_section.bin"  # Nombre para guardar la sección ELF extraída
compressed_size_file_name = "compressed_size.txt"  # Archivo para guardar el tamaño comprimido

# Rutas completas de los archivos
input_file_path = os.path.join(current_dir, input_file_name)
output_elf_path = os.path.join(current_dir, output_elf_name)
modified_elf_path = os.path.join(current_dir, modified_elf_name)
output_file_path = os.path.join(current_dir, output_file_name)
elf_section_path = os.path.join(current_dir, elf_section_name)
compressed_size_file_path = os.path.join(current_dir, compressed_size_file_name)

# Offsets de las secciones
compressed_section_offset = 0x2D20
elf_section_offset = 0x3525C

# Función para descomponer el archivo original y extraer la sección ELF
def descomponer_archivo():
    with open(input_file_path, "rb") as file:
        # Leer la parte anterior a la sección comprimida
        header_data = file.read(compressed_section_offset)
        # Leer la sección comprimida completa desde el offset
        file.seek(compressed_section_offset)
        compressed_data = file.read(elf_section_offset - compressed_section_offset)

        # Mover el puntero al inicio de la sección ELF
        file.seek(elf_section_offset)
        # Leer la sección ELF hasta el final del archivo
        elf_section_data = file.read()

        try:
            # Descomprimir los datos desde el offset comprimido hasta el final del archivo
            decompressed_data = zlib.decompress(compressed_data)
            # Guardar el ELF descomprimido
            with open(output_elf_path, "wb") as elf_file:
                elf_file.write(decompressed_data)
            print(f"Archivo ELF descomprimido guardado en: {output_elf_path}")

            # Guardar la sección ELF extraída
            with open(elf_section_path, "wb") as elf_section_file:
                elf_section_file.write(elf_section_data)
            print(f"Sección ELF extraída guardada en: {elf_section_path}")

            # Guardar el tamaño de la sección comprimida
            compressed_size = len(compressed_data)
            with open(compressed_size_file_name, "w") as size_file:
                size_file.write(str(compressed_size))
            print(f"Tamaño de la sección comprimida guardado en: {compressed_size_file_name}")
        except Exception as e:
            print(f"Error al descomprimir los datos: {e}")

# Función para recomponer el archivo original después de modificar la sección ELF
def recomponer_archivo():
    try:
        # Leer el ELF modificado
        with open(modified_elf_path, "rb") as modified_elf:
            modified_data = modified_elf.read()

        # Crear un objeto de compresión con el nivel de mejor compresión `zlib.Z_BEST_COMPRESSION`
        # Usamos `wbits=15` para la compresión estándar que generará `78 9C`
        compressor = zlib.compressobj(level=zlib.Z_BEST_COMPRESSION, wbits=15)
        compressed_modified_data = compressor.compress(modified_data) + compressor.flush()

        # Verificar el encabezado de la compresión
        if compressed_modified_data[:2] != b'\x78\x9C':
            print("Advertencia: La compresión no ha producido el encabezado esperado `78 9C`.")

        # Leer la sección ELF extraída
        with open(elf_section_path, "rb") as elf_section_file:
            elf_section_data = elf_section_file.read()

        # Leer el tamaño de la sección comprimida original
        with open(compressed_size_file_name, "r") as size_file:
            original_compressed_data_size = int(size_file.read())

        # Leer el archivo original completo
        with open(input_file_path, "rb") as original_file:
            original_data = original_file.read()

        # Crear el archivo recompuesto
        with open(output_file_path, "wb") as output_file:
            # Escribir la parte anterior al offset (datos intactos)
            output_file.write(original_data[:compressed_section_offset])
            # Escribir la nueva sección comprimida
            output_file.write(compressed_modified_data)
            # Escribir la parte posterior al offset hasta el inicio de la sección ELF
            output_file.write(original_data[compressed_section_offset + original_compressed_data_size:elf_section_offset])
            # Añadir la sección ELF
            output_file.write(elf_section_data)

        print(f"Archivo recompuesto guardado en: {output_file_path}")
    except Exception as e:
        print(f"Error al recomponer los datos: {e}")

# Menú de opciones para el usuario
def main():
    print("Elige una opción:")
    print("1. Descomponer el archivo (extraer y descomprimir el ELF y extraer la sección ELF)")
    print("2. Recomponer el archivo (comprimir y reinsertar el ELF modificado y añadir la sección ELF)")
    opcion = input("Ingresa el número de la opción deseada: ")

    if opcion == "1":
        descomponer_archivo()
    elif opcion == "2":
        recomponer_archivo()
    else:
        print("Opción no válida. Por favor, elige 1 o 2.")

if __name__ == "__main__":
    main()
