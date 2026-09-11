import pytest

CREATE = """mutation($datos: ProductoInput!) {
  crearProducto(datos: $datos) { id nombre descripcion precio version }
}"""
UPDATE = """mutation($id:Int!, $version:Int!, $datos:ProductoInput!) {
  actualizarProducto(id:$id, version:$version, datos:$datos) { id nombre precio version }
}"""
DELETE = """mutation($id:Int!, $version:Int!) {
  eliminarProducto(id:$id, version:$version) { id eliminado }
}"""


def execute(client, query, variables=None):
    response = client.post("/graphql", json={"query": query, "variables": variables or {}})
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    return response.json()


def create(client, **changes):
    datos = {"nombre": "Monitor", "precio": "850000.00", "descripcion": "IPS"} | changes
    return execute(client, CREATE, {"datos": datos})


def test_crud_completo(client):
    created = create(client)
    assert "errors" not in created
    product = created["data"]["crearProducto"]
    assert product["precio"] == "850000.00"
    assert product["version"] == 1
    product_id = product["id"]

    queried = execute(client, "query($id:Int!){producto(id:$id){nombre}}", {"id": product_id})
    assert queried["data"]["producto"] == {"nombre": "Monitor"}

    updated = execute(
        client,
        UPDATE,
        {
            "id": product_id,
            "version": 1,
            "datos": {"nombre": "Monitor 2", "precio": "900000.01"},
        },
    )
    assert "errors" not in updated
    assert updated["data"]["actualizarProducto"]["version"] == 2

    deleted = execute(client, DELETE, {"id": product_id, "version": 2})
    assert deleted["data"]["eliminarProducto"]["eliminado"] is True
    page = execute(client, "{productos {total items{id}}}")
    assert page["data"]["productos"] == {"total": 0, "items": []}


@pytest.mark.parametrize(
    "changes",
    [
        {"nombre": "  "},
        {"nombre": "x" * 121},
        {"precio": "0"},
        {"precio": "-0.01"},
        {"precio": "1.999"},
        {"precio": "10000000000.00"},
        {"descripcion": "x" * 2001},
    ],
)
def test_validacion_no_crea_datos(client, changes):
    result = create(client, **changes)
    assert result["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"
    assert result["data"]["crearProducto"] is None
    assert execute(client, "{productos{total}} ")["data"]["productos"]["total"] == 0


def test_descripcion_null_y_nombre_normalizado(client):
    result = create(client, nombre=" Monitor ", descripcion=None)
    assert result["data"]["crearProducto"]["nombre"] == "Monitor"
    assert result["data"]["crearProducto"]["descripcion"] is None


def test_no_encontrado_tiene_codigo_y_correlacion(client):
    result = execute(client, "{producto(id:999999){id}}")
    assert result["errors"][0]["extensions"]["code"] == "NOT_FOUND"
    assert result["errors"][0]["extensions"]["requestId"]
    assert result["data"]["producto"] is None


@pytest.mark.parametrize(
    "query", ["{productos(limite:101){total}}", "{productos(offset:-1){total}}"]
)
def test_paginacion_acotada(client, query):
    assert execute(client, query)["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"


def test_paginacion_y_aliases(client):
    for name in ["Uno", "Dos", "Tres"]:
        create(client, nombre=name)
    page = execute(client, "{productos(limite:2,offset:1){items{nombre} total}}")
    assert page["data"]["productos"] == {
        "items": [{"nombre": "Dos"}, {"nombre": "Tres"}],
        "total": 3,
    }
    result = execute(client, "{a:productos(limite:1){total} b:productos(limite:1){items{id}}}")
    assert "errors" not in result


def test_edicion_y_borrado_con_version_antigua(client):
    product_id = create(client)["data"]["crearProducto"]["id"]
    params = {"id": product_id, "version": 1, "datos": {"nombre": "Nuevo", "precio": "20.00"}}
    assert "errors" not in execute(client, UPDATE, params)
    for query, variables in [(UPDATE, params), (DELETE, {"id": product_id, "version": 1})]:
        assert execute(client, query, variables)["errors"][0]["extensions"]["code"] == "CONFLICT"


def test_campo_no_definido_se_rechaza(client):
    response = client.post("/graphql", json={"query": "{producto(id:1){secreto}}"})
    assert response.json()["errors"]


def test_exceso_aliases_se_rechaza(client):
    fields = " ".join(f"p{i}:producto(id:1){{id}}" for i in range(11))
    response = client.post("/graphql", json={"query": "{" + fields + "}"})
    assert response.json()["errors"]


def test_health(client):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_get_no_ejecuta_consultas(client):
    response = client.get("/graphql", params={"query": "{productos{total}}"})
    assert response.status_code in (400, 405)
