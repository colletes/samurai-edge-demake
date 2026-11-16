import ast, os
root = "/Users/thiagocarvalho/Public/SamuraiEdge"
files=[os.path.join(root,"main.py")]
for d,_,fs in os.walk(os.path.join(root,"src")):
    for f in fs:
        if f.endswith(".py"): files.append(os.path.join(d,f))
def walk_local(stmts, parent_lists, out):
    # yields (node, list_id, idx_in_list) with enclosing stmt-list chain
    for i, s in enumerate(stmts):
        chain = parent_lists + [(id(stmts), i)]
        out.append((s, chain))
        if isinstance(s,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): continue
        for field in ("body","orelse","finalbody"):
            sub = getattr(s, field, None)
            if isinstance(sub, list) and sub and isinstance(sub[0], ast.stmt):
                walk_local(sub, chain, out)
        if isinstance(s, ast.Try):
            for h in s.handlers:
                walk_local(h.body, chain, out)
        if isinstance(s, ast.Match) if hasattr(ast,"Match") else False:
            for c in s.cases: walk_local(c.body, chain, out)
n=0
for path in sorted(files):
    tree=ast.parse(open(path,encoding="utf-8").read())
    for fn in ast.walk(tree):
        if not isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
        out=[]; walk_local(fn.body, [], out)
        imps=[]  # (name, lineno, chain)
        for s,chain in out:
            if isinstance(s,(ast.Import,ast.ImportFrom)):
                for a in s.names:
                    imps.append(((a.asname or a.name).split(".")[0], s.lineno, chain))
        if not imps: continue
        names={}
        for nm,l,c in imps: names.setdefault(nm,[]).append((l,c))
        for s,chain in out:
            if isinstance(s,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): continue
            # loads directly in this statement's own expressions (not nested stmts, handled separately)
            exprs=[]
            for field,val in ast.iter_fields(s):
                if isinstance(val, ast.AST) and not isinstance(val, ast.stmt): exprs.append(val)
                elif isinstance(val, list):
                    for v in val:
                        if isinstance(v, ast.AST) and not isinstance(v, (ast.stmt, ast.excepthandler)): exprs.append(v)
            for e in exprs:
                for nd in ast.walk(e):
                    if isinstance(nd,ast.Name) and isinstance(nd.ctx,ast.Load) and nd.id in names:
                        ok=False
                        for l,c in names[nd.id]:
                            # import dominates this stmt if import's stmt-list entry is a prefix-compatible earlier sibling
                            # i.e. exists level k: chain_import[:k+1] same list as chain_stmt[k] and idx_import < idx_stmt, and import is at last level (directly in that list)
                            for k,(lid,idx) in enumerate(c):
                                if k < len(chain) and chain[k][0]==lid and k==len(c)-1 and idx < chain[k][1]:
                                    ok=True
                        if not ok:
                            n+=1
                            print(f"{os.path.relpath(path,root)}:{nd.lineno} in {fn.name}() uses '{nd.id}' not dominated by local import (lines {[l for l,_ in names[nd.id]]})")
print("total",n)
