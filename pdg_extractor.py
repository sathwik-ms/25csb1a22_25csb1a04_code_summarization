import ast
import re

try:
    from agent_security.input_limits import safe_parse
except ImportError:
    safe_parse = ast.parse

class PDGExtractor(ast.NodeVisitor):
    def __init__(self):
        # We will store dependencies as a list of strings to feed the NLP model
        self.nodes = []
        self.control_edges = []
        self.data_edges = []
        self.node_linenos = {}  # node_id -> AST line number
        
        # Track state during traversal
        self.current_control_node = "root"
        self.var_definitions = {}  # var_name -> defining_node_id
        self.node_counter = 0

    def add_node(self, desc, lineno=0):
        node_id = f"N{self.node_counter}"
        self.node_counter += 1
        self.nodes.append(f"{node_id}: {desc}")
        self.node_linenos[node_id] = lineno
        return node_id

    def add_control_edge(self, target_id, source_id):
        self.control_edges.append(f"{target_id} depends on {source_id} (Control)")

    def add_data_edge(self, target_id, var_name, source_id):
        self.data_edges.append(f"{target_id} uses '{var_name}' from {source_id} (Data)")

    def visit_FunctionDef(self, node):
        node_id = self.add_node(f"Function {node.name}", lineno=getattr(node, 'lineno', 0))
        self.control_edges.append(f"{node_id} depends on root (Control)")
        
        # Record arguments as data sources
        for arg in node.args.args:
            self.var_definitions[arg.arg] = node_id
            
        prev_control = self.current_control_node
        self.current_control_node = node_id
        
        self.generic_visit(node)
        
        self.current_control_node = prev_control

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        val_str = ast.unparse(node.value) if hasattr(ast, 'unparse') else "value"
        
        node_id = self.add_node(f"Assign {', '.join(targets)} = {val_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)
        
        # Find data dependencies (variables used on the right side)
        for var_node in ast.walk(node.value):
            if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                if var_node.id in self.var_definitions:
                    self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])
        
        # Update data definitions
        for target in targets:
            self.var_definitions[target] = node_id

    def visit_AugAssign(self, node):
        if not isinstance(node.target, ast.Name):
            return
        var = node.target.id
        val_str = ast.unparse(node.value) if hasattr(ast, 'unparse') else "value"
        op_name = type(node.op).__name__
        op_map = {"Add": "+=", "Sub": "-=", "Mult": "*=", "Div": "/=", "Mod": "%=", "Pow": "**="}
        op_str = op_map.get(op_name, f"({op_name})=")
        
        node_id = self.add_node(f"AugAssign {var} {op_str} {val_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)

        # Read dependency: current definition of var flows IN
        if var in self.var_definitions:
            self.add_data_edge(node_id, var, self.var_definitions[var])

        # Data deps from RHS expression
        for var_node in ast.walk(node.value):
            if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                if var_node.id in self.var_definitions:
                    self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])

        # Write: update definition of var to this node
        self.var_definitions[var] = node_id

    def visit_For(self, node):
        iter_str = ast.unparse(node.iter) if hasattr(ast, 'unparse') else "iter"
        target_str = ast.unparse(node.target) if hasattr(ast, 'unparse') else "target"
        node_id = self.add_node(f"For {target_str} in {iter_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)

        # Data dep: variables used in iterable expression
        for var_node in ast.walk(node.iter):
            if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                if var_node.id in self.var_definitions:
                    self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])

        # Loop variables defined by for-node
        if isinstance(node.target, ast.Name):
            self.var_definitions[node.target.id] = node_id
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in ast.walk(node.target):
                if isinstance(elt, ast.Name):
                    self.var_definitions[elt.id] = node_id

        # Visit body with for-node as control parent
        prev_control = self.current_control_node
        self.current_control_node = node_id
        for stmt in node.body:
            self.visit(stmt)
        if node.orelse:
            self.current_control_node = f"{node_id}_Else"
            for stmt in node.orelse:
                self.visit(stmt)
        self.current_control_node = prev_control

    def visit_While(self, node):
        test_str = ast.unparse(node.test) if hasattr(ast, 'unparse') else "condition"
        node_id = self.add_node(f"While {test_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)

        # Data deps in condition
        for var_node in ast.walk(node.test):
            if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                if var_node.id in self.var_definitions:
                    self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])

        prev_control = self.current_control_node
        self.current_control_node = node_id
        for stmt in node.body:
            self.visit(stmt)
        if node.orelse:
            self.current_control_node = f"{node_id}_Else"
            for stmt in node.orelse:
                self.visit(stmt)
        self.current_control_node = prev_control

    def visit_If(self, node):
        test_str = ast.unparse(node.test) if hasattr(ast, 'unparse') else "condition"
        node_id = self.add_node(f"If {test_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)
        
        # Data dependencies in condition
        for var_node in ast.walk(node.test):
            if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                if var_node.id in self.var_definitions:
                    self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])
                    
        # Visit body with IF as control node
        prev_control = self.current_control_node
        self.current_control_node = node_id
        for stmt in node.body:
            self.visit(stmt)
            
        # Visit orelse with IF as control node
        self.current_control_node = f"{node_id}_Else"
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)
                
        self.current_control_node = prev_control

    def visit_With(self, node):
        items_str = ", ".join(
            ast.unparse(item.context_expr) if hasattr(ast, 'unparse') else "ctx"
            for item in node.items
        )
        node_id = self.add_node(f"With {items_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)

        for item in node.items:
            # Data deps from context expression
            for var_node in ast.walk(item.context_expr):
                if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                    if var_node.id in self.var_definitions:
                        self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self.var_definitions[item.optional_vars.id] = node_id

        prev_control = self.current_control_node
        self.current_control_node = node_id
        for stmt in node.body:
            self.visit(stmt)
        self.current_control_node = prev_control

    def visit_Call(self, node):
        func_str = ast.unparse(node.func) if hasattr(ast, 'unparse') else "call"
        node_id = self.add_node(f"Call {func_str}(...)", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)

        # Arguments data dependencies
        for arg in node.args:
            for var_node in ast.walk(arg):
                if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                    if var_node.id in self.var_definitions:
                        self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])
        for kw in node.keywords:
            for var_node in ast.walk(kw.value):
                if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                    if var_node.id in self.var_definitions:
                        self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])

    def visit_Expr(self, node):
        # If expression is a bare Call, visit it to capture invocation dependencies
        if isinstance(node.value, ast.Call):
            self.visit(node.value)
        else:
            self.generic_visit(node)

    def visit_Return(self, node):
        ret_str = ast.unparse(node.value) if hasattr(ast, 'unparse') and node.value else "None"
        node_id = self.add_node(f"Return {ret_str}", lineno=getattr(node, 'lineno', 0))
        self.add_control_edge(node_id, self.current_control_node)
        
        if node.value:
            for var_node in ast.walk(node.value):
                if isinstance(var_node, ast.Name) and isinstance(var_node.ctx, ast.Load):
                    if var_node.id in self.var_definitions:
                        self.add_data_edge(node_id, var_node.id, self.var_definitions[var_node.id])

