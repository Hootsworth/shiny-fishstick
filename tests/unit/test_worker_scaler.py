from unittest.mock import MagicMock

from backend.app.services.worker_scaler import WorkerQueueAutoscaler


def test_worker_scaler_queue_sizing_recommendation(mocker):
    # Mock redis instance client
    mock_redis = MagicMock()
    mock_redis.keys.return_value = ["arq:job:1", "arq:job:2"]
    mock_redis.llen.return_value = 10  # simulate large queue size

    mocker.patch("redis.Redis.from_url", return_value=mock_redis)

    scaler = WorkerQueueAutoscaler()
    stats = scaler.get_queue_stats()

    # Assert correct recommended scale-up trigger
    assert stats["queue_length"] == 10
    assert stats["job_keys_count"] == 2
    assert stats["scale_recommendation"] == "scale_up"
    assert stats["redis_status"] == "connected"
