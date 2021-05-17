import json

import wikipedia
import igraph
import unidecode


class WikipediaGraph(igraph.Graph):
    def __init__(self, start_page, levels=1, pages_per_level=10):
        super().__init__()
        self.start_page = start_page
        self.levels = 0
        self.unicode_errors = []
        self.pages_per_level = pages_per_level
        while self.levels < levels:
            self.add_level()

    def add_level(self):
        if self.levels == 0:
            self.map_vertex(self.start_page)
        else:
            unmapped_vertices = igraph.VertexSeq(self).select(is_mapped=False)[:]
            print(unmapped_vertices.indices)
            for v in unmapped_vertices:
                print(v)
                self.map_vertex(v["name"])

        self.levels += 1

    def is_page_in_graph(self, page_name):
        """
        Checks whether a page named "page_name" is in the graph
        """
        page_vertex = None
        try:
            page_vertex = self.vs.find(name=page_name)
            return True
        except ValueError:
            return False

    def is_page_mapped(self, page_name):
        """
        Checks whether page "page_name" has been mapped
        """
        if self.is_page_in_graph(page_name) == False:
            return False
        if self.vs.find(name=page_name)["is_mapped"] == False:
            return False
        return True

    def map_vertex(self, page_name):
        page_link_count = 1

        page = None
        try:
            page = wikipedia.page(page_name)
        except (wikipedia.DisambiguationError, wikipedia.PageError) as e:
            print(page_name)
            return
        print(page_name)
        page_links = map(lambda x: unidecode.unidecode(x), page.links)

        # if page isn't in graph
        if self.is_page_in_graph(page_name) == False:
            vertex = self.add_vertex(name=page_name)  # add the page to the graph
            vertex["is_mapped"] = True
            vertex["level"] = self.levels
            for link in page_links:
                if page_link_count > self.pages_per_level:
                    break
                page_link_count += 1

                if (
                    self.is_page_in_graph(link) == False
                ):  # if the target page isn't already in the graph
                    link_vertex = self.add_vertex(name=link)
                    link_vertex["is_mapped"] = False
                    link_vertex["level"] = self.levels + 1

                self.add_edge(page_name, link)  # connectes the source and target pages

        # if page is in graph but hasn't been mapped
        elif (
            self.is_page_in_graph(page_name) == True
            and self.is_page_mapped(page_name) == False
        ):
            self.vs.find(name=page_name)["is_mapped"] = True
            for link in page_links:
                if page_link_count > self.pages_per_level:
                    break
                page_link_count += 1

                if (
                    self.is_page_in_graph(link) == False
                ):  # if the target page isn't already in the graph
                    link_vertex = self.add_vertex(name=link)
                    link_vertex["is_mapped"] = False
                    #                     print(link_vertex["name"])
                    #                     print(self.levels)
                    link_vertex["level"] = self.levels + 1

                self.add_edge(page_name, link)  # connectes the source and target pages

        # if the page is in the graph and has been mapped
        else:
            return

    def write(self):
        page_name = self.start_page.replace(" ", "_")
        file_name = "static/sample_data/{}_l_{}_ppl_{}.json".format(
            page_name, self.levels, self.pages_per_level
        )
        graph_json = {}
        graph_json["nodes"] = []
        graph_json["links"] = []
        for i, vertex in enumerate(self.vs):
            if i == 0:  # change the group so the node is a different color
                graph_json["nodes"].append(
                    {"id": vertex["name"], "group": vertex["level"]}
                )
            else:
                graph_json["nodes"].append(
                    {"id": vertex["name"], "group": vertex["level"]}
                )
        for edge in self.es:
            graph_json["links"].append(
                {
                    "source": self.vs[edge.source]["name"],
                    "target": self.vs[edge.target]["name"],
                    "value": 1,
                }
            )
        # print(json.dumps(graph_json, indent=1))

        with open(file_name, "w") as f:
            json.dump(graph_json, f)

    def plot(self):
        visual_style = {}
        visual_style["vertex_label"] = self.vs["name"]
        visual_style["layout"] = self.layout("fr")
        visual_style["margin"] = 50

        return igraph.plot(self, **visual_style)

    def _check_result(self, search_query, search_result):
        print(type(search_query))
        print(type(search_result))
        if search_query.lower() == search_result.lower():
            return True
        else:
            return False


if __name__ == "__main__":
    g = WikipediaGraph("Neuroscience", levels=4, pages_per_level=8)
    g.write()