def extract_pdg_context(source_code: str) -> str:
    """
    Parses the source code to extract a simplified Program Dependence Graph (PDG),
    capturing Control Flow and Data Flow dependencies.
    """
    try:
        tree = safe_parse(source_code)
        extractor = PDGExtractor()
        extractor.visit(tree)
        
        pdg_representation = "Nodes:\n" + "\n".join(extractor.nodes) + "\n"
        pdg_representation += "Edges:\n" + "\n".join(extractor.control_edges + extractor.data_edges)
        
        if len(pdg_representation) > 4000:
            pdg_representation = pdg_representation[:4000] + "\n...[Truncated]"
            
        return pdg_representation.strip()
    except Exception as e:
        return f"PDG parsing failed: {str(e)}"


def extract_pdg_graph(source_code: str) -> dict:
    """
    Extracts structured PDG nodes and edges for visualization.
    Edges point from the dependency source to the dependent target.
    """
    try:
        tree = safe_parse(source_code)
        extractor = PDGExtractor()
        extractor.visit(tree)

        nodes = {"root": "Program root"}
        node_linenos = {"root": 0}
        for node_text in extractor.nodes:
            node_id, _, label = node_text.partition(": ")
            if node_id:
                nodes[node_id] = label or node_id
                node_linenos[node_id] = extractor.node_linenos.get(node_id, 0)

        edges = []
        for edge_text in extractor.control_edges:
            match = re.match(r"(?P<target>\S+) depends on (?P<source>\S+) \(Control\)", edge_text)
            if match:
                edges.append(
                    {
                        "source": match.group("source"),
                        "target": match.group("target"),
                        "kind": "Control",
                        "label": "control",
                    }
                )

        for edge_text in extractor.data_edges:
            match = re.match(
                r"(?P<target>\S+) uses '(?P<var>[^']+)' from (?P<source>\S+) \(Data\)",
                edge_text,
            )
            if match:
                edges.append(
                    {
                        "source": match.group("source"),
                        "target": match.group("target"),
                        "kind": "Data",
                        "label": match.group("var"),
                    }
                )

        return {
            "status": "ok",
            "nodes": nodes,
            "node_linenos": node_linenos,
            "edges": edges,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "nodes": {},
            "node_linenos": {},
            "edges": [],
        }

if __name__ == "__main__":
    sample_code = '''
def process_items(items):
    total = 0
    for x in items:
        total += x
    while total > 100:
        total -= 10
    print(total)
    return total
'''
    print("=== PDG Context ===")
    print(extract_pdg_context(sample_code))
    print("\n=== PDG Graph ===")
    g = extract_pdg_graph(sample_code)
    print("Nodes:", len(g["nodes"]))
    print("Edges:", len(g["edges"]))
    print("Line numbers:", g.get("node_linenos"))
