"""Ensayo de propiedad y privilegios entre dos bases de Leda (T6 de `odd/tasks/aislamiento-entre-clientes.md`).

Uso:
    python tools/ensayo_propiedad.py "<conninfo A>" "<conninfo B>"

Típicamente A es una instalación limpia (`db/esquema.sql` sobre un clúster recién creado con
`initdb`, sin roles `leda_*` previos) y B una base migrada. Lee sólo el catálogo efectivo, nunca
el texto de los archivos, y abre las dos conexiones en modo de sólo lectura
(`default_transaction_read_only=on`): no escribe nada en ninguna de las dos.

Comprueba en cada base:
  a. toda función `security definer` del esquema `leda` tiene un dueño que no es superusuario ni
     tiene `bypassrls`, fija `search_path` con `pg_temp` al final y no la ejecuta `public`
     (`docs/architecture/frontera.md`, regla 1);
  b. toda tabla con `workspace_id` tiene `row level security` encendida y forzada, salvo las
     excepciones declaradas en `tests/garantias/test_aislamiento.py` (`EXCEPCIONES_SIN_RLS`,
     leídas de ahí para no duplicarlas), a las que ni `leda_app` ni `leda_gateway` llegan;
  c. la matriz de privilegios: atributos y membresías de los roles `leda_*`, uso del esquema,
     privilegios por tabla, columna y secuencia, `execute` por función, dueños y privilegios por
     omisión. Las dos matrices se comparan (criterio 5: instalación limpia y base migrada
     convergen a la misma matriz de privilegios).

No lee `.env` ni imprime la cadena de conexión: sólo servidor, puerto y base. Sale con 0 si todo
pasa y las matrices coinciden; con 1 si algo falla o difieren.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row

RAIZ = Path(__file__).resolve().parent.parent
ROLES = ("leda_admin", "leda_app", "leda_gateway", "leda_owner")
TOPE_DE_RENGLONES = 200


def _excepciones_sin_rls() -> dict[str, str]:
    """`EXCEPCIONES_SIN_RLS` de la prueba de aislamiento, leída sin importar el módulo."""
    origen = RAIZ / "tests" / "garantias" / "test_aislamiento.py"
    arbol = ast.parse(origen.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign) and len(nodo.targets) == 1
                and isinstance(nodo.targets[0], ast.Name)
                and nodo.targets[0].id == "EXCEPCIONES_SIN_RLS"):
            return ast.literal_eval(nodo.value)
    raise SystemExit(f"no se encontró EXCEPCIONES_SIN_RLS en {origen.relative_to(RAIZ)}")


def _describir(conninfo: str) -> str:
    d = conninfo_to_dict(conninfo)
    return f"{d.get('host', '?')}:{d.get('port', '5432')}/{d.get('dbname', '?')}"


def _conectar(conninfo: str):
    d = conninfo_to_dict(conninfo)
    opciones = (d.get("options") or "") + " -c default_transaction_read_only=on"
    return psycopg.connect(make_conninfo(**{**d, "options": opciones.strip()}),
                           autocommit=True, row_factory=dict_row)


def _filas(cur, sql: str, params=None) -> list[dict]:
    cur.execute(sql, params)
    return cur.fetchall()


# --- a. funciones elevadas ---------------------------------------------------------------------

def _funciones_elevadas(cur) -> tuple[list[str], dict[str, int], int]:
    filas = _filas(cur, """
        select p.oid::regprocedure::text as firma, r.rolname as dueno, r.rolsuper, r.rolbypassrls,
               p.proconfig, has_function_privilege('public', p.oid, 'execute') as de_public
          from pg_proc p
          join pg_namespace n on n.oid = p.pronamespace
          join pg_roles r on r.oid = p.proowner
         where n.nspname = 'leda' and p.prosecdef
         order by 1""")
    fallas: list[str] = []
    duenos: dict[str, int] = {}
    if not filas:
        fallas.append("no hay ninguna función security definer (¿esquema vacío?)")
    for f in filas:
        duenos[f["dueno"]] = duenos.get(f["dueno"], 0) + 1
        if f["rolsuper"] or f["rolbypassrls"]:
            fallas.append(f"{f['firma']}: dueño {f['dueno']} ignora la RLS "
                          f"(superusuario={f['rolsuper']}, bypassrls={f['rolbypassrls']})")
        camino: list[str] = []
        for c in f["proconfig"] or []:
            if c.startswith("search_path="):
                camino = [e.strip().strip('"') for e in c.removeprefix("search_path=").split(",")]
        if camino[-1:] != ["pg_temp"]:
            fallas.append(f"{f['firma']}: search_path sin pg_temp al final ({camino})")
        if f["de_public"]:
            fallas.append(f"{f['firma']}: la ejecuta public")
    return fallas, duenos, len(filas)


# --- b. RLS de las tablas con espacio ----------------------------------------------------------

def _rls(cur, excepciones: dict[str, str]) -> tuple[list[str], int, list[str]]:
    tablas = _filas(cur, """
        select c.relname, c.relrowsecurity, c.relforcerowsecurity
          from pg_class c
          join pg_namespace n on n.oid = c.relnamespace
          join pg_attribute a on a.attrelid = c.oid
         where n.nspname = 'leda' and c.relkind in ('r', 'p')
           and a.attname = 'workspace_id' and not a.attisdropped
         order by 1""")
    fallas: list[str] = []
    nombres = {t["relname"] for t in tablas}
    if not tablas:
        fallas.append("no hay ninguna tabla con workspace_id (¿esquema vacío?)")
    for sobrante in sorted(set(excepciones) - nombres):
        fallas.append(f"excepción declarada que no es una tabla con workspace_id: {sobrante}")
    for t in tablas:
        if t["relname"] in excepciones:
            continue
        if not (t["relrowsecurity"] and t["relforcerowsecurity"]):
            fallas.append(f"{t['relname']}: rls={t['relrowsecurity']}, "
                          f"forzada={t['relforcerowsecurity']}")
    presentes = sorted(set(excepciones) & nombres)
    if presentes:
        for f in _filas(cur, """
                select t.tabla, r.rol, p.privilegio
                  from unnest(%s::text[]) t(tabla)
                 cross join unnest(array['leda_app', 'leda_gateway']) r(rol)
                 cross join unnest(array['select', 'insert', 'update', 'delete']) p(privilegio)
                 where has_table_privilege(r.rol, 'leda.' || t.tabla, p.privilegio)
                 order by 1, 2, 3""", (presentes,)):
            fallas.append(f"excepción sin RLS a la que llega {f['rol']}: "
                          f"{f['tabla']} ({f['privilegio']})")
    return fallas, len(tablas), presentes


# --- c. matriz de privilegios ------------------------------------------------------------------

def _matriz(cur) -> dict[str, set[tuple]]:
    """Cada categoría es un conjunto de tuplas comparables entre bases. El `grantor` no entra:
    depende de quién corrió el script, no de lo que el rol puede hacer."""
    m: dict[str, set[tuple]] = {}
    m["atributos de rol"] = {
        (f["rolname"], "super" if f["rolsuper"] else "nosuper",
         "inherit" if f["rolinherit"] else "noinherit",
         "login" if f["rolcanlogin"] else "nologin",
         "bypassrls" if f["rolbypassrls"] else "nobypassrls",
         "createrole" if f["rolcreaterole"] else "nocreaterole",
         "createdb" if f["rolcreatedb"] else "nocreatedb",
         "replication" if f["rolreplication"] else "noreplication")
        for f in _filas(cur, "select * from pg_roles where rolname = any(%s)", (list(ROLES),))}
    m["roles leda_* que faltan"] = {
        (r,) for r in ROLES
        if not _filas(cur, "select 1 from pg_roles where rolname = %s", (r,))}
    m["membresías entre roles leda_*"] = {
        (f["rol"], f["miembro"], f["admin_option"], f["inherit_option"], f["set_option"])
        for f in _filas(cur, """
            select r.rolname as rol, u.rolname as miembro, m.admin_option, m.inherit_option,
                   m.set_option
              from pg_auth_members m
              join pg_roles r on r.oid = m.roleid
              join pg_roles u on u.oid = m.member
             where r.rolname = any(%s) and u.rolname = any(%s)""", (list(ROLES), list(ROLES)))}
    m["esquema leda: dueño y privilegios"] = {
        tuple(f.values()) for f in _filas(cur, """
            select 'dueño' as que, pg_get_userbyid(n.nspowner) as quien, '' as priv, false as g
              from pg_namespace n where n.nspname = 'leda'
            union all
            select 'grant', case when a.grantee = 0 then 'PUBLIC'
                                 else pg_get_userbyid(a.grantee) end,
                   a.privilege_type, a.is_grantable
              from pg_namespace n,
                   aclexplode(coalesce(n.nspacl, acldefault('n', n.nspowner))) a
             where n.nspname = 'leda'""")}
    m["dueños de relaciones"] = {
        tuple(f.values()) for f in _filas(cur, """
            select c.relname, c.relkind::text, pg_get_userbyid(c.relowner)
              from pg_class c join pg_namespace n on n.oid = c.relnamespace
             where n.nspname = 'leda' and c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')""")}
    m["privilegios por relación"] = {
        tuple(f.values()) for f in _filas(cur, """
            select c.relname, c.relkind::text,
                   case when a.grantee = 0 then 'PUBLIC' else pg_get_userbyid(a.grantee) end,
                   a.privilege_type, a.is_grantable
              from pg_class c join pg_namespace n on n.oid = c.relnamespace,
                   aclexplode(coalesce(c.relacl, acldefault(
                       case when c.relkind = 'S' then 's' else 'r' end::"char",
                       c.relowner))) a
             where n.nspname = 'leda' and c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')""")}
    m["privilegios por columna"] = {
        tuple(f.values()) for f in _filas(cur, """
            select c.relname, att.attname,
                   case when a.grantee = 0 then 'PUBLIC' else pg_get_userbyid(a.grantee) end,
                   a.privilege_type, a.is_grantable
              from pg_attribute att
              join pg_class c on c.oid = att.attrelid
              join pg_namespace n on n.oid = c.relnamespace,
                   aclexplode(att.attacl) a
             where n.nspname = 'leda' and att.attacl is not null and not att.attisdropped""")}
    m["funciones: dueño, security definer y configuración"] = {
        (f["firma"], f["dueno"], f["prosecdef"], tuple(sorted(f["proconfig"] or ())))
        for f in _filas(cur, """
            select p.oid::regprocedure::text as firma, pg_get_userbyid(p.proowner) as dueno,
                   p.prosecdef, p.proconfig
              from pg_proc p join pg_namespace n on n.oid = p.pronamespace
             where n.nspname = 'leda'""")}
    m["execute por función"] = {
        tuple(f.values()) for f in _filas(cur, """
            select p.oid::regprocedure::text,
                   case when a.grantee = 0 then 'PUBLIC' else pg_get_userbyid(a.grantee) end,
                   a.privilege_type, a.is_grantable
              from pg_proc p join pg_namespace n on n.oid = p.pronamespace,
                   aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
             where n.nspname = 'leda'""")}
    m["privilegios por omisión"] = {
        tuple(f.values()) for f in _filas(cur, """
            select pg_get_userbyid(d.defaclrole), coalesce(n.nspname, '(todos)'),
                   d.defaclobjtype::text,
                   case when a.grantee = 0 then 'PUBLIC' else pg_get_userbyid(a.grantee) end,
                   a.privilege_type, a.is_grantable
              from pg_default_acl d
              left join pg_namespace n on n.oid = d.defaclnamespace,
                   aclexplode(d.defaclacl) a""")}
    m["base: connect y temp"] = {
        tuple(f.values()) for f in _filas(cur, """
            select r.rol, p.priv, has_database_privilege(r.rol, current_database(), p.priv)
              from unnest(%s::text[]) r(rol)
             cross join unnest(array['connect', 'temporary', 'create']) p(priv)""",
            (list(ROLES),))}
    return m


