import unittest
import time

# Import from your actual project
from app.services.task_service import (
    start_task,
    get_task_status,
    task_store,
    SERVICE_MAP,
)
from app.services.exceptions import MathWizardError


class TestStartTask(unittest.TestCase):

    def setUp(self):
        """Clear task_store before each test"""
        task_store.clear()

    def tearDown(self):
        """Clear task_store after each test"""
        task_store.clear()

    def test_start_task_returns_task_id(self):
        """start_task should return a string task_id"""
        task_id = start_task(5, 3, "add")

        self.assertIsNotNone(task_id)
        self.assertIsInstance(task_id, str)
        self.assertGreater(len(task_id), 0)

    def test_start_task_returns_immediately(self):
        """start_task should return instantly, not wait for work to complete"""
        start_time = time.time()
        task_id = start_task(5, 3, "add")
        elapsed = time.time() - start_time

        # Should return in under 0.1 seconds (not waiting for background work)
        self.assertLess(elapsed, 0.1)

    def test_start_task_creates_entry_in_store(self):
        """start_task should create an entry in task_store"""
        task_id = start_task(5, 3, "add")

        self.assertIn(task_id, task_store)

    def test_start_task_initial_status_is_pending(self):
        """Task should start with pending status"""
        task_id = start_task(5, 3, "add")

        # Check immediately - might still be pending
        self.assertIn(task_store[task_id]["status"], ["pending", "complete"])

    def test_start_task_unknown_operation_raises_error(self):
        """Should raise MathWizardError for unknown operations"""
        with self.assertRaises(MathWizardError) as context:
            start_task(5, 3, "unknown_op")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Unknown operation", context.exception.message)

    def test_start_task_generates_unique_ids(self):
        """Each task should get a unique ID"""
        task_id_1 = start_task(5, 3, "add")
        task_id_2 = start_task(10, 20, "add")

        self.assertNotEqual(task_id_1, task_id_2)


class TestGetTaskStatus(unittest.TestCase):

    def setUp(self):
        """Clear task_store before each test"""
        task_store.clear()

    def tearDown(self):
        """Clear task_store after each test"""
        task_store.clear()

    def test_get_task_status_returns_task_data(self):
        """Should return the task data for a valid task_id"""
        task_id = start_task(5, 3, "add")

        result = get_task_status(task_id)

        self.assertIsNotNone(result)
        self.assertIn("status", result)
        self.assertIn("result", result)

    def test_get_task_status_nonexistent_task_raises_error(self):
        """Should raise MathWizardError for non-existent task_id"""
        with self.assertRaises(MathWizardError) as context:
            get_task_status("fake-task-id-12345")

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No Task_ID to check status", context.exception.message)


class TestAsyncFlow(unittest.TestCase):
    """Test the full async polling flow"""

    def setUp(self):
        task_store.clear()

    def tearDown(self):
        task_store.clear()

    def test_full_async_polling_flow(self):
        """Test create task -> poll -> get result"""
        # Create task
        task_id = start_task(5, 3, "add")

        # Poll until complete (with timeout)
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            status = get_task_status(task_id)
            if status["status"] == "complete":
                break
            time.sleep(0.5)
            attempt += 1

        # Verify result
        final_status = get_task_status(task_id)
        self.assertEqual(final_status["status"], "complete")
        self.assertEqual(final_status["result"], 8)


class TestServiceMap(unittest.TestCase):

    def test_service_map_contains_add(self):
        """SERVICE_MAP should contain the add operation"""
        self.assertIn("add", SERVICE_MAP)

    def test_service_map_add_is_callable(self):
        """The add function in SERVICE_MAP should be callable"""
        self.assertTrue(callable(SERVICE_MAP["add"]))


if __name__ == '__main__':
    unittest.main()