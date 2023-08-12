import dataclasses
import json
from typing import Callable, List, Optional, Tuple

import stfed.factories.sqb
from stfed.model import ResourceType, ImportIssue, Severity, SquibResource, InMemoryResource
from stfed.repos.user_preferences import repo as user_preferences_repo
import stfed.repos.resources

def get_file_filters_for_resource_import(rt: ResourceType) -> List[str]:
    ext = rt.name.upper()

    filters = [
        f"{ext} file *.{ext} (*.{ext})",
        "All Files (*)"
    ]

    if rt == ResourceType.SQB:
        filters.insert(1, "JSON files *.json (*.json)")

    return filters


def get_import_func(path: str, rt: ResourceType) -> Callable:
    if rt == ResourceType.SQB:
        if __is_json(path):
            return lambda p, rn, _: try_import_squib_from_json(p, rn)
        else:
            try_import_raw_resource
    return try_import_raw_resource


def try_import_raw_resource(
    path: str,
    rn: int,
    rt: ResourceType
) -> Tuple[List[ImportIssue], Optional[InMemoryResource]]:
    is_headerless = stfed.model.is_headerless(stfed.model.ResourceType(rt))
    res_header, errors = stfed.repos.resources.validate_res_header(path)

    if is_headerless and len(errors) == 0:
        msg = f'Header {res_header} found in a headerless resource type.'
        return [ImportIssue(Severity.Critical, msg)], None
    elif not is_headerless and len(errors) > 0:
        return errors, None
    elif not is_headerless and res_header is not None and res_header.resource_type != rt.value:
        msg = f'Resource type expected: {rt.name} but found {stfed.model.ResourceType(res_header.resource_type).name}.'
        return [ImportIssue(Severity.Critical, msg)], None

    new_resource = stfed.repos.resources.load_single_resource_file_resource(
        path, is_headerless, rn, rt)
    new_resource = dataclasses.replace(
        new_resource,
        source_file=stfed.repos.resources.resources_repo_instance.source_path())

    m = stfed.factories.factory_methods.factory_method_for_resource(new_resource)
    if m is not None:
        try:
            m(new_resource)
        except Exception:
            msg = f"Data in the imported file does not look like a {rt.name} resource and could be corrupted"
            return [ImportIssue(Severity.Warning, msg)], new_resource
    return [], new_resource


def try_import_squib_from_json(
    path: str,
    rn: int
) -> Tuple[List[ImportIssue], Optional[InMemoryResource]]:
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

    found_rns = set(d['rn'] for d in list_of_dicts)
    if len(found_rns) > 1:
        issues.append(
            ImportIssue(
                Severity.Critical,
                "Multiple resource numbers found in the file."))
        return issues, []

    sqb = stfed.factories.sqb.import_json(content)[0]
    wrapped_resource = stfed.model.InMemoryResource(
        rn,
        stfed.model.ResourceType.SQB.value,
        0,
        0,
        stfed.factories.sqb.dump(sqb))
    return [], wrapped_resource


def __is_json(path):
    try:
        with open(path, 'r') as f:
            json.load(f)
    except:
        return False
    return True
