import test from "node:test";
import assert from "node:assert/strict";
import {normalizePrice, validateProduct} from "../dist/js/validation.js";
import {graphql} from "../dist/js/graphql-client.js";

test("dinero se conserva como string decimal exacto", () => {
  assert.equal(normalizePrice("00012,50"), "12.50");
  assert.equal(normalizePrice("0.01"), "0.01");
  assert.equal(normalizePrice("9999999999.99"), "9999999999.99");
});
test("precios no válidos se rechazan", () => {
  for (const v of ["0", "-1", "NaN", "Infinity", "1.999", "10000000000", "1e3", "", "1,000.50"]) assert.throws(() => normalizePrice(v));
});
test("normaliza formulario y descripción opcional", () => {
  assert.deepEqual(validateProduct({nombre: " Monitor ", descripcion: " ", precio: "10"}), {nombre: "Monitor", descripcion: null, precio: "10.00"});
  assert.throws(() => validateProduct({nombre: " ", descripcion: "", precio: "10"}));
});
test("GraphQL envía variables y maneja data", async () => {
  const result = await graphql("query Q($id: Int!) { producto(id:$id) { id } }", {id: 1}, async (url, options) => {
    assert.equal(url, "/graphql");
    assert.equal(options.method, "POST");
    assert.deepEqual(JSON.parse(options.body).variables, {id: 1});
    return {ok: true, json: async () => ({data: {producto: {id: 1}}})};
  });
  assert.equal(result.producto.id, 1);
});
test("HTTP 200 con errors no se presenta como éxito", async () => {
  await assert.rejects(() => graphql("query { producto(id:1){id} }", {}, async () => ({ok:true,json:async()=>({data:{producto:null},errors:[{message:"Cambió",extensions:{code:"CONFLICT",requestId:"abc"}}]})})), {code:"CONFLICT",requestId:"abc"});
});
test("HTTP 429 se maneja sin reintento automático", async () => {
  let calls = 0;
  await assert.rejects(() => graphql("query { productos { total } }", {}, async () => { calls++; return {ok:false,status:429}; }), {code:"HTTP_429"});
  assert.equal(calls,1);
});
test("respuesta sin data se rechaza", async () => {
  await assert.rejects(() => graphql("query { productos { total } }", {}, async () => ({ok:true,json:async()=>({})})), {code:"INVALID_RESPONSE"});
});
