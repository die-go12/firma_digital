from firmar_pdf import firmar_pdf

# Nombre del PDF
archivo_pdf = 'constancia.pdf'

# Generar la firma
firma = firmar_pdf(archivo_pdf)

# Guardar la firma en un archivo
with open('constancia_firma.bin', 'wb') as f:
    f.write(firma)

print("Firma guardada en 'constancia_firma.bin'")
