import pandas as pd
import numpy as np
import pytest
from tools.pattern_helper import calculate_ichimoku, identify_multi_tops, identify_multi_bottoms


# Test data for calculate_ichimoku
@pytest.fixture
def ichimoku_data():
    data = pd.DataFrame({
        'high': np.random.random(100) + 100,
        'close': np.random.random(100) + 100,
        'low': np.random.random(100) + 99,
    })
    return data


# Test data for identify_multi_tops and identify_multi_bottoms
@pytest.fixture
def tops_and_bottoms_data():
    data = pd.DataFrame({
        'close': [100, 102, 101, 103, 100, 104, 99, 105, 98, 106],
        'open': [99, 101, 100, 102, 99, 103, 98, 104, 97, 105],
    })
    return data


# Tests for calculate_ichimoku
def test_calculate_ichimoku(ichimoku_data):
    df = calculate_ichimoku(ichimoku_data)
    assert 'tenkan_sen' in df.columns
    assert 'kijun_sen' in df.columns
    assert 'senkou_span_a' in df.columns
    assert 'senkou_span_b' in df.columns
    assert 'chikou_span' in df.columns
    assert not df['tenkan_sen'].isnull().all()
    assert not df['kijun_sen'].isnull().all()


# Tests for identify_multi_tops
def test_identify_multi_tops_no_tops(tops_and_bottoms_data):
    touches, resistance_value = identify_multi_tops(tops_and_bottoms_data, order=5)
    assert touches is None
    assert resistance_value is None


def test_identify_multi_tops_with_tops(tops_and_bottoms_data):
    touches, resistance_value = identify_multi_tops(tops_and_bottoms_data, tolerance=0.1, order=1)
    assert touches is not None
    assert resistance_value is not None


# Tests for identify_multi_bottoms
def test_identify_multi_bottoms_no_bottoms(tops_and_bottoms_data):
    touches, support_value = identify_multi_bottoms(tops_and_bottoms_data, order=5)
    assert touches is None
    assert support_value is None


def test_identify_multi_bottoms_with_bottoms(tops_and_bottoms_data):
    touches, support_value = identify_multi_bottoms(tops_and_bottoms_data, tolerance=0.1, order=1)
    assert touches is not None
    assert support_value is not None
