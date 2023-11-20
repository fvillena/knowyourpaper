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
SELECT ?publlabel ?citingpublabel WHERE {{
  ?publ rdf:type dblp:Publication .
  ?publ dblp:doi <https://doi.org/{doi}> .
  ?publ dblp:doi ?publdoi .
  ?publ rdfs:label ?publlabel .
  ?citation rdf:type cito:Citation .
  ?citation cito:hasCitedEntity ?publdoi .
  ?citation cito:hasCitingEntity ?citingpubldoi .
  OPTIONAL {{
  ?citingpubl rdf:type dblp:Publication .
  ?citingpubl dblp:doi ?citingpubldoi .
  ?citingpubl rdfs:label ?citingpublabel .
  }}
}}
"""
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    publlabel = results["results"]["bindings"][0]["publlabel"]["value"]
    citingpubllabels = []
    for citingpubl in results["results"]["bindings"]:
        try:
            citingpubllabels.append(citingpubl["citingpublabel"]["value"])
        except KeyError:
            citingpubllabels.append("-")
    return render(
        request,
        "paper/paper.html",
        {
            "publlabel": publlabel,
            "cites_num": len(citingpubllabels),
            "citingpubllabels": citingpubllabels,
        },
    )
