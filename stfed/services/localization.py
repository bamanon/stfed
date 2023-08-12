import dataclasses
import json
from typing import Optional, List, Tuple

import stfed.model
import stfed.repos.resources
import stfed.factories.sqb
from stfed.model import ImportIssue, SquibResource, Language, Severity


_all_squib_names = [
    1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1100, 1110,
    1120, 1130, 1140, 1310, 1320, 1330, 1340, 1350, 1360, 1410,
    1420, 1430, 1440, 1510, 1610, 1710, 1810, 1910, 1920, 2010,
    3010, 4010, 5000, 5010, 5020, 5030, 5040, 5050, 5060, 5070,
    5080, 5090, 5100, 5110, 5120, 5130, 5140, 5150, 5160, 5170,
    5180, 5190, 5200, 5210, 5220, 5230, 5240, 5250, 5260, 5270,
    5280, 5290, 5300, 5310, 5320, 5330, 5400, 5500, 5600, 5700,
    6000, 7010, 7020, 7030, 7040, 7050, 8010, 8020, 8030, 8040,
    8050, 8060, 8070, 8080, 8090, 8100, 8110, 8120, 8130, 8140,
    8150, 9010, 9110, 9210, 9310
]


def export_language_as_json(language: Language) -> str:
    rns = set(rn + language.value for rn in _all_squib_names)
    rs = [
        r for r in stfed.repos.resources.resources_repo_instance.all_resources()
        if r.resource_type == stfed.model.ResourceType.SQB.value
        if r.resource_name in rns
    ]
    if len(rns) != len(rs):
        found_rns = set(r.resource_number for r in rs)
        missing_rns = rns - found_rns
        raise Exception(f"Not all required SQB resources found in STF files. Missing resources: {','.join(missing_rns)}")
    result = stfed.factories.sqb.export_multiple_as_json(rs)
    return result


def guess_language_from_json(path: str) -> Optional[Language]:
    try:
        with open(path, 'rb') as f:
            content = f.read()
            list_of_dicts = json.loads(content)
            found_langs = set(d['rn'] % 10 for d in list_of_dicts)
            if len(found_langs) == 1:
                return Language(found_langs.pop())
    except:
        pass
    return None


def try_import_language_from_json(
    path: str,
    language: Language
) -> Tuple[List[ImportIssue], List[SquibResource]]:
    issues = []
    with open(path, 'r') as f:
        try:
            content = f.read()
        except Exception as ex:
            issues.append(
                ImportIssue(
                    Severity.Critical,
                    f"Selected file is not a text file: {ex}"))
            return issues, []
        
    try:
        list_of_dicts = json.loads(content)
    except Exception as ex:
        issues.append(
            ImportIssue(
                Severity.Critical,
                f"Selected file is not valid json: {ex}"))
        return issues, []

    found_langs = set(d['rn'] % 10 for d in list_of_dicts)
    if len(found_langs) > 1:
        issues.append(
            ImportIssue(
                Severity.Warning,
                "Resource numbers in the imported file refer to several different languages, " +
                "they will be changed to target language on import."))

    imported_sqbs = stfed.factories.sqb.import_json(content)

    found_rns = set((s.resource_name // 10) * 10 for s in imported_sqbs)
    if len(_all_squib_names) != len(found_rns):
        missing_rns = _all_squib_names - found_rns
        # TODO: import what you've got and skip missing ones?
        issues.append(
            ImportIssue(
                Severity.Critical,
                f"Imported file doesn't match all required SQB resources. Missing resources: {','.join(missing_rns)}"))

    language_adj_sqbs = replace_language(imported_sqbs, language)
    adjusted_rns = set(s.resource_name for s in language_adj_sqbs)
    current_rs = {
        r.resource_name: r
        for r in stfed.repos.resources.resources_repo_instance.all_resources()
        if r.resource_type == stfed.model.ResourceType.SQB.value
        if r.resource_name in adjusted_rns
    }
    for imported_sqb in imported_sqbs:
        current_sqb = stfed.factories.sqb.parse(current_rs[imported_sqb.resource_name])
        current_keys = current_sqb.squibs.keys()
        imported_keys = imported_sqb.squibs.keys()
        missing_keys = current_keys - imported_keys
        if len(missing_keys) > 0:
            missing_keys_formatted = ', '.join(str(k) for k in extra_keys)
            issues.append(
                ImportIssue(
                    Severity.Critical,
                    f"Missing required keys: {missing_keys_formatted} for resource {imported_sqb.resource_name}.SQB"))
        extra_keys =  imported_keys - current_keys
        if len(extra_keys) > 0:
            extra_keys_formatted = ', '.join(str(k) for k in extra_keys)
            issues.append(
                ImportIssue(
                    Severity.Warning,
                    f"Extraneous keys: {extra_keys_formatted} for resource {imported_sqb.resource_name}.SQB"))
    return issues, imported_sqbs


def save_imported_sqbs(sqbs: List[SquibResource], target_language: Language):
    sqbs = replace_language(sqbs, target_language)
    resources = [
        stfed.model.InMemoryResource(
            sqb.resource_name,
            stfed.model.ResourceType.SQB.value,
            0,
            0,
            stfed.factories.sqb.dump(sqb)
        )
        for sqb in sqbs
    ]
    for r in resources:
        stfed.repos.resources.resources_repo_instance.update(r)


def replace_language(
    sqbs: List[SquibResource],
    language: Language
) -> List[SquibResource]:
    return [
        dataclasses.replace(
            sqb,
            resource_name=(sqb.resource_name // 10) * 10 + language.value)
        for sqb in sqbs
    ]
