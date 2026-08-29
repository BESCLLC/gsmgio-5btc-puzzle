M = """0 0 1 1 0 1 0 0 1 0 1 1 0 0
1 1 1 1 0 0 1 1 1 0 1 0 1 1
1 1 0 1 1 1 0 1 0 0 1 0 0 1
0 1 1 0 1 0 0 0 0 1 1 1 0 1
0 1 1 0 0 0 1 1 0 0 0 1 1 0
1 0 0 1 1 0 0 0 1 0 0 0 1 1
1 0 0 1 1 1 0 0 0 1 0 0 0 0
1 1 1 0 0 0 0 0 0 0 1 0 0 0
0 0 0 1 1 1 0 1 1 1 1 1 0 1
1 1 1 1 1 1 0 0 1 1 0 0 0 1
1 1 0 1 0 0 0 0 0 1 1 0 1 1
1 1 1 1 0 0 1 0 1 0 1 1 0 0
0 1 0 1 1 1 0 1 0 0 0 1 1 0
0 1 1 0 1 1 0 1 1 0 1 0 1 1"""
rows=[[int(c) for c in l.split()] for l in M.strip().splitlines()]
cols=list(zip(*rows))
rs=[sum(r) for r in rows]
cs=[sum(c) for c in cols]
print("rowsums :",rs, "".join(map(str,rs)))
print("colsums :",cs, "".join(map(str,cs)))
print("total   :",sum(rs))
d1=sum(rows[i][i] for i in range(14)); d2=sum(rows[i][13-i] for i in range(14))
print("diag    :",d1,d2)
