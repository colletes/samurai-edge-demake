import ast, sys, os
root = "/Users/thiagocarvalho/Public/SamuraiEdge"
files = [os.path.join(root, "main.py")]
for d, _, fs in os.walk(os.path.join(root, "src")):
    for f in fs:
        if f.endswith(".py"):
            files.append(os.path.join(d, f))
def local_nodes(fn):
    # yield nodes of fn excluding nested function/class bodies (but include lambdas? skip)
    stack = list(fn.body)
    while stack:
        n = stack.pop()
        yield n
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            stack.append(c)
hits = []
for path in sorted(files):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception as e:
        print("PARSE FAIL", path, e); continue
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        binds = {}  # name -> list of linenos where bound by import
        loads = {}
        assigns = {}
        for n in local_nodes(fn):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    nm = (a.asname or a.name).split(".")[0]
                    binds.setdefault(nm, []).append(n.lineno)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                loads.setdefault(n.id, []).append(n.lineno)
        # nested function bodies referencing the name are closures - ignore
        argnames = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
        for nm, bl in binds.items():
            first = min(bl)
            early = [l for l in loads.get(nm, []) if l < first]
            if early:
                hits.append((path, fn.name, fn.lineno, nm, first, early[:3]))
for h in hits:
    print(f"{os.path.relpath(h[0], root)}:{h[2]} in {h[1]}(): '{h[3]}' imported locally at line {h[4]} but used earlier at {h[5]}")
print("total", len(hits))
