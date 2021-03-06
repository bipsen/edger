"""Logic for converting pandas dataframe to gexf."""

from itertools import chain
import numpy as np
from scipy import sparse
import networkx as nx


def edger(df, node, link, graphtype, attr_cols, node_sep, link_sep, file_path):
    """Main function. Called buy GUI, and can be used standalone by supplying a
    pandas dataframe and relevant attributes."""

    df = clean(df, node, link, graphtype, node_sep, link_sep)

    if graphtype == 'normal':
        indptr = np.fromiter(chain((0,), map(len, df[link])),
                             int, len(df[link])+1).cumsum()
        unq, idx = np.unique(np.concatenate(df[link]), return_inverse=True)
        node_link_matrix = sparse.csr_matrix(
            (np.ones(idx.size, int), idx, indptr),
            (len(df[link]),
             len(unq))
        )
        node_node_matrix = (node_link_matrix@node_link_matrix.T).tocoo()
        G = nx.convert_matrix.from_scipy_sparse_matrix(node_node_matrix)
        labels = df[node]

    if graphtype == 'citation':
        indptr = np.fromiter(chain((0,), map(len, df[link])),
                             int, len(df[link])+1).cumsum()
        unq = np.unique(df[node])
        idx = np.where(np.concatenate(df[link])[:, None] == unq[None, :])[1]
        node_node_matrix = sparse.csr_matrix(
            (np.ones(np.concatenate(df[link]).size, int), idx, indptr),
            (len(df[link]),
             len(unq))
        ).rint()
        G = nx.convert_matrix.from_scipy_sparse_matrix(
            node_node_matrix, create_using=nx.DiGraph)
        labels = df[node]

    if graphtype == 'bipartite':
        indptr1 = np.fromiter(chain((0,), map(len, df[node])),
                              int, len(df[node])+1).cumsum()
        unq, idx = np.unique(np.concatenate(df[node]), return_inverse=True)
        node1_matrix = sparse.csr_matrix(
            (np.ones(idx.size, int), idx, indptr1),
            (len(df[node]),
             len(unq))
        )

        indptr2 = np.fromiter(chain((0,), map(len, df[link])),
                              int, len(df[link])+1).cumsum()
        unq, idx = np.unique(np.concatenate(df[link]), return_inverse=True)
        node2_matrix = sparse.csr_matrix(
            (np.ones(idx.size, int), idx, indptr2),
            (len(df[link]),
             len(unq))
        )

        node1_node2_matrix = (node1_matrix.T@node2_matrix).tocoo()
        G = nx.algorithms.bipartite.matrix.from_biadjacency_matrix(
            node1_node2_matrix)
        labels = np.concatenate([np.unique(np.concatenate(df[node])),
                                 np.unique(np.concatenate(df[link]))])

    nx.relabel_nodes(G, dict(zip(G.nodes, labels)), copy=False)

    if attr_cols:
        if graphtype == 'bipartite':
            attrdf = df.explode(node).explode(
                link)[[node] + [link] + attr_cols]
            node_attrs = attrdf.set_index(
                node).drop_duplicates().drop(link, axis=1)
            node_attrs = node_attrs.groupby(node_attrs.index).agg(
                lambda x: '|'.join(x)).to_dict('index')
            link_attrs = attrdf.set_index(
                link).drop_duplicates().drop(node, axis=1)
            link_attrs = link_attrs.groupby(link_attrs.index).agg(
                lambda x: '|'.join(x)).to_dict('index')
            nx.set_node_attributes(G, node_attrs)
            nx.set_node_attributes(G, link_attrs)
        else:
            node_attr_dict = df.set_index(node)[attr_cols].to_dict('index')
            nx.set_node_attributes(G, node_attr_dict)

    outfile = f'{file_path[:-4]}.gexf'
    nx.write_gexf(G, outfile)

    return outfile


def clean(df, node, link, graphtype, node_sep, link_sep):
    """Cleans the dataframe"""
    if node_sep:
        df[node] = df[node].str.split(node_sep)
    if link_sep:
        df[link] = df[link].str.split(link_sep)
    if graphtype != 'bipartite':
        agg_dict = {col: lambda lst: '|'.join([str(x) for x in lst])
                    for col in df.columns if col not in (node, link)}
        agg_dict.update({link: 'sum'})
        df = df.groupby(node).agg(agg_dict).reset_index()
    return df
