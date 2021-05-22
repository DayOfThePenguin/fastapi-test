import json
import logging

import igraph

from database.models import WikiMap

import utils.scratch

VERTICES_PER_CHUNK = 10
logging.basicConfig(level=logging.INFO)


class WikipediaGraph(igraph.Graph):
    """Subclass of igraph.Graph for storing data about a wikipedia graph

    assumes first title has already been validated and that subsequent links that
    wikipedia returns are links to real pages

        Parameters
        ----------
        igraph : [type]
            [description]
    """

    def __init__(self, start_page, levels=1, lpp=10):
        super().__init__()
        self.start_page = start_page
        self.levels = levels
        self.lpp = lpp

    def generate(self, yield_size=None):
        """build out a graph of wikipedia page connections

        the function can work in two ways. if yield_size is an integer, every time
        yield_size new vertices are added to the graph, it will yield a json chunk
        of the new vertices and edges that have been added (so you can serve it over
        a websocket). if yield_size is None, it will build the whole graph without
        yielding anything

        Parameters
        ----------
        yield_size : int, optional
            how many vertices to yield at a time, by default None. if None, won't yield
            anything and will just build the whole graph.

        Yields
        -------
        Dict
            dict of vertices and edges that can be sent over a websocket as json
        """
        start_vertex = self.add_vertex(name=self.start_page, is_mapped=False, level=0)
        if yield_size is not None:
            yield self._json_chunk([start_vertex], [])
        new_vertices = []
        new_edges = []
        current_level = 1
        for _ in range(self.levels):
            unmapped_vertices = self.vs.select(is_mapped=False)
            for vertex in unmapped_vertices:
                vertex_links = utils.scratch.get_links(
                    vertex["name"], num_links=self.lpp
                )
                for link in vertex_links:
                    if self.is_page_in_graph(link):
                        self.add_edge(vertex, link)
                        if yield_size is not None:
                            new_edges.append([vertex["name"], link])
                    else:
                        link_vertex = self.add_vertex(
                            name=link, is_mapped=False, level=current_level
                        )
                        self.add_edge(vertex, link)
                        if yield_size is not None:
                            new_vertices.append(link_vertex)
                            new_edges.append([vertex["name"], link])
                            if len(new_vertices) == yield_size:
                                yield self._json_chunk(new_vertices, new_edges)
                                new_vertices = []
                                new_edges = []
                self.vs.find(name=vertex["name"])["is_mapped"] = True
            current_level += 1
        if yield_size is not None:  # yield the last bit
            yield self._json_chunk(new_vertices, new_edges)

    def generate_from_wikimap(self, wikimap: WikiMap, yield_size=10):
        nodes = wikimap.json_data["nodes"]
        links = wikimap.json_data["links"]
        min_vertex_id = len(nodes)
        max_vertex_id = 0
        while True:
            if len(nodes) == 0 and len(links) == 0:
                return None
            graph_json = {}
            graph_json["nodes"] = []
            graph_json["links"] = []
            for _ in range(yield_size):
                try:
                    node = nodes.pop(0)
                    graph_json["nodes"].append(node)
                    if node["id"] > max_vertex_id:
                        max_vertex_id = node["id"]
                    if node["id"] < min_vertex_id:
                        min_vertex_id = node["id"]
                except IndexError:
                    break
            pop_indices = []
            for i in range(len(links)):
                valid_source = (
                    links[i]["source"] <= max_vertex_id
                    and links[i]["source"] >= min_vertex_id
                )
                valid_target = (
                    links[i]["target"] <= max_vertex_id
                    and links[i]["target"] >= min_vertex_id
                )
                if valid_source and valid_target:
                    graph_json["links"].append(links[i])
                    pop_indices.append(i)
            pop_indices = sorted(pop_indices, reverse=True)
            for idx in pop_indices:
                links.pop(idx)

            yield graph_json

    def _json_chunk(self, new_vertices, new_edges):
        """returns a json chunk that can be websocketed'd to the browser

        Parameters
        ----------
        new_vertices : List[igraph.Vertex]

        new_edges : List[List[str, str]]
            list of lists of the form [src_name, target_name]
        """
        graph_json = {}
        graph_json["nodes"] = []
        graph_json["links"] = []

        for vertex in new_vertices:
            graph_json["nodes"].append(
                {"id": vertex.index, "name": vertex["name"], "group": vertex["level"]}
            )
        for edge in new_edges:
            graph_json["links"].append(
                {
                    "source": self.vs.find(name=edge[0]).index,
                    "target": self.vs.find(name=edge[1]).index,
                    "value": 1,
                }
            )
        return graph_json

    def is_page_in_graph(self, page_name):
        """
        Checks whether a page named "page_name" is in the graph
        """
        try:
            self.vs.find(name=page_name)
            return True
        except ValueError:
            return False

    def get_json_dict(self):
        graph_json = {}
        graph_json["nodes"] = []
        graph_json["links"] = []
        for vertex in self.vs:
            graph_json["nodes"].append(
                {"id": vertex.index, "name": vertex["name"], "group": vertex["level"]}
            )
        for edge in self.es:
            graph_json["links"].append(
                {
                    "source": self.vs[edge.source].index,
                    "target": self.vs[edge.target].index,
                    "value": 1,
                }
            )
        return graph_json

    def write_json(self):
        """write graph to file

        use the json format that 3d-force-directed-graph can read
        """
        graph_json = self.get_json_dict()
        page_name = self.start_page.replace(" ", "_")
        file_name = "static/sample_data/{}_l_{}_lpp_{}.json".format(
            page_name, self.levels, self.lpp
        )
        with open(file_name, "w") as f:
            json.dump(graph_json, f)
        logging.info("Wrote file %s", file_name)


if __name__ == "__main__":
    # graph = WikipediaGraph("Neuroscience", levels=4, lpp=8)
    # for json_chunk in graph.generate():
    #     pass
    #     # print(json.dumps(json_chunk, indent=2, separators=(",", ": ")))
    # graph.write()
    from database.db import Database

    database = Database(sslmode=False)
    with database.Session() as sess:
        result = sess.query(WikiMap).filter_by(title="COVID-19 pandemic", lpp=2).first()
        logging.info(result)
    graph = WikipediaGraph("COVID-19 pandemic", levels=2, lpp=2)
    for json_chunk in graph.generate_from_wikimap(result, yield_size=5):
        print(json_chunk)
