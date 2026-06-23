from spreadsheet.spreadsheet import RECORD_NOTE_GENRES, RecordGenre, Sheet


class FakeCell:
    """Minimal stand-in for a pygsheets header cell (only col and note are read)."""

    def __init__(self, col, note=None):
        self.col = col
        self.note = note


class TestRecordColumns:
    """Extract dated war/donation columns from the header row.

    Equivalence classes: war note, donation note, undated header note, empty cell,
    prefix without a date token.
    """

    def test_extracts_war_and_donation_in_column_order(self):
        cells = [
            FakeCell(1, None),
            FakeCell(4, "首領 3\n副首 2"),  # role-header note -> ignored
            FakeCell(5, "結算日 20260518"),
            FakeCell(6, "統計日 20260602"),
            FakeCell(7, None),  # empty last column -> ignored
        ]
        assert Sheet._record_columns(cells) == [
            (5, RecordGenre.WAR, "20260518"),
            (6, RecordGenre.DONATE, "20260602"),
        ]

    def test_ignores_prefix_without_date(self):
        assert Sheet._record_columns([FakeCell(5, "結算日")]) == []


class TestLatestWarDate:
    """Right-most war date, used as the back-fill cutoff.

    Equivalence classes: multiple wars, donation interleaved, no war at all.
    """

    def test_returns_rightmost_war(self):
        cols = [(5, RecordGenre.WAR, "20260511"), (7, RecordGenre.WAR, "20260518")]
        assert Sheet._latest_war_date(cols) == "20260518"

    def test_ignores_donations(self):
        cols = [(5, RecordGenre.WAR, "20260518"), (6, RecordGenre.DONATE, "20260602")]
        assert Sheet._latest_war_date(cols) == "20260518"

    def test_no_war_returns_epoch(self):
        assert Sheet._latest_war_date([(5, RecordGenre.DONATE, "20260602")]) == "00000000"


class TestLeadingUnrecorded:
    """Count newest-first races newer than the latest recorded war.

    Equivalence classes: some new, none new, all new, empty.
    """

    def test_counts_new_wars(self):
        dates = ["20260608", "20260601", "20260525", "20260518", "20260511"]
        assert Sheet._leading_unrecorded(dates, "20260518") == 3

    def test_none_new(self):
        assert Sheet._leading_unrecorded(["20260518", "20260511"], "20260518") == 0

    def test_all_new(self):
        assert Sheet._leading_unrecorded(["20260608", "20260601"], "00000000") == 2

    def test_empty(self):
        assert Sheet._leading_unrecorded([], "20260518") == 0


class TestInsertColForDate:
    """Column index where a back-filled war column is inserted to stay date-ordered.

    Equivalence classes: before a later-dated column, append when newest, before the
    first record, no existing records.
    """

    def test_inserts_before_later_donation(self):
        cols = [(5, RecordGenre.WAR, "20260518"), (6, RecordGenre.DONATE, "20260602")]
        assert Sheet._insert_col_for_date(cols, "20260525", append_col=7) == 6

    def test_newest_appends(self):
        cols = [(5, RecordGenre.WAR, "20260518"), (6, RecordGenre.DONATE, "20260602")]
        assert Sheet._insert_col_for_date(cols, "20260608", append_col=7) == 7

    def test_oldest_inserts_before_first(self):
        cols = [(5, RecordGenre.WAR, "20260525"), (6, RecordGenre.DONATE, "20260602")]
        assert Sheet._insert_col_for_date(cols, "20260518", append_col=7) == 5

    def test_empty_appends(self):
        assert Sheet._insert_col_for_date([], "20260608", append_col=5) == 5


class TestBackfillRegression:
    """Regression for the reported bug: a donation dated newer than older un-recorded
    wars must not block their back-fill.

    Previously update_racelog used the right-most record (a donation) as the cutoff,
    so only the single war newer than that donation was filled. The cutoff must be the
    latest WAR date instead.
    """

    def test_donation_does_not_truncate_backfill(self):
        record_columns = [
            (5, RecordGenre.WAR, "20260518"),
            (6, RecordGenre.DONATE, "20260602"),  # right-most column is a donation
        ]
        cutoff = Sheet._latest_war_date(record_columns)
        assert cutoff == "20260518"  # the war date, not the donation 20260602

        racelog_dates = ["20260608", "20260601", "20260525", "20260518", "20260511"]
        # All three wars after 0518 get filled, not just the one newer than the donation.
        assert Sheet._leading_unrecorded(racelog_dates, cutoff) == 3


class TestFindLatestRecord:
    """Right-most record found by the donation flow's header scan.

    Regression: update_donations looked up wars with the prefix "發起日", which is
    never written (wars are noted "結算日"). A war column at the right edge was then
    invisible, so a new donation overwrote it. Both readers and writers now share
    RECORD_NOTE_GENRES, so the prefixes cannot drift.

    Equivalence classes: right-most column is a war, no record at all.
    """

    def test_recognizes_rightmost_war_column(self):
        cells = [
            FakeCell(5, "統計日 20260610"),
            FakeCell(6, "結算日 20260613"),  # war is the right-most record
            FakeCell(7, None),  # empty last column
        ]
        genre, date, offset = Sheet._find_latest_record(cells, RECORD_NOTE_GENRES, total_cols=7)
        assert genre == RecordGenre.WAR
        assert date == "20260613"
        assert offset == 1  # 7 - 6

    def test_no_record_returns_unknown(self):
        cells = [FakeCell(4, "首領 3\n副首 2"), FakeCell(7, None)]
        genre, date, offset = Sheet._find_latest_record(cells, RECORD_NOTE_GENRES, total_cols=7)
        assert genre == RecordGenre.UNKNOWN
        assert date is None
