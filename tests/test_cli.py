import cli
import commands


class TestParser:
    """Equivalence classes: optional arg present, optional arg absent, dispatch binding."""

    def test_show_racelog_with_count(self):
        parser = cli.build_parser()
        ns = parser.parse_args(["show", "racelog", "5"])
        assert ns.count == 5
        assert ns.func is commands.show_racelog

    def test_show_racelog_no_count(self):
        parser = cli.build_parser()
        ns = parser.parse_args(["show", "racelog"])
        assert ns.count is None
        assert ns.func is commands.show_racelog

    def test_update_donation_with_date(self):
        parser = cli.build_parser()
        ns = parser.parse_args(["update", "donation", "20260501"])
        assert ns.date == "20260501"
        assert ns.func is commands.update_donation

    def test_init_dispatch(self):
        parser = cli.build_parser()
        ns = parser.parse_args(["init"])
        assert ns.func is commands.cmd_init


class TestRunOnce:
    """Equivalence classes: handler invoked with parsed namespace, return value propagated."""

    def test_dispatches_to_handler(self, monkeypatch):
        called = []

        def stub(args, cr, sheet):
            called.append((args, cr, sheet))
            return commands.Status.OK

        monkeypatch.setattr(commands, "show_members", stub)
        parser = cli.build_parser()
        cr_obj, sheet_obj = object(), object()
        status = cli.run_once(parser, ["show", "members"], cr_obj, sheet_obj)
        assert len(called) == 1
        assert called[0][1] is cr_obj
        assert called[0][2] is sheet_obj
        assert status == commands.Status.OK


class TestRepl:
    """Equivalence classes: quit terminates loop, prompt is rendered."""

    def test_quits_on_quit(self, monkeypatch, capsys):
        inputs = iter(["quit"])
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(inputs))
        parser = cli.build_parser()
        cli.repl(parser, object(), object())
        captured = capsys.readouterr()
        assert "❯" in captured.out
