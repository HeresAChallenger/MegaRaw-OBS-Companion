"""Offline tests for the companion. No API key or network access required."""
import json
import sys
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mega_raw_obs as app


class MetadataTests(unittest.TestCase):
    def test_is_megadrive(self):
        self.assertTrue(app.is_megadrive({'ConsoleName': 'Sega Mega Drive'}))
        self.assertTrue(app.is_megadrive({'consoleName': 'Sega Genesis'}))
        self.assertFalse(app.is_megadrive({'ConsoleName': 'Super Nintendo'}))

    def test_achievement_fields(self):
        item = {'AchievementID': 123, 'Date': '2026-10-31 14:00:00',
                'HardcoreMode': 0, 'BadgeName': '12345',
                'Title': 'Test Achievement', 'Points': 5,
                'ConsoleName': 'Mega Drive', 'GameTitle': 'Test Game'}
        e = app.event_from_ra(item)
        self.assertEqual(e['points'], 5)
        self.assertEqual(e['title'], 'Test Achievement')
        self.assertEqual(e['game'], 'Test Game')
        self.assertEqual(e['badge'], 'https://retroachievements.org/Badge/12345.png')
        self.assertEqual(app.identity(item), ('123', '2026-10-31 14:00:00', '0'))

    def test_untrusted_badge_domain_rejected(self):
        self.assertEqual(app.badge_url({'BadgeURL': 'https://example.com/tracker.png'}), '')
        self.assertEqual(app.badge_url({'BadgeURL': '//example.com/another.png'}), '')
        self.assertEqual(app.badge_url({'BadgeName': 'bad<>path'}), '')

    def test_demo_audio_is_wav(self):
        with wave.open(str(app.SOUND_PATH), 'rb') as f:
            self.assertEqual(f.getframerate(), 48000)
            self.assertEqual(f.getnchannels(), 2)
            self.assertGreater(f.getnframes(), 5000)

    def test_overlay_uses_local_queue(self):
        self.assertIn('/api/events?after=', app.OVERLAY)
        self.assertIn('250', app.OVERLAY)
        self.assertIn('/audio/alert.wav', app.OVERLAY)


if __name__ == '__main__':
    unittest.main()
