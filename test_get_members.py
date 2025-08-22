"""Simple test runner to call the Project Membership tool/service for every project.

This script uses the project's `config` to create a Redmine client, then
uses `ProjectService` and `ProjectMembershipService` to retrieve all projects
and list membership for each one.

Run: python test_get_members.py
"""

from config.config import config
from services import ProjectService, ProjectMembershipService


def main():
    try:
        redmine = config.create_client()
    except Exception as e:
        print(f"Failed to create Redmine client: {e}")
        return

    project_service = ProjectService(redmine)
    membership_service = ProjectMembershipService(redmine)

    proj_result = project_service.get_all()
    if not proj_result.success:
        print(f"Failed to retrieve projects: {proj_result.message} - {getattr(proj_result, 'error', '')}")
        return

    projects = proj_result.data.get("projects", []) if proj_result.data else []
    if not projects:
        print("No projects found.")
        return

    total_projects = len(projects)
    print(f"Found {total_projects} project(s). Testing memberships for each...\n")

    failures = 0
    skipped = 0
    real_count = 0
    import json
    from pprint import pformat

    def dump_project_info(project_obj):
        """Attempt to extract everything we can from the Project object."""
        info = {}

        # Basic mapped info from the service (already converted to dict)
        try:
            pid = project_obj.get("id")
        except Exception:
            pid = getattr(project_obj, "id", None)

        info["id"] = pid
        info["repr"] = repr(project_obj)

        # If object supports dict-like access return that
        try:
            if isinstance(project_obj, dict):
                info["as_dict"] = project_obj
        except Exception:
            pass

        # Try to inspect attributes available on the real Redmine resource (if present)
        try:
            # Many Redmine resources expose _decoded_attrs or _original
            decoded = getattr(project_obj, "_decoded_attrs", None)
            if decoded:
                info["_decoded_attrs"] = decoded
        except Exception:
            pass

        try:
            raw = {a: getattr(project_obj, a) for a in dir(project_obj) if not a.startswith("_")}
            # Convert non-serializable values to string
            serializable = {}
            for k, v in raw.items():
                try:
                    json.dumps(v)
                    serializable[k] = v
                except Exception:
                    serializable[k] = str(v)
            info["dir_attrs"] = serializable
        except Exception as e:
            info["dir_error"] = str(e)

        return info


    import re
    from concurrent.futures import ThreadPoolExecutor, TimeoutError

    # Heuristic to detect time-off / non-project items
    timeoff_keywords = re.compile(r"vac(aci[oó]nes?|ation)|enfermedad|illness|vacation|permiso|incapacidad|holiday|ausencia", re.I)

    # When True the script will only retrieve and print detailed
    # information for projects classified as real/billable. Time-off
    # projects will be skipped early (no raw fetch, no dumps, no membership calls).
    ONLY_REAL = True

    executor = ThreadPoolExecutor(max_workers=4)
    # Keep track of submitted futures so we can try to cancel them on timeout
    futures = []

    for project in projects:
        project_id = project.get("id")
        project_name = project.get("name", f"Project {project_id}")
        print(f"== Project: {project_name} (ID: {project_id}) ==")

        # Quick pre-check: if name/identifier/description clearly match
        # time-off keywords and ONLY_REAL is enabled, skip the project
        try:
            identifier_q = str(project.get('identifier', '')).lower()
            desc_q = str(project.get('description', '')).lower()
            if ONLY_REAL and timeoff_keywords.search(identifier_q or '') or timeoff_keywords.search(desc_q or '') or (ONLY_REAL and timeoff_keywords.search(project_name)):
                print('  Skipped (quick keyword match for time-off).')
                skipped += 1
                print()
                continue
        except Exception:
            pass

        # Dump all available info for inspection (only for projects we didn't skip)
        proj_info = dump_project_info(project)
        print("-- Project info dump --")
        try:
            print(pformat(proj_info))
        except Exception:
            print(str(proj_info))

        # Try to fetch the raw Redmine resource to inspect additional fields
        extra = {}
        try:
            raw_proj = redmine.project.get(project_id)
            raw_decoded = getattr(raw_proj, "_decoded_attrs", None)
            raw_custom = getattr(raw_proj, "custom_fields", None)

            extra = {}
            extra["type"] = type(raw_proj).__name__
            if raw_decoded:
                extra["_decoded_attrs_keys"] = list(raw_decoded.keys())
            if raw_custom:
                try:
                    extra["custom_fields"] = [{"id": cf.id, "name": getattr(cf, 'name', str(cf)), "value": getattr(cf, 'value', str(cf))} for cf in raw_custom]
                except Exception:
                    extra["custom_fields"] = str(raw_custom)

            # Try to expose enabled_modules and trackers
            try:
                extra["enabled_modules"] = [m.name if hasattr(m, 'name') else str(m) for m in getattr(raw_proj, 'enabled_modules', [])]
            except Exception:
                extra["enabled_modules"] = "<unavailable>"

            try:
                extra["trackers"] = [t.name if hasattr(t, 'name') else str(t) for t in getattr(raw_proj, 'trackers', [])]
            except Exception:
                extra["trackers"] = "<unavailable>"

            print("-- Raw Redmine project extra fields --")
            print(pformat(extra))
        except Exception as e:
            print(f"-- Failed to fetch raw project resource: {e}")

        # Classifier: decide whether this is a real/billable project or a
        # time-off / non-billable project. Uses simple weighted rules so you
        # can tune thresholds later.
        def classify_project(project_obj, extra_fields):
            score = 0
            reasons = []

            name = str(project_obj.get('name', '')).lower()
            identifier = str(project_obj.get('identifier', '')).lower()
            desc = str(project_obj.get('description', '')).lower()

            # keyword match (strong signal)
            if timeoff_keywords.search(name) or timeoff_keywords.search(identifier) or timeoff_keywords.search(desc):
                score += 5
                reasons.append('keyword match (name/identifier/description)')

            # custom_fields from extra_fields is a list of dicts with name/value
            tipo = None
            horas = None
            cf_list = extra_fields.get('custom_fields') if extra_fields else None
            if isinstance(cf_list, list):
                for cf in cf_list:
                    try:
                        k = str(cf.get('name', '')).lower()
                        v = cf.get('value')
                    except Exception:
                        continue
                    if 'tipo' in k:
                        tipo = str(v).lower()
                    if 'horas presupuestadas' in k or 'horas presup' in k:
                        horas = str(v)

            if tipo:
                if 'sin presupuesto' in tipo or tipo.strip() == 'sin presupuesto':
                    score += 4
                    reasons.append(f"custom_field Tipo de proyecto='{tipo}'")

            # placeholder huge hours or absent/placeholder values -> likely non-billable
            if horas:
                h = horas.strip()
                if h in ('', '-', '0'):
                    score += 2
                    reasons.append(f"Horas Presupuestadas='{horas}' (empty/placeholder)")
                else:
                    # extremely large sentinel value used in your dump
                    if len(h) > 10 or h.isdigit() and int(h) > 10**9:
                        score += 3
                        reasons.append(f"Horas Presupuestadas placeholder/sentinel='{horas}'")

            # trackers or enabled modules hints
            trackers = extra_fields.get('trackers') if extra_fields else None
            enabled = extra_fields.get('enabled_modules') if extra_fields else None
            if trackers and any('falta' in t.lower() for t in trackers if isinstance(t, str)):
                score += 3
                reasons.append('tracker contains "Falta"')
            if enabled and any('work_time' == m for m in enabled if isinstance(m, str)):
                score += 2
                reasons.append('enabled_modules contains work_time')

            # Decision threshold
            threshold = 5
            classification = 'time-off/non-billable' if score >= threshold else 'real/billable'
            return classification, score, reasons

        try:
            classification, cscore, creasons = classify_project(project, extra)
            print(f"-- Classification: {classification} (score={cscore})")
            if creasons:
                print("   Reasons:")
                for r in creasons:
                    print(f"    - {r}")
        except Exception:
            # If classifier fails treat project as real to avoid skipping data
            classification = 'real/billable'

        # If classification indicates a time-off/non-billable project, skip
        # membership retrieval to avoid unnecessary API calls and timeouts.
        if classification.startswith('time-off'):
            print('  Skipping membership retrieval for non-billable project.')
            skipped += 1
            print()
            continue
        else:
            real_count += 1

        # Then test membership retrieval so we still exercise the original behavior
        # If project looks like a time-off project, mark it and still try memberships optionally
        try:
            identifier = str(project.get('identifier', '')).lower()
            desc = str(project.get('description', '')).lower()
            if timeoff_keywords.search(identifier) or timeoff_keywords.search(desc) or timeoff_keywords.search(project_name):
                print("-- Heuristic: looks like a time-off / non-billable project (identifier/description match keywords)")
        except Exception:
            pass

        # Retrieve memberships with a timeout to avoid hanging
        future = executor.submit(membership_service.get_by_project, project_id)
        futures.append(future)
        try:
            res = future.result(timeout=10)
        except TimeoutError:
            print("  ERROR: membership retrieval timed out (10s)")
            failures += 1
            # Attempt to cancel the underlying task; if it is already running
            # cancel() will return False, but we still avoid waiting on the
            # executor later by shutting it down without waiting.
            try:
                future.cancel()
            except Exception:
                pass
            print()
            continue
        except Exception as e:
            print(f"  ERROR calling membership service: {e}")
            failures += 1
            print()
            continue

        if not res.success:
            print(f"  ❌ {res.message} - {getattr(res, 'error', '')}")
            failures += 1
            print()
            continue

        memberships = res.data.get("memberships", []) if res.data else []
        if not memberships:
            print("  No members found for this project.")
            print()
            continue

        for m in memberships:
            uid = m.get("user_id")
            uname = m.get("user")
            roles = m.get("roles", [])
            roles_str = ", ".join(roles) if roles else "(no roles)"
            print(f"  - ID: {uid} - Name: {uname} - Roles: {roles_str}")

        print(f"  Total members: {len(memberships)}\n")

    # Shutdown the executor without waiting for running tasks so the script
    # can exit promptly even if some membership calls are still in progress.
    try:
        executor.shutdown(wait=False)
    except TypeError:
        # Older python versions may not support wait=False; fall back to
        # a non-blocking pattern by attempting to cancel pending futures.
        for f in futures:
            try:
                f.cancel()
            except Exception:
                pass

    print(f"Done. Projects tested: {total_projects}. Real: {real_count}. Skipped: {skipped}. Failures: {failures}.")


if __name__ == "__main__":
    main()
