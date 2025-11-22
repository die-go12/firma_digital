from Crypto.PublicKey import RSA

def generate_keys_bytes():
    """
    Genera un par de claves RSA (Privada y Pública).
    Retorna:
        Tuple(bytes, bytes): (clave_privada, clave_publica)
    No guarda archivos en disco, solo devuelve los datos crudos.
    """
    key = RSA.generate(2048)
    
    # Exportamos a formato PEM (bytes)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    
    return private_key, public_key


if __name__ == "__main__":
    print("Probando generación de llaves...")
    priv, pub = generate_keys_bytes()
    print(f"Llave privada generada ({len(priv)} bytes)")
    print(f"Llave pública generada ({len(pub)} bytes)")
