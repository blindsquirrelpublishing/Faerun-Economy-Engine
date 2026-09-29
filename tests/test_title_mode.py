from faerun.webassets import APP_JS


def test_app_title_and_badge_mark_seasonal_mode_in_browser_title():
    text = APP_JS.lower()
    assert 'document.title' in text
    assert 'mode-badge' in text
    assert 'seasonal' in text
    assert 'boot.seasonal_inventory' in text
