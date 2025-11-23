import { signPDF, verifyPDF } from "./api.js";

// Firmar PDF
document.getElementById("signBtn")?.addEventListener("click", async () => {
    const file = document.getElementById("pdfInput").files[0];
    const result = document.getElementById("signResult");
    if (!file) return result.textContent = "Seleccione un PDF";

    try {
        const res = await signPDF(file);
        result.textContent = "Documento firmado correctamente: " + JSON.stringify(res);
    } catch {
        result.textContent = "Error al firmar el documento.";
    }
});

// Verificar PDF
document.getElementById("verifyBtn")?.addEventListener("click", async () => {
    const pdf = document.getElementById("verifyPdfInput").files[0];
    const sig = document.getElementById("signatureInput").files[0];
    const result = document.getElementById("verifyResult");

    if (!pdf || !sig) return result.textContent = "Seleccione ambos archivos";

    try {
        const res = await verifyPDF(pdf, sig);
        result.textContent = "Resultado de verificación: " + JSON.stringify(res);
    } catch {
        result.textContent = "Error al verificar el PDF.";
    }
});
