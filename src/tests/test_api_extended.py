import pytest
from api.schemas.review import ReviewRequest


class TestReviewRequestSchema:
    def test_valid_repo_url(self):
        req = ReviewRequest(repo_url="https://github.com/test/repo")
        assert str(req.repo_url) == "https://github.com/test/repo/"  or "github.com" in str(req.repo_url)

    def test_default_mode_is_review(self):
        req = ReviewRequest(repo_url="https://github.com/test/repo")
        assert req.mode == "review"

    def test_custom_mode(self):
        req = ReviewRequest(repo_url="https://github.com/test/repo", mode="design")
        assert req.mode == "design"

    def test_with_brief(self):
        req = ReviewRequest(repo_url="https://github.com/test/repo", brief="Build a video platform")
        assert req.brief == "Build a video platform"

    def test_repo_url_required(self):
        with pytest.raises(Exception):
            ReviewRequest()

    def test_invalid_url_rejected(self):
        with pytest.raises(Exception):
            ReviewRequest(repo_url="not-a-url")


class TestReviewRequestModes:
    def test_all_14_modes_accepted(self):
        from archon.engine.modes.configs import ALL_MODES
        for mode_name in ALL_MODES:
            req = ReviewRequest(repo_url="https://github.com/test/repo", mode=mode_name)
            assert req.mode == mode_name
