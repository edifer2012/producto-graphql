"""Prueba CRUD sobre un registro nuevo y propio; no elimina productos existentes."""

import json
import sys
import uuid
from urllib.request import Request, urlopen

endpoint = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/graphql"


def call(query, variables=None):
    data = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=15) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


product = None
try:
    product = call(
        "mutation($datos:ProductoInput!){crearProducto(datos:$datos){id version}}",
        {"datos": {"nombre": f"Smoke-{uuid.uuid4()}", "precio": "19.90"}},
    )["crearProducto"]
    queried = call("query($id:Int!){producto(id:$id){precio}}", {"id": product["id"]})
    assert queried["producto"]["precio"] == "19.90"
    product = call(
        "mutation($id:Int!,$version:Int!,$datos:ProductoInput!){"
        "actualizarProducto(id:$id,version:$version,datos:$datos){id version}}",
        {**product, "datos": {"nombre": "Smoke actualizado", "precio": "20.00"}},
    )["actualizarProducto"]
finally:
    if product:
        call(
            "mutation($id:Int!,$version:Int!){eliminarProducto(id:$id,version:$version){eliminado}}",
            product,
        )
print("CRUD smoke: OK (registro temporal eliminado)")
