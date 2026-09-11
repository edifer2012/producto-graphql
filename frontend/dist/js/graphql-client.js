export class GraphQLRequestError extends Error {
  constructor(message, code, requestId = null) {
    super(message);
    this.name = "GraphQLRequestError";
    this.code = code;
    this.requestId = requestId;
  }
}

export async function graphql(query, variables = {}, fetcher = globalThis.fetch) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetcher("/graphql", {
      method: "POST",
      headers: {"Content-Type": "application/json", Accept: "application/json"},
      body: JSON.stringify({query, variables}),
      signal: controller.signal,
      credentials: "same-origin",
    });
    if (!response.ok) {
      const message = response.status === 429
        ? "Demasiadas solicitudes. Espera unos segundos antes de reintentar."
        : "No fue posible contactar la API. Actualiza el listado para comprobar su estado.";
      throw new GraphQLRequestError(message, `HTTP_${response.status}`);
    }
    const body = await response.json();
    // HTTP 200 no implica éxito en GraphQL. Revisar también el array errors.
    if (body.errors?.length) {
      const first = body.errors[0];
      throw new GraphQLRequestError(first.message, first.extensions?.code || "GRAPHQL_ERROR", first.extensions?.requestId);
    }
    if (!body.data) throw new GraphQLRequestError("La API devolvió una respuesta vacía.", "INVALID_RESPONSE");
    return body.data;
  } catch (error) {
    if (error instanceof GraphQLRequestError) throw error;
    if (error.name === "AbortError") {
      throw new GraphQLRequestError("Se agotó el tiempo de espera. Si estabas guardando, consulta el listado antes de repetir la operación.", "TIMEOUT");
    }
    throw new GraphQLRequestError("La conexión se interrumpió. Consulta el listado antes de repetir un cambio.", "NETWORK_ERROR");
  } finally {
    clearTimeout(timer);
  }
}
