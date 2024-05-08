import pandas as pd
import requests
import time

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        # 2. start recursive search by calling dfs_visit
        self.visited.clear()
        self.order=[]
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        # 2. mark node as visited by adding it to the set
        # 3. call self.visit_and_get_children(node) to get the children
        # 4. in a loop, call dfs_visit on each of the children
        if node in self.visited:
            return
        self.visited.add(node)
        children = self.visit_and_get_children(node)
        for i in children:
            self.dfs_visit(i)
            
    def bfs_search(self, node):
        todo = [node]
        added = {node}
        while len(todo) > 0:
            curr = todo.pop(0)
            child = self.visit_and_get_children(curr)
            for i in child:
                if i not in added:
                    added.add(i)
                    todo.append(i)
        
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        self.order.append(node)
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for node, has_edge in self.df.loc[node].items():
            if has_edge != 0:
                children.append(node)
        return children

class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, node):
        f = open(f"file_nodes/{node}", "r")
        string = f.read()
        f.close()
        string[0]
        self.order.append(string[0])
        children = string.split("\n")[1].split(",")
        return children
    def concat_order(self):
        return "".join(self.order)
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.data = []
        
    def visit_and_get_children(self, url):
        self.order.append(url)
        self.driver.get(url)
        var = self.driver.find_elements_by_tag_name("a")        
        children = []
        self.data.append(pd.read_html(self.driver.page_source)[0])
        for i in var:
            i.get_attribute("href")
            children.append(i.get_attribute("href"))
        return children
       
    def table(self):
        return pd.concat(self.data, ignore_index=True)
        
def reveal_secrets(driver, url, travellog):
    
    list1 = list(travellog["clue"])
    pw = "".join(str(i) for i in list1)
    driver.get(url)
    password= driver.find_element(by="id", value="password")
    go = driver.find_element(by="id", value="attempt-button")
    password.send_keys(pw)
    go.click()
    time.sleep(1)
    view = driver.find_element(by="id", value="securityBtn")
    view.click()
    time.sleep(1)
    image = driver.find_element(by="id", value="image")
    image_link = image.get_attribute("src")
    r = requests.get(image_link).content                        
    with open("Current_Location.jpg", "wb") as f:
        f.write(r)      
    location = driver.find_element(by="id", value="location")
    text = location.text
    return text
