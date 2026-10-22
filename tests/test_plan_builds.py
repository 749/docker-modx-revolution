import json
import unittest
from io import BytesIO
from unittest.mock import patch

from scripts.plan_builds import build_matrix, fetch_tags, latest_per_major


class BuildPlanTests(unittest.TestCase):
    def setUp(self):
        self.tags = [
            "v2.8.9-pl", "v3.2.4-pl", "v2.9.0-rc1", "v2.8.10-pl",
            "v3.10.0-pl", "v1.9.99-pl", "v3.10.1-beta", "v2.7.99-pl",
        ]

    def test_selects_highest_stable_minor_and_patch_per_major(self):
        self.assertEqual(latest_per_major(self.tags), {2: (2, 8, 10), 3: (3, 10, 0)})

    def test_scheduled_and_manual_runs_publish_all_major_lines(self):
        for event in ("schedule", "workflow_dispatch"):
            with self.subTest(event=event):
                entries = build_matrix(self.tags, event, "refs/heads/main", "example/modx")["include"]
                self.assertEqual([entry["version"] for entry in entries], ["2.8.10", "3.10.0"])
                self.assertEqual(entries[0]["tags"].splitlines(), [
                    "example/modx:2.8.10", "example/modx:2.8", "example/modx:2",
                ])
                self.assertEqual(entries[1]["tags"].splitlines(), [
                    "example/modx:3.10.0", "example/modx:3.10", "example/modx:3", "example/modx:latest",
                ])

    def test_main_push_updates_all_majors_and_edge_from_newest_major(self):
        entries = build_matrix(self.tags, "push", "refs/heads/main", "example/modx")["include"]
        self.assertEqual([entry["major"] for entry in entries], ["2", "3"])
        self.assertNotIn("example/modx:edge", entries[0]["tags"])
        self.assertEqual(entries[1]["tags"].splitlines()[-2:], ["example/modx:latest", "example/modx:edge"])

    def test_fails_if_a_major_line_disappears(self):
        with self.assertRaisesRegex(ValueError, "Missing a stable MODX major"):
            latest_per_major(["v2.8.9-pl", "v4.0.0-pl"])

    def test_new_major_gets_its_own_tags_and_latest(self):
        entries = build_matrix(self.tags + ["v4.0.1-pl"], "schedule", "refs/heads/main", "example/modx")["include"]
        self.assertEqual([entry["major"] for entry in entries], ["2", "3", "4"])
        self.assertEqual(entries[-1]["tags"].splitlines(), [
            "example/modx:4.0.1", "example/modx:4.0", "example/modx:4", "example/modx:latest",
        ])
        self.assertNotIn("example/modx:latest", entries[1]["tags"])

    def test_fetches_beyond_first_page(self):
        requests = []

        def open_url(request, timeout):
            requests.append(request.full_url)
            names = ["v3.2.4-pl"] * 100 if len(requests) == 1 else ["v2.8.9-pl"]
            return BytesIO(json.dumps([{"name": name} for name in names]).encode())

        with patch("scripts.plan_builds.time.sleep"):
            tags = fetch_tags(open_url)
        self.assertEqual(len(tags), 101)
        self.assertIn("page=2", requests[1])
        self.assertEqual(latest_per_major(tags), {2: (2, 8, 9), 3: (3, 2, 4)})


if __name__ == "__main__":
    unittest.main()
