import argparse
import asyncio
import os
import subprocess
import sys

import yaml
from app.core.database import Base, SessionLocal, engine
from app.models.db_models import Action, Crawl, Project, Workflow
from app.services.crawler import CrawlerService
from app.services.generator import SDKGeneratorService
from app.services.workflow import WorkflowDiscoveryService


def handle_compile(args):
    url = args.url
    out_dir = args.out or "./shared/specs"
    os.makedirs(out_dir, exist_ok=True)

    print(f"🐟 Compiling website actions: {url} -> {out_dir}")

    # Setup local SQLite test database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Pre-cleanup database project
        db.query(Action).delete()
        db.query(Workflow).delete()
        db.query(Crawl).delete()
        db.query(Project).delete()
        db.commit()

        print("[1/4] Registering target project...")
        project = Project(name="CLI Compiled Project", root_url=url)
        db.add(project)
        db.commit()
        db.refresh(project)

        crawl = Crawl(project_id=project.id, status="pending")
        db.add(crawl)
        db.commit()
        db.refresh(crawl)

        print("[2/4] Executing browser analysis crawl (resolving logins & sessions)...")
        crawler = CrawlerService(db, project.id, crawl.id, url)
        asyncio.run(crawler.crawl())

        print("[3/4] Running workflow state transitions discoverer...")
        wf_service = WorkflowDiscoveryService(db, project.id)
        wf_service.discover_and_save()

        print("[4/4] Generating OpenAPI specs, SDK client scripts, and Model Context Protocol servers...")
        sdk_service = SDKGeneratorService(db, project.id)
        sdk_service.generate_all(specs_dir=out_dir)

        actions = db.query(Action).filter(Action.project_id == project.id).all()
        print(f"\n✨ Compilation successful! Discovered {len(actions)} web actions:")
        for act in actions:
            print(f"  - {act.name} (intent: {act.intent}, type: {act.action_type})")

    except Exception as e:
        print(f"❌ Error during compilation: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


def handle_inspect(args):
    spec_path = args.spec_yaml
    if not os.path.exists(spec_path):
        print(f"❌ Error: Spec file not found at '{spec_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(spec_path, "r") as f:
            spec = yaml.safe_load(f)

        from app.services.validator import SpecValidator
        is_valid, errors = SpecValidator.validate_spec(spec)

        print(f"🐟 Shiny Fishstick Spec Inspection: {spec_path}")
        print(f"  Target Website: {spec.get('site')}")
        print(f"  Spec Version: {spec.get('version')}")
        if is_valid:
            print("  Validation Status: ✅ VALID SPECIFICATION")
        else:
            print("  Validation Status: ❌ INVALID SPECIFICATION")
            for err in errors:
                print(f"    - {err}")

        actions = spec.get("actions", {})
        print(f"  Discovered Actions count: {len(actions)}")
        print("\nActions list:")
        for name, details in actions.items():
            print(f"  - {name}:")
            print(f"      Description: {details.get('description')}")
            print(f"      Type: {details.get('action_type')}")
            print(f"      Selector: {details.get('selector')}")
            params = details.get("parameters", [])
            if params:
                print("      Parameters:")
                for p in params:
                    req_str = "required" if p.get("required") else "optional"
                    print(f"        * {p.get('name')} ({p.get('type')}, {req_str})")
    except Exception as e:
        print(f"❌ Error parsing spec file: {e}", file=sys.stderr)
        sys.exit(1)


def handle_validate(args):
    spec_path = args.spec_yaml
    if not os.path.exists(spec_path):
        print(f"❌ Error: Spec file not found at '{spec_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(spec_path, "r") as f:
            spec = yaml.safe_load(f)

        from app.services.validator import SpecValidator
        is_valid, errors = SpecValidator.validate_spec(spec)
        if is_valid:
            print("✅ Spec file is valid!")
            sys.exit(0)
        else:
            print("❌ Spec file contains validation errors:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading/parsing spec file: {e}", file=sys.stderr)
        sys.exit(1)


def handle_serve_mcp(args):
    spec_path = args.spec_yaml
    if not os.path.exists(spec_path):
        print(f"❌ Error: Spec file not found at '{spec_path}'", file=sys.stderr)
        sys.exit(1)

    # Get directory where the spec file is located
    specs_dir = os.path.dirname(os.path.abspath(spec_path))
    mcp_server_path = os.path.join(specs_dir, "mcp_server.py")

    if not os.path.exists(mcp_server_path):
        print(f"❌ Error: MCP Server code not found at '{mcp_server_path}'. Please run compile first.", file=sys.stderr)
        sys.exit(1)

    print(f"🔌 Launching Model Context Protocol (MCP) Server: {mcp_server_path}", file=sys.stderr)
    try:
        # Run generated mcp_server.py directly
        # Since MCP server communicates over stdin/stdout, we must forward them directly
        # Change working directory so local imports from specs_dir work cleanly
        sys.exit(subprocess.run([sys.executable, "mcp_server.py"], cwd=specs_dir).returncode)
    except KeyboardInterrupt:
        print("\n🔌 MCP Server terminated.", file=sys.stderr)
        sys.exit(0)


def handle_test(args):
    spec_path = args.spec_yaml
    if not os.path.exists(spec_path):
        print(f"❌ Error: Spec file not found at '{spec_path}'", file=sys.stderr)
        sys.exit(1)

    specs_dir = os.path.dirname(os.path.abspath(spec_path))
    test_suite_path = os.path.join(specs_dir, "test_sdk.py")

    if not os.path.exists(test_suite_path):
        print(f"❌ Error: Test suite code not found at '{test_suite_path}'. Please run compile first.", file=sys.stderr)
        sys.exit(1)

    print(f"🧪 Executing compiled E2E SDK Test Suite: {test_suite_path}")
    try:
        # Execute generated test suite under pytest
        sys.exit(subprocess.run(["pytest", "-v", "test_sdk.py"], cwd=specs_dir).returncode)
    except Exception as e:
        print(f"❌ Error running test suite: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Shiny Fishstick CLI tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compile Command
    compile_parser = subparsers.add_parser("compile", help="Compile target website actions into a preflight spec")
    compile_parser.add_argument("url", help="Target website base URL")
    compile_parser.add_argument("--out", help="Output specs destination folder path")
    compile_parser.set_defaults(func=handle_compile)

    # Inspect Command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a compiled preflight spec file")
    inspect_parser.add_argument("spec_yaml", help="Path to preflight.yaml spec file")
    inspect_parser.set_defaults(func=handle_inspect)

    # Validate Command
    validate_parser = subparsers.add_parser("validate", help="Validate a compiled preflight spec file structure")
    validate_parser.add_argument("spec_yaml", help="Path to preflight.yaml spec file")
    validate_parser.set_defaults(func=handle_validate)

    # Serve MCP Command
    serve_parser = subparsers.add_parser("serve-mcp", help="Serve target preflight actions over Model Context Protocol")
    serve_parser.add_argument("spec_yaml", help="Path to preflight.yaml spec file")
    serve_parser.set_defaults(func=handle_serve_mcp)

    # Test Command
    test_parser = subparsers.add_parser("test", help="Test site compatibility with the compiled preflight spec")
    test_parser.add_argument("spec_yaml", help="Path to preflight.yaml spec file")
    test_parser.set_defaults(func=handle_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
