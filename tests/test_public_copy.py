import unittest
from scripts.update_public_copy import updated_blocks


class PublicCopyTest(unittest.TestCase):
    def test_only_known_demo_copy_changes_and_repeated_run_is_empty(self):
        blocks = [{'component': 'hero', 'data': {'subtitle': 'События дают быстрые лиды, статьи закрывают SEO-запросы родителей.', 'title': 'Название клиента'}}]
        updated, count = updated_blocks(blocks)
        self.assertEqual(count, 1)
        self.assertEqual(updated[0]['data']['title'], 'Название клиента')
        self.assertNotEqual(updated, blocks)
        self.assertEqual(updated_blocks(updated), (updated, 0))

    def test_custom_copy_is_preserved(self):
        blocks = [{'component': 'hero', 'data': {'subtitle': 'Наши семейные встречи'}}]
        self.assertEqual(updated_blocks(blocks), (blocks, 0))


class UpcomingEventsTest(unittest.TestCase):
    def test_upcoming_excludes_expired_and_undated_then_sorts_before_limit(self):
        from datetime import date, timedelta
        from types import SimpleNamespace
        from app.utils.content import hydrate_blocks
        today = date.today()
        dates = [today + timedelta(days=5), today - timedelta(days=1), None, today, today + timedelta(days=1)]
        events = [SimpleNamespace(event_date=value) for value in dates]
        result = hydrate_blocks([{'component': 'events_teaser', 'data': {'source': 'upcoming_events', 'limit': 2}}], {'events': events})
        self.assertEqual([e.event_date for e in result[0]['data']['events']], [today, today + timedelta(days=1)])
        self.assertEqual(len(events), 5)
