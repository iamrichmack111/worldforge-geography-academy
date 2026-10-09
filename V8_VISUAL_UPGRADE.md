# WorldForge V8 — Motion Academy

This release changes presentation, not the homework API or saved account data.

- Animated gradient hero and slowly moving background geometry
- Refined cards, navigation, quizzes, homework, and flashcards
- Scroll-entry transitions, hover and click feedback
- Motion toggle in the top navigation (saved per browser)
- Respect for operating-system reduced-motion preference
- Updated 3D lab panel styling; terrain rendering logic unchanged

## Start
`PORT=8081 python3 server.py`

Navigate to `http://family.local:8081`. Use a private local network.

## Preserve accounts
Back up and retain your `classroom.sqlite3` database from the old installation. Do not overwrite it with a blank database.

## Verify
`python3 -m unittest discover -s tests -p 'test_*.py'`
`node --check classroom.js && node --check learning-studio.js && node --check motion.js`
