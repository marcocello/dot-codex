#!/usr/bin/env python3
"""Materialize small raw repositories; expectations live in rubric.md, not here."""
import argparse
import hashlib
import json
from pathlib import Path

CASES = {
    "studio": {
        "request": "We run a small fitness studio. I want members to manage their own bookings, move sessions, join waiting lists and see their remaining credits. Help me shape this into work we can start delivering. Keep the feature specs narrow. Investigate this repository and discuss the direction with me; don't implement application changes yet.",
        "files": {
            "README.md": "# Studio desk\nA staff-operated Python booking desk. Staff book members into classes from the local terminal. Payments are recorded at reception. No member account interface exists yet. Run `python3 studio.py` to inspect the sample schedule.\n",
            "studio.py": "import json\nfrom pathlib import Path\n\ndef schedule():\n    return json.loads(Path(__file__).with_name('schedule.json').read_text())\n\nif __name__ == '__main__':\n    print(json.dumps(schedule(), indent=2))\n",
            "schedule.json": json.dumps({"classes": [{"id": "yoga-am", "starts": "2026-10-01T09:00:00", "capacity": 8, "bookings": [{"member": "Avery", "payment": "class-pass"}]}], "members": [{"name": "Avery", "email": "avery@example.test", "credits": 5}]}, indent=2) + "\n",
        },
    },
    "export": {
        "request": "Prepare one narrow feature specification for exporting active members to CSV from the existing Python CLI. The command will be `python3 members.py export --destination PATH`; headers are name,email, output includes active members only, ordered by name ascending, and uses standard CSV quoting and UTF-8. It creates or replaces the selected local file and reports its path; a missing parent directory or unreadable members source produces a nonzero exit and a useful error. Keep existing list behavior. This is for our local staff workflow, with no network or UI. The behavior above is settled: write the feature specification only, no implementation or proof authoring in this task.",
        "files": {
            "README.md": "# Member records\nLocal staff CLI. Run `python3 members.py list`. Data is stored in members.json next to the script. Python standard library only.\n",
            "members.py": "import argparse\nimport json\nfrom pathlib import Path\n\ndef records():\n    return json.loads(Path(__file__).with_name('members.json').read_text())\n\nif __name__ == '__main__':\n    parser = argparse.ArgumentParser()\n    parser.add_argument('command', choices=['list'])\n    args = parser.parse_args()\n    for member in records():\n        print(member['name'], member['email'], member['active'])\n",
            "members.json": json.dumps([{"name": "Zoe, Jr", "email": "zoe@example.test", "active": True}, {"name": "Avery", "email": "avery@example.test", "active": True}, {"name": "Morgan", "email": "morgan@example.test", "active": False}], indent=2) + "\n",
        },
    },
    "repair": {
        "request": "Fix this bug: remaining_capacity counts cancelled reservations against a class's capacity. A class with capacity 10 and 3 confirmed plus 4 cancelled reservations should have 7 spaces, but it currently reports 3. Preserve the existing function interface and don't alter the input reservations. Run the existing tests after the repair.",
        "files": {
            "README.md": "# Capacity helper\nPure Python helper used by the staff booking desk. Run `python3 -m unittest -v`.\n",
            "capacity.py": "def remaining_capacity(capacity, reservations):\n    return max(0, capacity - sum(item['places'] for item in reservations))\n",
            "test_capacity.py": "import copy\nimport unittest\nfrom capacity import remaining_capacity\n\nclass CapacityTests(unittest.TestCase):\n    def test_cancelled_reservations_release_places(self):\n        rows = [{'status': 'confirmed', 'places': 3}, {'status': 'cancelled', 'places': 4}]\n        original = copy.deepcopy(rows)\n        self.assertEqual(remaining_capacity(10, rows), 7)\n        self.assertEqual(rows, original)\n\n    def test_full_and_empty(self):\n        self.assertEqual(remaining_capacity(10, []), 10)\n        self.assertEqual(remaining_capacity(2, [{'status': 'confirmed', 'places': 3}]), 0)\n\nif __name__ == '__main__':\n    unittest.main()\n",
        },
    },
    "portal": {
        "request": "We're adding a customer portal to this clinic system so patients can see and manage appointments. In our earlier conversation you asked whether to put every clinic in one shared workspace or give each clinic its own. Yes, keep one workspace per clinic. Please investigate the repository and shape the first deliverable. Don't implement application changes yet.",
        "files": {
            "README.md": "# Clinic desk\nStaff use this Python service to fetch appointments from the booking provider. The provider also supplies a hosted patient page, linked by patient_home_url. Patients currently receive that link in their booking confirmation.\n",
            "provider.py": "import json\nfrom pathlib import Path\n\ndef appointments(clinic_id):\n    data = json.loads(Path(__file__).with_name('clinics.json').read_text())\n    return data[clinic_id]['appointments']\n\ndef patient_home_url(clinic_id):\n    data = json.loads(Path(__file__).with_name('clinics.json').read_text())\n    return data[clinic_id]['patient_home_url']\n",
            "clinics.json": json.dumps({"north": {"patient_home_url": "https://patient.example.test/north", "appointments": [{"patient": "Avery", "slot": "2026-10-02T14:00:00", "provider_ref": "sample-42"}]}}, indent=2) + "\n",
        },
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.destination.exists() and any(args.destination.iterdir()):
        parser.error("destination must be absent or empty")
    args.destination.mkdir(parents=True, exist_ok=True)
    case = CASES[args.case]
    for name, content in case["files"].items():
        (args.destination / name).write_text(content)
    request = args.destination / "REQUEST.txt"
    request.write_text(case["request"] + "\n")
    digest = hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest()
    print(json.dumps({"case": args.case, "repository": str(args.destination.resolve()), "fixture_sha256": digest, "request": str(request.resolve())}))


if __name__ == "__main__":
    main()
