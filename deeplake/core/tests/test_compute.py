import pytest
from deeplake.util.compute import get_compute_provider

schedulers = ["threaded", "processed", "serial"]
all_schedulers = pytest.mark.parametrize("scheduler", schedulers)


@pytest.mark.slow
@pytest.mark.flaky
@all_schedulers
def test_compute_with_progress_bar(scheduler):
    def f(pg_callback, x):
        pg_callback(1)
        return x * 2

    compute = get_compute_provider(scheduler=scheduler, num_workers=2)
    try:
        r = compute.map_with_progress_bar(f, range(1000), 1000)

        assert r is not None
        assert len(r) == 1000

    finally:
        compute.close()
