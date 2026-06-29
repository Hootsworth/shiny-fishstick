import random
import time


class UIChaosMonkey:
    def __init__(self):
        self.latency_delay_ms = 0
        self.chaos_enabled = False

    def enable_chaos(self, enabled: bool = True):
        self.chaos_enabled = enabled

    def set_latency_delay(self, ms: int):
        self.latency_delay_ms = ms

    def inject_latency(self):
        if self.chaos_enabled and self.latency_delay_ms > 0:
            time.sleep(self.latency_delay_ms / 1000.0)

    def mutate_classes(self, classes_str: str) -> str:
        if not self.chaos_enabled or not classes_str:
            return classes_str

        words = classes_str.split()
        if not words:
            return classes_str

        mutated = []
        for w in words:
            # 20% chance to append a chaos suffix string
            if random.random() < 0.2:
                mutated.append(f"{w}-chaos-{random.randint(10, 99)}")
            # 10% chance to omit the tailwind class entirely
            elif random.random() < 0.1:
                continue
            else:
                mutated.append(w)

        return " ".join(mutated)


# Global singleton instance for app state management
chaos_monkey = UIChaosMonkey()
