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

# Directorio para guardar los ELF extraídos
extracted_elf_dir = os.path.join(current_dir, "extracted_elf_files")
os.makedirs(extracted_elf_dir, exist_ok=True)

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
            with open(compressed_size_file_path, "w") as size_file:
                size_file.write(str(compressed_size))
            print(f"Tamaño de la sección comprimida guardado en: {compressed_size_file_name}")

            # Extraer múltiples ELF del archivo descomprimido
            extraer_multiples_elf(decompressed_file_path=output_elf_path, output_dir=extracted_elf_dir)

        except Exception as e:
            print(f"Error al descomprimir los datos: {e}")

# Función para encontrar todas las posiciones de cabeceras ELF
def encontrar_cabeceras_elf(path):
    cabecera_elf_64 = b'\x7f\x45\x4c\x46\x02'  # Bytes de la cabecera ELF para 64 bits
    cabecera_elf_32 = b'\x7f\x45\x4c\x46\x01'  # Bytes de la cabecera ELF para 32 bits
    posiciones = []
    with open(path, "rb") as file:
        data = file.read()
        offset = 0
        while True:
            # Buscar cabeceras ELF de 64 bits
            offset_64 = data.find(cabecera_elf_64, offset)
            # Buscar cabeceras ELF de 32 bits
            offset_32 = data.find(cabecera_elf_32, offset)
            
            # Tomar la más cercana
            if offset_64 == -1 and offset_32 == -1:
                break
            elif offset_64 != -1 and (offset_32 == -1 or offset_64 < offset_32):
                posiciones.append(offset_64)
                offset = offset_64 + 1
            else:
                posiciones.append(offset_32)
                offset = offset_32 + 1
    return posiciones

# Función para extraer ELF desde posiciones dadas
def extraer_elfs(path, posiciones, output_dir):
    with open(path, "rb") as file:
        data = file.read()
        for i, inicio in enumerate(posiciones):
            if i + 1 < len(posiciones):
                fin = posiciones[i + 1]
            else:
                fin = len(data)
            # Extraer y guardar el ELF
            elf_data = data[inicio:fin]
            output_path = os.path.join(output_dir, f"elf_{i}.bin")
            with open(output_path, "wb") as elf_file:
                elf_file.write(elf_data)
            print(f"ELF extraído guardado en: {output_path}")

# Función para extraer múltiples ELF de un archivo descomprimido
def extraer_multiples_elf(decompressed_file_path, output_dir):
    # Buscar todas las posiciones de cabeceras ELF en el archivo descomprimido
    posiciones_cabeceras = encontrar_cabeceras_elf(decompressed_file_path)
    print(f"Posiciones de cabeceras ELF encontradas: {posiciones_cabeceras}")

    # Extraer y guardar todos los ELF encontrados
    extraer_elfs(decompressed_file_path, posiciones_cabeceras, output_dir)

# Función para recomponer el archivo original después de modificar la sección ELF
def recomponer_archivo():
    try:
        # Leer el ELF modificado
        with open(modified_elf_path, "rb") as modified_elf:
            modified_data = modified_elf.read()

        # Crear un objeto de compresión con el nivel de mejor compresión `zlib.Z_BEST_COMPRESSION`
        compressor = zlib.compressobj(level=zlib.Z_BEST_COMPRESSION, wbits=15)
        compressed_modified_data = compressor.compress(modified_data) + compressor.flush()

        # Leer el tamaño de la sección comprimida original
        with open(compressed_size_file_path, "r") as size_file:
            original_compressed_data_size = int(size_file.read())

        # Alinear el tamaño del bloque comprimido
        compressed_size = len(compressed_modified_data)
        if compressed_size < original_compressed_data_size:
            # Si el tamaño comprimido es menor, agregar relleno (bytes nulos)
            padding_size = original_compressed_data_size - compressed_size
            compressed_modified_data += b'\x00' * padding_size
            print(f"Se añadió {padding_size} bytes de relleno para alcanzar el tamaño original.")
        elif compressed_size > original_compressed_data_size:
            # Si el tamaño comprimido es mayor, truncar los datos (con cuidado)
            print("Advertencia: El tamaño comprimido excede el tamaño original, los datos serán truncados.")
            compressed_modified_data = compressed_modified_data[:original_compressed_data_size]

        # Leer la sección ELF extraída
        with open(elf_section_path, "rb") as elf_section_file:
            elf_section_data = elf_section_file.read()

        # Leer el archivo original completo
        with open(input_file_path, "rb") as original_file:
            original_data = original_file.read()

        # Crear el archivo recompuesto
        with open(output_file_path, "wb") as output_file:
            # Escribir la parte anterior al offset (datos intactos)
            output_file.write(original_data[:compressed_section_offset])
            # Escribir la nueva sección comprimida alineada
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
