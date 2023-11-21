from django.shortcuts import render

from django.http import HttpResponse, HttpResponseNotFound

from SPARQLWrapper import SPARQLWrapper, JSON


def index(request):
    return render(request, "paper/index.html")


def get_doi(doi_url):
    # get url path without the domain
    doi = doi_url.split("doi.org/")[-1]
    return doi


def get_citations(doi):
    sparql = SPARQLWrapper("https://sparql.dblp.org/sparql")
    sparql.setQuery(
        f"""
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {{
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
    return results["results"]["bindings"]


def get_publication_authors(doi):
    sparql = SPARQLWrapper("https://sparql.dblp.org/sparql")
    sparql.setQuery(
        f"""
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {{
  ?publ rdf:type dblp:Publication .
  ?publ dblp:doi <https://doi.org/{doi}> .
  ?publ dblp:authoredBy ?author .
  ?author rdfs:label ?name .
}}
"""
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # return author names
    return [result["name"]["value"] for result in results["results"]["bindings"]]


def get_publication_info(doi):
    authors = get_publication_authors(doi)
    sparql = SPARQLWrapper("https://sparql.dblp.org/sparql")
    sparql.setQuery(
        f"""
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {{
  ?publ rdf:type dblp:Publication .
  ?publ dblp:doi <https://doi.org/{doi}> .
  ?publ rdfs:label ?publlabel .
  ?publ dblp:publishedIn ?source .
  ?publ dblp:title ?publtitle .
}}
"""
    )
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"][0]
    return {
        "label": result["publlabel"]["value"],
        "source": result["source"]["value"],
        "doi_url": f"https://doi.org/{doi}",
        "authors": authors,
        "title": result["publtitle"]["value"]
    }


def paper(request, doi):
    citing_papers = get_citations(doi)
    try:
        publication_info = get_publication_info(doi)
    except IndexError:
        return HttpResponseNotFound("Paper not found")
    publlabel = publication_info["label"]
    publdoi = publication_info["doi_url"]
    publauthors = publication_info["authors"]
    publsource = publication_info["source"]
    publtitle = publication_info["title"]
    if len(citing_papers) > 0:
        citingpubls = []
        for citingpubl in citing_papers:
            try:
                citingpubls.append(
                    {
                        "label": citingpubl["citingpublabel"]["value"],
                        "doi": get_doi(citingpubl["citingpubldoi"]["value"]),
                    }
                )
            except KeyError:
                citingpubls.append(
                    {"label": "-", "doi": get_doi(citingpubl["citingpubldoi"]["value"])}
                )
        return render(
            request,
            "paper/paper.html",
            {
                "publlabel": publlabel,
                "cites_num": len(citingpubls),
                "citingpubls": citingpubls,
                "publdoi": publdoi,
                "publauthors": publauthors,
                "publsource": publsource,
                "publtitle": publtitle,
            },
        )
    else:
        return render(
            request,
            "paper/paper.html",
            {
                "publlabel": publlabel,
                "cites_num": 0,
                "citingpubls": [],
                "publdoi": publdoi,
                "publauthors": publauthors,
                "publsource": publsource,
                "publtitle": publtitle,
            },
        )
