"""Small helper: run a SPARQL query on LiITA (POST), return bindings as plain dicts."""
import requests, sys, json
PREFIXES = """PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX elita: <http://w3id.org/elita/>
PREFIX marl: <http://www.gsi.upm.es/ontologies/marl/ns#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX lime: <http://www.w3.org/ns/lemon/lime#>
"""
def run(q, prefixes=True, timeout=300):
    r = requests.post("https://liita.it/sparql", data={"query": (PREFIXES if prefixes else "") + q},
                      headers={"Accept": "application/sparql-results+json"}, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
    return [{k: v["value"] for k, v in b.items()} for b in r.json()["results"]["bindings"]]
def short(v):
    return v.rsplit("#", 1)[-1].rsplit("/", 1)[-1] if v.startswith("http") else v
