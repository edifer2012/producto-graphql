import {graphql} from "./graphql-client.js";

const fields = "id nombre descripcion precio version creadoEn actualizadoEn";

export async function listProducts(limite = 20, offset = 0) {
  const data = await graphql(`query Listar($limite: Int!, $offset: Int!) {
    productos(limite: $limite, offset: $offset) { items { ${fields} } total limite offset }
  }`, {limite, offset});
  return data.productos;
}

export async function getProduct(id) {
  const data = await graphql(`query Obtener($id: Int!) { producto(id: $id) { ${fields} } }`, {id});
  return data.producto;
}

export async function createProduct(datos) {
  const data = await graphql(`mutation Crear($datos: ProductoInput!) {
    crearProducto(datos: $datos) { ${fields} }
  }`, {datos});
  return data.crearProducto;
}

export async function updateProduct(id, version, datos) {
  const data = await graphql(`mutation Actualizar($id: Int!, $version: Int!, $datos: ProductoInput!) {
    actualizarProducto(id: $id, version: $version, datos: $datos) { ${fields} }
  }`, {id, version, datos});
  return data.actualizarProducto;
}

export async function deleteProduct(id, version) {
  const data = await graphql(`mutation Eliminar($id: Int!, $version: Int!) {
    eliminarProducto(id: $id, version: $version) { id eliminado }
  }`, {id, version});
  return data.eliminarProducto;
}
