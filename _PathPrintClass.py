# Python program to print all paths from a source to destination.
import sys
import pandas as pd
import altair as alt
import numpy as np
from collections import defaultdict


class Graph:

    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices

        # default dictionary to store graph
        self.graph = defaultdict(list)

    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)

    '''A recursive function to print all paths from 'u' to 'd'. 
    visited[] keeps track of vertices in current path. 
    path[] stores actual vertices and path_index is current 
    index in path[]'''

    # patharray = []

    def printAllPathsUtil(self, u, d, visited, path, storagearray):

        # Mark the current node as visited and store in path

        visited[u] = True
        path.append(u)

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            storagearray.append(path[:])
        else:
            i=0
            for i in self.graph[u]:
                if visited[i] == False:
                    self.printAllPathsUtil(i, d, visited, path, storagearray)

        # st.write(storagearray)
        path.pop()
        visited[u] = False
        return storagearray

    def printAllPaths(self, s, d):
        visited = [False] * (self.V)
        path = []
        storagearray = []
        self.printAllPathsUtil(s, d, visited, path, storagearray)

        return storagearray
