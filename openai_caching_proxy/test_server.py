from server import *
from contextlib import closing


def test_prompts():
    with (closing(State())) as state:
        assert len(state.completion('text-curie-001', 'Hello!', stop = ['\n'], n=1)) == 1
