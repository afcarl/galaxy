import networkx as nx

def sentencize(plain_text):
    return plain_text.split(".")

def tokenize(sentence):
    terms = sentence.strip().split(" ")
    return terms

class DocumentIndexGraph(nx.Graph):
    """
    Document Index Graph structure
    as defined on the paper

    "Efficient Phrase-Based Document Indexing for Web Document Clustering"
    """
    def __init__(self):
        super(DocumentIndexGraph, self).__init__()
        self.document_tables = {}
        self.next_doc_id = 1


    def index_document(self, plain_text):
        doc_id = self.next_doc_id
        # split in sentences
        sentences = sentencize(plain_text)
        # tokenize sentences
        sentences = [tokenize(s) for s in sentences]

        for n, sent in enumerate(sentences):
            previous_term = sent[0]
            for p, current_term in enumerate(sent[1:]):
                self.add_edge(doc_id, n + 1, p + 1, previous_term, current_term)
                previous_term = current_term

        self.next_doc_id += 1


    def add_edge(self, doc_id, sentence_number, position_in_sentence, term1, term2):
        edge = (term1, term2)
        super(DocumentIndexGraph, self).add_edge(*edge)
        self.document_tables.setdefault(term1, {})
        doc_table = self.document_tables[term1]

        doc_table.setdefault(doc_id, {})
        edge_table = doc_table[doc_id]

        edge_table.setdefault(edge, {})
        edge_table[edge][sentence_number] = position_in_sentence

if __name__ == '__main__':
    docs = ["river rafting. mild river rafting. river rafting trips",
            "wild river adventures. river rafting vacation plan",
            "fishin trips. fishing vacation plan. booking fishing trips. river fishing"]

    dig = DocumentIndexGraph()
    for doc in docs:
        dig.index_document(doc)

    import ipdb; ipdb.set_trace()

    # TODO: turn the following session into a test
    # (this is the example from the figure 3 in the paper,
    #  we use 1-based indices for docs, sentences, etc. to make
    #  make it easier to match results with the paper)

    # ipdb> dig.nodes()
    # ['river', 'vacation', 'booking', 'rafting', 'fishing', 'trips', 'plan', 'fishin', 'adventures', 'wild', 'mild']
    # ipdb> dig.edges()
    # [('river', 'adventures'), ('river', 'fishing'), ('river', 'rafting'), ('river', 'wild'), ('river', 'mild'), ('vacation', 'rafting'), ('vacation', 'fishing'), ('vacation', 'plan'), ('booking', 'fishing'), ('rafting', 'trips'), ('fishing', 'trips'), ('trips', 'fishin')]
    # ipdb> dig.document_tables["river"]
    # {1: {('river', 'rafting'): {1: 1, 2: 2, 3: 1}}, 2: {('river', 'rafting'): {2: 1}, ('river', 'adventures'): {1: 2}}, 3: {('river', 'fishing'): {4: 1}}}
    # ipdb> doc_table = dig.document_tables["river"]
    # ipdb> doc_table[1]
    # {('river', 'rafting'): {1: 1, 2: 2, 3: 1}}
    # ipdb> doc_table[2]
    # {('river', 'rafting'): {2: 1}, ('river', 'adventures'): {1: 2}}
    # ipdb> doc_table[3]
    # {('river', 'fishing'): {4: 1}}
