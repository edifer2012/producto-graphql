import {listProducts, getProduct, createProduct, updateProduct, deleteProduct} from "./products-api.js";
import {validateProduct} from "./validation.js";

const el = (id) => document.getElementById(id);
const state = {offset: 0, limit: 20, total: 0, loading: false, saving: false, editing: null, deleting: null, sequence: 0};

function notify(message, error = false) {
  el("notice").textContent = message;
  el("notice").className = `notice${error ? " error" : ""}`;
  el("notice").hidden = false;
}

function errorText(error) {
  return error.requestId ? `${error.message} Referencia: ${error.requestId}` : error.message;
}

function makeElement(tag, text, className = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

function renderRows(items) {
  el("products").replaceChildren();
  for (const product of items) {
    const row = document.createElement("tr");
    const name = document.createElement("td");
    name.append(makeElement("div", product.nombre, "product-name"), makeElement("div", `ID ${product.id} · v${product.version}`, "product-id"));
    const description = document.createElement("td");
    description.append(makeElement("span", product.descripcion || "Sin descripción", "description"));
    const price = makeElement("td", product.precio, "number");
    const actions = document.createElement("td");
    const actionGroup = makeElement("div", "", "row-actions");
    const edit = makeElement("button", "Editar");
    edit.type = "button";
    edit.setAttribute("aria-label", `Editar ${product.nombre}`);
    edit.addEventListener("click", async () => {
      edit.disabled = true;
      try {
        const current = await getProduct(product.id);
        if (!current) throw new Error("El producto ya no está disponible.");
        openEditor(current);
      } catch (error) { notify(errorText(error), true); }
      finally { edit.disabled = false; }
    });
    const remove = makeElement("button", "Eliminar", "delete");
    remove.type = "button";
    remove.setAttribute("aria-label", `Eliminar ${product.nombre}`);
    remove.addEventListener("click", () => {
      state.deleting = product;
      el("delete-description").textContent = `Vas a eliminar «${product.nombre}» (ID ${product.id}).`;
      el("delete-error").hidden = true;
      el("delete-dialog").showModal();
      el("cancel-delete").focus();
    });
    actionGroup.append(edit, remove);
    actions.append(actionGroup);
    row.append(name, description, price, actions);
    el("products").append(row);
  }
}

function updatePagination() {
  el("previous").disabled = state.loading || state.offset === 0;
  el("next").disabled = state.loading || state.offset + state.limit >= state.total;
  el("refresh").disabled = state.loading;
}

async function loadProducts() {
  const sequence = ++state.sequence;
  state.loading = true;
  updatePagination();
  el("loading").hidden = false;
  el("empty").hidden = true;
  el("table-wrap").hidden = true;
  try {
    const result = await listProducts(state.limit, state.offset);
    if (sequence !== state.sequence) return;
    state.total = result.total;
    if (!result.items.length && state.offset > 0) {
      state.offset = Math.max(0, state.offset - state.limit);
      return await loadProducts();
    }
    renderRows(result.items);
    el("total").textContent = String(result.total);
    el("empty").hidden = result.items.length > 0;
    el("table-wrap").hidden = !result.items.length;
    el("page-info").textContent = result.total ? `${state.offset + 1}–${state.offset + result.items.length} de ${result.total} productos` : "0 productos";
  } catch (error) {
    if (sequence !== state.sequence) return;
    state.total = 0;
    el("page-info").textContent = "Listado no disponible";
    el("total").textContent = "—";
    notify(errorText(error), true);
  } finally {
    if (sequence === state.sequence) {
      state.loading = false;
      el("loading").hidden = true;
      updatePagination();
    }
  }
}

function openEditor(product = null) {
  state.editing = product;
  el("product-form").reset();
  el("editor-title").textContent = product ? "Editar producto" : "Nuevo producto";
  el("save").textContent = product ? "Guardar cambios" : "Crear producto";
  el("name").value = product?.nombre || "";
  el("description").value = product?.descripcion || "";
  el("price").value = product?.precio || "";
  el("form-error").hidden = true;
  el("editor").showModal();
  el("name").focus();
}

function setSaving(value) {
  state.saving = value;
  for (const id of ["save", "cancel-editor", "close-editor", "confirm-delete", "cancel-delete", "name", "description", "price"]) el(id).disabled = value;
}

el("create").addEventListener("click", () => openEditor());
el("refresh").addEventListener("click", () => { el("notice").hidden = true; loadProducts(); });
el("previous").addEventListener("click", () => { state.offset = Math.max(0, state.offset - state.limit); loadProducts(); });
el("next").addEventListener("click", () => { state.offset += state.limit; loadProducts(); });
for (const id of ["close-editor", "cancel-editor"]) el(id).addEventListener("click", () => el("editor").close());
el("cancel-delete").addEventListener("click", () => el("delete-dialog").close());
for (const id of ["editor", "delete-dialog"]) el(id).addEventListener("cancel", (event) => { if (state.saving) event.preventDefault(); });

el("product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.saving) return;
  el("form-error").hidden = true;
  try {
    const datos = validateProduct({nombre: el("name").value, descripcion: el("description").value, precio: el("price").value});
    setSaving(true);
    const product = state.editing
      ? await updateProduct(state.editing.id, state.editing.version, datos)
      : await createProduct(datos);
    el("editor").close();
    notify(`«${product.nombre}» se guardó correctamente.`);
    await loadProducts();
  } catch (error) {
    el("form-error").textContent = errorText(error);
    el("form-error").hidden = false;
  } finally { setSaving(false); }
});

el("confirm-delete").addEventListener("click", async () => {
  if (state.saving || !state.deleting) return;
  setSaving(true);
  try {
    await deleteProduct(state.deleting.id, state.deleting.version);
    el("delete-dialog").close();
    notify("El producto se eliminó correctamente.");
    await loadProducts();
  } catch (error) {
    el("delete-error").textContent = errorText(error);
    el("delete-error").hidden = false;
  } finally { setSaving(false); }
});

loadProducts();