def _informe(nombre: str, cur, excepciones) -> tuple[bool, dict[str, set[tuple]]]:
    print(f"\n== {nombre}")
    ok = True
    fallas_a, duenos, n_elevadas = _funciones_elevadas(cur)
    print(f"  a. funciones security definer: {n_elevadas}; dueños: "
          + ", ".join(f"{d} ({n})" for d, n in sorted(duenos.items())))
    for d in sorted(duenos):
        r = _filas(cur, "select rolsuper, rolbypassrls, rolcanlogin, rolinherit "
                        "from pg_roles where rolname = %s", (d,))[0]
        print(f"     {d}: superusuario={r['rolsuper']}, bypassrls={r['rolbypassrls']}, "
              f"login={r['rolcanlogin']}, inherit={r['rolinherit']}")
    print(f"     {'PASA' if not fallas_a else 'FALLA'}")
    for f in fallas_a:
        print(f"     - {f}")
    fallas_b, n_tablas, presentes = _rls(cur, excepciones)
    print(f"  b. tablas con workspace_id: {n_tablas}; excepciones declaradas presentes: "
          f"{len(presentes)} ({', '.join(presentes)})")
    print(f"     {'PASA' if not fallas_b else 'FALLA'}")
    for f in fallas_b:
        print(f"     - {f}")
    ok = not fallas_a and not fallas_b
    return ok, _matriz(cur)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.split("\n\n")[1])
        return 2
    excepciones = _excepciones_sin_rls()
    resultados = []
    for etiqueta, conninfo in zip(("A", "B"), argv):
        nombre = f"{etiqueta} = {_describir(conninfo)}"
        with _conectar(conninfo) as conn, conn.cursor() as cur:
            resultados.append((nombre, *_informe(nombre, cur, excepciones)))

    (nombre_a, ok_a, m_a), (nombre_b, ok_b, m_b) = resultados
    print("\n== c. matriz de privilegios: A contra B")
    iguales = True
    for categoria in m_a:
        solo_a = sorted(m_a[categoria] - m_b[categoria], key=repr)
        solo_b = sorted(m_b[categoria] - m_a[categoria], key=repr)
        estado = "igual" if not solo_a and not solo_b else "DIFIERE"
        print(f"  {categoria}: {len(m_a[categoria])} en A, {len(m_b[categoria])} en B: {estado}")
        for marca, filas in (("sólo en A", solo_a), ("sólo en B", solo_b)):
            for fila in filas[:TOPE_DE_RENGLONES]:
                print(f"     {marca}: {fila}")
            if len(filas) > TOPE_DE_RENGLONES:
                print(f"     {marca}: ... y {len(filas) - TOPE_DE_RENGLONES} más")
        iguales = iguales and estado == "igual"

    print("\n== Resumen")
    print(f"  a+b en A: {'PASA' if ok_a else 'FALLA'}")
    print(f"  a+b en B: {'PASA' if ok_b else 'FALLA'}")
    print(f"  c. matrices: {'CONVERGEN' if iguales else 'DIFIEREN'}")
    return 0 if ok_a and ok_b and iguales else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
