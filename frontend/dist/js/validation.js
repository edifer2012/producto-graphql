export function normalizePrice(value) {
  const normalized = value.trim().replace(",", ".");
  if (!/^\d{1,10}(\.\d{1,2})?$/.test(normalized) || /^0+(\.0+)?$/.test(normalized)) {
    throw new Error("El precio debe ser mayor que cero, con hasta 10 enteros y 2 decimales.");
  }
  const [whole, decimals = ""] = normalized.split(".");
  // Conservar dinero como texto. No utilizar parseFloat ni redondeos binarios.
  return `${whole.replace(/^0+(?=\d)/, "")}.${decimals.padEnd(2, "0")}`;
}

export function validateProduct({nombre, descripcion, precio}) {
  nombre = nombre.trim();
  descripcion = descripcion.trim();
  if (nombre.length < 1 || nombre.length > 120) throw new Error("El nombre debe tener entre 1 y 120 caracteres.");
  if (descripcion.length > 2000) throw new Error("La descripción no puede superar 2000 caracteres.");
  return {nombre, descripcion: descripcion || null, precio: normalizePrice(precio)};
}
