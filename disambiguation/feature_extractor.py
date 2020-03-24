# Author: Arjun Menon <amm8987@psu.edu>

"""
This script contains the definition for the following usecases:
1. Retrieve list of patents assigned to inventors with a first and last name similar
to a given inventor
2. Retrieve patent information given patent id
3. Retrieve inventor information given an inventor name and patent id
"""

from utilities import patent_sections


def get_patent_features(con_cursor, pid):
    p_query = "SELECT title from patent where id = '{0}'".format(pid)
    con_cursor.execute(p_query)
    patent_title = con_cursor.fetchone()[0]

    c_query = ("SELECT current.section_id, cpc_subsection.title as sub_sec, "
               "cpc_group.title as cpc_group, cpc_subgroup.title as cpc_subgroup "
               "FROM cpc_current current "
               "LEFT JOIN cpc_subsection on current.subsection_id = cpc_subsection.id "
               "LEFT JOIN cpc_group on current.group_id = cpc_group.id "
               "LEFT JOIN cpc_subgroup on current.subgroup_id = cpc_subgroup.id "
               "WHERE current.patent_id = '{0}' AND current.category='primary' "
               "AND current.sequence=0".format(pid))
    con_cursor.execute(c_query)
    try:
        (section_id, subsec, group, subgroup) = con_cursor.fetchone()
        section = patent_sections[section_id]
    except TypeError as e:
        print(e)
        print("Class query returned empty set for Patent ----> ", pid)
        return None

    org_q = "SELECT a.organization FROM assignee a, patent_assignee pa " \
            "WHERE pa.patent_id = '{0}' AND a.id = pa.assignee_id"
    con_cursor.execute(org_q)
    if con_cursor.rowcount == 1:
        org = con_cursor.fetchone()
    else:
        org = [org[0] for org in con_cursor.fetchall()]
    try:
        org[0]
    except IndexError:
        org = ''

    return patent_title, section, subsec, group, subgroup, org


def get_inventor_features(con_cursor, pid, first_name, last_name):
    loc_q = "SELECT loc.location_id, loc.city, loc.state FROM rawinventor inv, rawlocation loc " \
            "WHERE patent_id = '{0}' AND name_first='{1}' AND name_last = '{2}'" \
            " AND inv.rawlocation_id=loc.id".format(pid, first_name, last_name)
    con_cursor.execute(loc_q)
    try:
        (inv_long_lat, inv_city, inv_state) = con_cursor.fetchone()
    except TypeError:
        return None

    return inv_long_lat, inv_city, inv_state


def get_patents_similar_inventor(con_cursor, first_name, last_name, pid):
    inventor_patents_query = r"SELECT id FROM inventor WHERE name_first = '{0}' AND  " \
                             r"name_last = '{1}';".format(first_name, last_name)
    patent_list_query = r"SELECT patent_id from patent_inventor where inventor_id = '{0}'"
    con_cursor.execute(inventor_patents_query)
    sim_inventor = [sim_inventor[0] for sim_inventor in con_cursor.fetchall()]
    patent_list = []
    for inv in sim_inventor:
        con_cursor.execute(patent_list_query.format(inv))
        patents = [patent[0] for patent in con_cursor.fetchall()]
        if pid not in patents:
            patent_list.extend(patents)
    return patent_list
