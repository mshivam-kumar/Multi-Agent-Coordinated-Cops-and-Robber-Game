import networkx as nx
import random
import matplotlib.pyplot as plt
import time
import heapq

def generate_random_connected_graph(n, e):
    G = nx.Graph()
    nodes = list(range(n))
    G.add_nodes_from(nodes)
    
    random.shuffle(nodes)
    for i in range(n - 1):
        G.add_edge(nodes[i], nodes[i + 1])
    
    while G.number_of_edges() < e:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            G.add_edge(u, v)
    
    return G

def a_star_chase(graph, start_edge, target_edge):
    def heuristic(edge1, edge2):
        return abs(edge1[0] - edge2[0]) + abs(edge1[1] - edge2[1])
    
    queue = [(0, start_edge, [start_edge])]
    visited = set()
    
    while queue:
        cost, edge, path = heapq.heappop(queue)
        if edge == target_edge:
            return path
        if edge not in visited:
            visited.add(edge)
            for neighbor in graph.edges():
                neighbor = tuple(sorted(neighbor))
                if edge[0] in neighbor or edge[1] in neighbor:
                    if neighbor != edge:
                        heapq.heappush(queue, (cost + 1 + heuristic(neighbor, target_edge), neighbor, path + [neighbor]))
    return []

def get_voronoi_regions(G, cop_edges):
    regions = {cop: set() for cop in cop_edges}
    for node in G.nodes():
        closest_cop = min(cop_edges, key=lambda cop: nx.shortest_path_length(G, source=cop[0], target=node))
        regions[closest_cop].add(node)
    return regions

def draw_graph(G, cop_edges, robber_edge, goal_edge, pos):
    plt.clf()
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    
    def get_position_on_edge(edge, factor):
        return [(1 - factor) * pos[edge[0]][0] + factor * pos[edge[1]][0], (1 - factor) * pos[edge[0]][1] + factor * pos[edge[1]][1]]
    
    for cop_edge in cop_edges:
        plt.scatter(*get_position_on_edge(cop_edge, 0.2), color='red', label='Cop', s=100)
    plt.scatter(*get_position_on_edge(robber_edge, 0.8), color='black', label='Robber', s=100)
    plt.scatter(*get_position_on_edge(goal_edge, 0.5), color='gold', label='Goal', s=100)
    
    plt.legend()
    plt.pause(0.5)

def get_user_move(G, current_edge):
    valid_moves = {tuple(sorted(e)) for e in G.edges() if (current_edge[0] in e or current_edge[1] in e) and e != current_edge}
    print(f"Available moves: {valid_moves}")
    while True:
        try:
            next_move = tuple(sorted(map(int, input("Enter your next move (format: node1 node2): ").split())))
            if next_move in valid_moves:
                return next_move
            else:
                print("Invalid move. Choose an adjacent edge.")
        except ValueError:
            print("Enter valid node numbers.")

def play_game(n, e, num_cops):
    G = generate_random_connected_graph(n, e)
    pos = nx.spring_layout(G, seed=42)
    
    edges = list(G.edges())
    cop_edges = [tuple(sorted(random.choice(edges))) for _ in range(num_cops)]
    robber_edge = tuple(sorted(random.choice([e for e in edges if e not in cop_edges])))
    goal_edge = tuple(sorted(random.choice([e for e in edges if e not in cop_edges and e != robber_edge])))
    
    print(f"Game started. Goal is present at {goal_edge}")
    
    while (cop_edges != robber_edge) and (robber_edge != goal_edge):
        draw_graph(G, cop_edges, robber_edge, goal_edge, pos)
        
        print(f"Robber: {robber_edge}, Cops: {cop_edges}, Goal: {goal_edge}")
        
        previous_robber_edge = robber_edge
        new_robber_edge = get_user_move(G, robber_edge)
        robber_edge = tuple(sorted(new_robber_edge))
        print(f"Robber moved from {previous_robber_edge} to {robber_edge}")
        
        flag = 0
        if robber_edge == goal_edge:
            flag = 1
            print("Robber reached the goal! Robber wins!")
        
        if flag == 0:
            new_cop_edges = []
            regions = get_voronoi_regions(G, cop_edges)
            
            for cop_edge in cop_edges:
                if robber_edge[0] in regions[cop_edge] or robber_edge[1] in regions[cop_edge]:
                    cop_path = a_star_chase(G, cop_edge, robber_edge)
                    if len(cop_path) > 1:
                        cop_edge = tuple(sorted(cop_path[1]))
                new_cop_edges.append(cop_edge)
            
            cop_edges = new_cop_edges
        
        if robber_edge in cop_edges:
            flag = 1
            print("Cop caught the robber! Cops win!")
        
        if flag == 1:
            draw_graph(G, cop_edges, robber_edge, goal_edge, pos)
            break
    
    plt.show()

if __name__ == "__main__":
    n = int(input("Enter number of nodes: "))
    max_edges = n * (n - 1) // 2
    graph_type = input("Choose graph type (sparse/dense): ").strip().lower()
    
    if graph_type in ["sparse", "s"]:
        e = n * 2
    elif graph_type in ["dense", "d"]:
        e = max_edges
    else:
        e = int(input(f"Enter number of edges (max {max_edges}): "))
    
    max_cops = min(e - 1, n // 2)
    num_cops = int(input(f"Enter number of cops (max {max_cops}): "))
    num_cops = max(1, min(num_cops, max_cops))
    
    if e < n:
        print("Number of edges cannot be less than number of nodes")
        exit(0)
    if num_cops > n:
        print("Number of cops cannot be more than number of nodes")
        exit(0)
    
    play_game(n, e, num_cops)