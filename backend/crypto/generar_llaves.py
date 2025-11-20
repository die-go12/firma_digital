from Crypto.PublicKey import RSA

def generar_llaves():
    key = RSA.generate(2048)  # Genera clave RSA de 2048 bits

    private_key = key.export_key()
    with open("private.pem", "wb") as priv_file:
        priv_file.write(private_key)

    public_key = key.publickey().export_key()
    with open("public.pem", "wb") as pub_file:
        pub_file.write(public_key)

    print("Llaves generadas y guardadas en 'private.pem' y 'public.pem'")

if __name__ == "__main__":
    generar_llaves()
