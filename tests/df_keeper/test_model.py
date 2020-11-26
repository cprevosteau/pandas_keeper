import pytest
from pandas_keeper.df_keeper.model import Model
from pydantic import ValidationError


def test_model_init_should_fail_when_exrat_args():
    # Given
    class TestModel(Model):
        name: str

    # When/ Then
    with pytest.raises(ValidationError):
        TestModel(naùe="test", size=2)
