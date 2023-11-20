from django.shortcuts import render

from django.http import HttpResponse

from SPARQLWrapper import SPARQLWrapper, JSON


def index(request):
    return HttpResponse("Hello, world. You're at the paper index.")


def paper(request, doi):
    sparql = SPARQLWrapper("https://sparql.dblp.org/sparql")
    sparql.setQuery(
        f"""
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?label (COUNT(?citation) as ?cites) WHERE {{
  ?publ rdf:type dblp:Publication .
  ?publ dblp:title ?title .
  ?publ dblp:doi <https://doi.org/{doi}> .
  ?publ rdfs:label ?label .
  ?publ dblp:doi ?doi .
  ?citation rdf:type cito:Citation .
  ?citation cito:hasCitedEntity ?doi .
}}
GROUP BY ?label
"""
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    label = results["results"]["bindings"][0]["label"]["value"]
    cites = results["results"]["bindings"][0]["cites"]["value"]
    return HttpResponse(f"{label} has {cites} cites.")
