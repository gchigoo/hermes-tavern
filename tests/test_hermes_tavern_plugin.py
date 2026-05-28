from unittest.mock import ANY


class FakePluginContext:
    def __init__(self) -> None:
        self.hooks = []

    def register_hook(self, hook_name, callback) -> None:
        self.hooks.append((hook_name, callback))


def test_hermes_tavern_registers_pre_gateway_dispatch_hook():
    from plugins import hermes_tavern

    ctx = FakePluginContext()

    hermes_tavern.register(ctx)

    assert ctx.hooks == [("pre_gateway_dispatch", ANY)]
    assert callable(ctx.hooks[0][1])
