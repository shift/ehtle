"""Frozen 0.6 engine. Replays traces recorded under protocol 0.6 exactly.

Frozen because protocol 0.7 changed what the published view contains. A trace is evidence of what
the subject was shown; replaying it through a newer engine would silently reinterpret it. This
package is never edited. See `docs/CORRECTION_POLICY.md` §1.
"""
