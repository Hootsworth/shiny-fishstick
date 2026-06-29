from backend.app.services.chaos import UIChaosMonkey


def test_chaos_monkey_class_mutator():
    monkey = UIChaosMonkey()

    classes = "flex items-center justify-between p-4"

    # 1. When chaos is disabled (should return input unmodified)
    monkey.enable_chaos(False)
    res_disabled = monkey.mutate_classes(classes)
    assert res_disabled == classes

    # 2. When chaos is enabled
    monkey.enable_chaos(True)
    res_enabled = monkey.mutate_classes(classes)
    # Since class mutations are probabilistic, some elements may mutate or drop
    assert isinstance(res_enabled, str)

    # 3. Latency config
    monkey.set_latency_delay(10)
    assert monkey.latency_delay_ms == 10
